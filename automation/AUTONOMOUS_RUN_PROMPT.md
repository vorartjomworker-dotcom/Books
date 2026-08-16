# Autonomous run contract

Use `$ml4t-autonomous-translation` to operate the configured active ML4T batch.

Read `AGENTS.md`, `automation/pipeline_config.json`, `automation/state.json`, and `config/registry_expectations.json` before writing. Work on the configured translation branch only. Process at most one batch in this run.

For the active range, use the EPUB as the canonical English source, the PDF as the visual reference, the chapter registry as the block ledger, and the glossary/style guide as binding rules. Use independent translator, language-QA, and structural-QA roles when subagents are available. The coordinator alone may write reconciled artifacts.

Create or resume the batch CSV, issue rows, QA report, and run-state artifact at the configured paths. Run all repository tests and validators. Correct findings for at most three cycles. Stop rather than guess when a source is missing, identifiers disagree, formulas/tables/figures are ambiguous, another run owns the range, or checks still fail.

Autonomous rules are mandatory: do not modify EPUB/PDF or accepted blocks without a registered issue; do not merge to `main` while `merge_policy` is `manual`; write canonical Drive registries only through the integrator after every required gate and explicit acceptance have been recorded. Stop at `AWAITING_REVIEW` for the required human decision. After a batch is accepted and reaches `COMPLETED`, advance to the next configured `READY` range when `auto_advance` is enabled.

Finish by reporting the branch, range, state, validation results, open issues, and required human decision.
