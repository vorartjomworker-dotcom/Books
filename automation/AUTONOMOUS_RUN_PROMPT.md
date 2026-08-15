# Autonomous run contract

Use `$ml4t-autonomous-translation` to operate the next or active ML4T batch.

Read `AGENTS.md`, `automation/pipeline_config.json`, `automation/state.json`, and `config/registry_expectations.json` before writing. Work on the configured translation branch only. Process at most one batch in this run.

For the active range, use the EPUB as the canonical English source, the PDF as the visual reference, the chapter registry as the block ledger, and the glossary/style guide as binding rules. Use independent translator, language-QA, and structural-QA roles when subagents are available. The coordinator alone may write reconciled artifacts.

Create or resume the batch CSV, issue rows, QA report, and run-state artifact at the configured paths. Run all repository tests and validators. Correct findings for at most three cycles. Stop rather than guess when a source is missing, identifiers disagree, formulas/tables/figures are ambiguous, another run owns the range, or checks still fail.

Pilot rules are mandatory: do not write canonical Drive registries, do not modify EPUB/PDF, do not change accepted blocks, do not merge to `main`, and do not start the next range after reaching `AWAITING_REVIEW`. Finish by reporting the branch, range, state, validation results, open issues, and required human decision.
