<!--
  infra/terraform/bootstrap/README.md — created by `engineering-automation scaffold
  create-project`. This root provisions the CI/CD OIDC roles the main stack's own CI/CD
  pipeline (.github/workflows/ci.yml) assumes -- it is applied once, by a human admin
  with their own AWS credentials, not by CI.
-->

# payroll_pipeline_2026_09_17 -- CI/CD bootstrap

This Terraform root provisions three IAM roles GitHub Actions assumes via OIDC (no
long-lived AWS keys are ever stored in the repo): a read-only `plan` role, a `deploy`
role scoped to the `dev` GitHub Environment, and a
`scripts` role that only uploads to the scripts bucket. It keeps its own Terraform
state, separate from the main stack's -- the `deploy` role it creates is what applies
the main stack, so it must never be created by the stack it applies.

## One-time setup

1. Fill in the real GitHub `<owner>/<repo>` before applying -- the rendered
   `github_owner_repo` default is a placeholder and every role's trust policy is
   meaningless without it.
2. Apply as an admin, with your own AWS credentials:

   ```bash
   cd infra/terraform/bootstrap
   terraform init
   terraform apply -var="github_owner_repo=<owner>/<repo>"
   ```
3. Copy the three ARNs from `terraform output` into the repo's Actions secrets:

   | Terraform output | GitHub secret |
   | --- | --- |
   | `plan_role_arn` | `AWS_PLAN_ROLE_ARN` |
   | `deploy_role_arn` | `AWS_DEPLOY_ROLE_ARN` |
   | `scripts_role_arn` | `AWS_SCRIPTS_ROLE_ARN` |

4. Create a GitHub **`dev` Environment** on the repo
   with a *Required reviewers* rule. This -- not the Terraform trust policy alone -- is
   what actually pauses `terraform apply` for human approval; the trust policy only
   ensures the `deploy` role can't be assumed by a job that isn't bound to this
   Environment.

## Re-applying

Only needed when a role's permissions or trust conditions change (e.g. renaming the
repo, adding a new managed resource type to the main stack). Routine deploys never
touch this root.
