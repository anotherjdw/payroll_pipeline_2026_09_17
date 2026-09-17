<!--
  README.md — created by `engineering-automation scaffold create-project`.

  Sections wrapped in AUTO:BEGIN / AUTO:END markers are owned by the generator and
  will be overwritten when documentation rendering lands. Do not hand-edit inside a
  marker pair, and do not remove the markers. Everything outside them is yours.

  Anything you write here that a transformation needs in order to be *correct* is in
  the wrong file. Dataset semantics belong in the data contract; business logic
  belongs in the job spec. This file is for the operational context that has no other
  home.

  Replace every TODO before this repository is reviewed.
-->

# payroll_pipeline_2026_09_17

> TODO: One sentence. What this data product is, and who depends on it.

## What this pipeline produces

TODO: The datasets this repository owns, and the decision or downstream system each one
serves. Name the consumers. If a dataset has no consumer, say so explicitly — that is
worth knowing.

## Ownership

| | |
| --- | --- |
| Data product | `payroll_pipeline_2026_09_17` |
| Owning team | TODO |
| Primary contact | TODO |
| Escalation channel | TODO |

## Upstream dependencies

TODO: The systems this pipeline reads from and who owns each one. Record refresh cadence,
expected arrival time, and the upstream contact in that source's data contract under
`src/payroll_pipeline_2026_09_17/contracts/` — not here. This section is for the dependencies that
are political rather than technical: who to talk to, and what breaks when they change
something.

## Service expectations

TODO: When must the output be ready, and what happens downstream if it is late? State the
freshness commitment you are actually making, not the one you hope for. If there is no
commitment, write "none" — an honest "none" is more useful than an aspirational SLA.

## Operations

TODO: The runbook. Where do logs go? How do you re-run a single failed window? What is the
backfill procedure, and who has to be told before you start one? What are the known
failure modes and their first diagnostic step?

<!-- AUTO:BEGIN jobs -->
## Jobs

_No ETL jobs are defined yet._

Define one with:

```bash
engineering-automation scaffold create-job-settings . <etl_job>
```

then fill in the generated `src/payroll_pipeline_2026_09_17/jobs/<etl_job>/<etl_job>.yaml` and its
data contract, and run `engineering-automation generate create-job`.
<!-- AUTO:END jobs -->

<!-- AUTO:BEGIN lineage -->
## Lineage

_Rendered from the job specs once at least one job exists._
<!-- AUTO:END lineage -->

<!-- AUTO:BEGIN contracts -->
## Data contracts

_Rendered from `src/payroll_pipeline_2026_09_17/contracts/` once at least one contract exists._
<!-- AUTO:END contracts -->

<!-- AUTO:BEGIN quickstart -->
## Getting started

```bash
make install          # pip install -e ".[dev]"
make test             # full suite
make check            # lint + typecheck + test
```

Individual test tiers: `make test-unit`, `make test-integration`, `make test-e2e`.

Copy `.env.example` to `.env` and fill in the values before running anything that touches
AWS.
<!-- AUTO:END quickstart -->

<!-- AUTO:BEGIN deployment -->
## Deployment

CI (`.github/workflows/ci.yml`) plans on every push and pull request, and applies +
deploys on push to the default branch, gated behind manual approval. Two one-time,
manual prerequisites before the first deploy can succeed:

1. **Bootstrap the CI/CD IAM roles.** `infra/terraform/bootstrap/` provisions the three
   roles CI assumes via OIDC. An admin applies it once (see
   `infra/terraform/bootstrap/README.md`) and copies its three outputs into the repo's
   Actions secrets: `AWS_PLAN_ROLE_ARN`, `AWS_DEPLOY_ROLE_ARN`, `AWS_SCRIPTS_ROLE_ARN`.
2. **Create the GitHub `dev` Environment**, with a *Required reviewers*
   rule. This is what actually pauses `terraform apply` for human approval -- the
   bootstrap role's trust policy only ensures it can't be assumed outside this
   Environment.
<!-- AUTO:END deployment -->

<!-- AUTO:BEGIN layout -->
## Repository layout

```
src/payroll_pipeline_2026_09_17/
├── contracts/          # data contracts — one YAML per dataset (dataset semantics)
├── jobs/               # one subdirectory per ETL job (job spec + generated code)
├── pipeline/           # shared read() / write() used by every job
├── runtime/            # per-run lifecycle: window resolution, SparkSession, run record
└── tests/              # unit / integration / end_to_end
infra/terraform/        # S3, Glue, and IAM for this data product
infra/terraform/bootstrap/  # CI/CD OIDC roles -- applied once, separately, by an admin
```
<!-- AUTO:END layout -->

<!-- AUTO:BEGIN changing -->
## How to change things

| To change | Edit | Then run |
| --- | --- | --- |
| What a column means | the data contract in `contracts/` | `generate codegen` |
| What a transformation does | `description` in the job spec | `generate codegen` |
| Which datasets a job reads or writes | `sources` / `sink` in the job spec | `generate create-job` |
| Infrastructure | `infra/terraform/` | `make plan` |

Generated transformation bodies are the one place where hand-editing is expected and
supported: `generate codegen` only fills functions that are still unimplemented, so a
function you have edited is left alone on re-run.
<!-- AUTO:END changing -->
