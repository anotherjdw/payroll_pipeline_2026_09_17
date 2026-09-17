from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def create_unique_key(payroll_register: DataFrame) -> DataFrame:
    """Creates an MD5 hashed unique key from employee_id, pay_run_id, and lohnart_code.

    Args:
        payroll_register: DataFrame containing payroll register records with employee,
            pay run, and wage type information.

    Returns:
        DataFrame with the original schema plus a payroll_register_key column containing
        an MD5 hash of the concatenated employee_id, pay_run_id, and lohnart_code fields,
        intended for use in deduplication.
    """
    return payroll_register.withColumn(
        "payroll_register_key",
        F.md5(F.concat(F.col("employee_id"), F.col("pay_run_id"), F.col("lohnart_code"))),
    ).select(
        "employee_id",
        "pay_run_id",
        "pay_period",
        "pay_date",
        "run_type",
        "lohnart_code",
        "component_name",
        "gl_account",
        "cost_center_code",
        "location_code",
        "bearer",
        "amount_eur",
        "assessment_base_eur",
        "quantity",
        "rate",
    )


def cast_data_types(create_unique_key_result: DataFrame) -> DataFrame:
    """Cast specific columns to their target data types.

    Casts gl_account and lohnart_code to integer type and pay_date to date type,
    while preserving all other columns and their existing types.

    Args:
        create_unique_key_result: Input DataFrame containing employee payroll data
            with string representations of gl_account, lohnart_code, and pay_date.

    Returns:
        DataFrame with the same schema where gl_account and lohnart_code are cast
        to integer and pay_date is cast to date type.
    """
    return (
        create_unique_key_result.withColumn("gl_account", F.col("gl_account").cast("integer"))
        .withColumn("lohnart_code", F.col("lohnart_code").cast("integer"))
        .withColumn("pay_date", F.col("pay_date").cast("date"))
        .select(
            F.col("employee_id"),
            F.col("pay_run_id"),
            F.col("pay_period"),
            F.col("pay_date"),
            F.col("run_type"),
            F.col("lohnart_code"),
            F.col("component_name"),
            F.col("gl_account"),
            F.col("cost_center_code"),
            F.col("location_code"),
            F.col("bearer"),
            F.col("amount_eur"),
            F.col("assessment_base_eur"),
            F.col("quantity"),
            F.col("rate"),
        )
    )


def filter_retro_runs(cast_data_types_result: DataFrame) -> DataFrame:
    """Filter rows to retain only retro pay runs.

    Args:
        cast_data_types_result: DataFrame containing payroll data with a run_type column.

    Returns:
        DataFrame containing only rows where run_type equals 'retro'.
    """
    return cast_data_types_result.filter(F.col("run_type") == "retro")


def filter_regular_runs(cast_data_types_result: DataFrame) -> DataFrame:
    """Filter payroll register rows to only include regular pay runs.

    Args:
        cast_data_types_result: DataFrame containing deduplicated payroll register
            data with typed columns including run_type.

    Returns:
        DataFrame containing only rows where run_type equals 'regular', with
        the same schema as the input.
    """
    return cast_data_types_result.filter(F.col("run_type") == "regular")


def sum_retro_amounts(filter_retro_runs_result: DataFrame) -> DataFrame:
    """Sum retro amounts grouped by employee, pay period, and lohnart code.

    Args:
        filter_retro_runs_result: DataFrame containing retro run records with
            employee, pay period, lohnart code, and amount columns.

    Returns:
        DataFrame with employee_id, pay_period, lohnart_code, and the summed
        retro_amount per group, with lohnart_code cast to integer.
    """
    return (
        filter_retro_runs_result.groupBy("employee_id", "pay_period", "lohnart_code")
        .agg(F.sum("amount_eur").cast("decimal(14,2)").alias("retro_amount"))
        .select(
            F.col("employee_id"),
            F.col("pay_period"),
            F.col("lohnart_code").cast("integer").alias("lohnart_code"),
            F.col("retro_amount"),
        )
    )


def join_regular_and_retro_data(
    filter_regular_runs_result: DataFrame, sum_retro_amounts_result: DataFrame
) -> DataFrame:
    """Join regular pay data with aggregated retro pay amounts.

    Performs a left join from the filtered regular pay DataFrame to the summed
    retro amounts DataFrame on employee_id, pay_period, and lohnart_code,
    adding the retro_amount column to the regular pay records.

    Args:
        filter_regular_runs_result: DataFrame containing filtered regular pay
            run records with employee, period, and compensation details.
        sum_retro_amounts_result: DataFrame containing summed retro amounts
            grouped by employee_id, pay_period, and lohnart_code.

    Returns:
        DataFrame with all columns from filter_regular_runs_result plus the
        retro_amount column from sum_retro_amounts_result, joined on
        employee_id, pay_period, and lohnart_code.
    """
    retro_prepared = (
        sum_retro_amounts_result.withColumn(
            "lohnart_code_str", F.col("lohnart_code").cast("string")
        )
        .drop("lohnart_code")
        .withColumnRenamed("lohnart_code_str", "lohnart_code")
    )
    joined = filter_regular_runs_result.join(
        retro_prepared, on=["employee_id", "pay_period", "lohnart_code"], how="left"
    )
    return joined.select(
        F.col("employee_id"),
        F.col("pay_run_id"),
        F.col("pay_period"),
        F.col("pay_date"),
        F.col("run_type"),
        F.col("lohnart_code"),
        F.col("component_name"),
        F.col("gl_account"),
        F.col("cost_center_code"),
        F.col("location_code"),
        F.col("bearer"),
        F.col("amount_eur"),
        F.col("assessment_base_eur"),
        F.col("quantity"),
        F.col("rate"),
        F.col("retro_amount"),
    )


def combine_regular_and_retro_pay(join_regular_and_retro_data_result: DataFrame) -> DataFrame:
    """Combines regular pay amounts with retro pay amounts into a single amount column.

    Adds the retro_amount to amount_eur for each row, treating null retro_amount
    values as zero, then drops the retro_amount column from the result.

    Args:
        join_regular_and_retro_data_result: DataFrame containing regular pay data
            joined with retro pay data, including both amount_eur and retro_amount columns.

    Returns:
        DataFrame with the same schema as the input minus the retro_amount column,
        where amount_eur reflects the sum of regular and retro pay amounts.
    """
    return join_regular_and_retro_data_result.withColumn(
        "amount_eur",
        F.col("amount_eur") + F.coalesce(F.col("retro_amount"), F.lit(0).cast("decimal(14,2)")),
    ).drop("retro_amount")
