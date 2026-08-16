# Parallel autonomous run contract

Use `$ml4t-autonomous-translation` for exactly one configured chapter slot from `automation/state.json.active_by_chapter`.

Before writing, read `AGENTS.md`, `automation/pipeline_config.json`, `automation/state.json`, `automation/AUTONOMOUS_RUN_PROMPT.md`, and `config/registry_expectations.json` from `main`, then read the same control state from the target translation branch. Confirm chapter, exact range, branch, registry version/count, and that the chapter-scoped lock is absent or expired.

A single run processes or resumes at most one batch for one chapter. Up to five separate chapter runs may execute concurrently because CH05, CH06, CH07, CH08, and CH09 have independent slots, branches, files, and locks. Never process two ranges from the same chapter concurrently.

Use EPUB as canonical English text, PDF as visual reference, the canonical chapter registry as ledger, and glossary/style guide as mandatory rules. Use independent translator, language_qa, and structural_qa roles; only integrator writes reconciled artifacts. Run every gate, validator, unit test, and CI check, allowing at most three correction cycles.

There is no intermediate human approval between clean batches. When a batch reaches `AWAITING_REVIEW` with all gates passing and zero open critical/high issues, integrator records it as internally completed for autonomous progression, prepares the next non-overlapping range for the same chapter, and continues on a new chapter-specific translation branch in the next run. Do not merge translation results into `main`, and do not write the canonical Google Drive registry during intermediate progression.

Stop and release only the affected chapter lock when an unresolved critical/source/registry/formula/table/figure conflict remains, retry limit is exhausted, or the whole chapter is ready for one final human review. A stopped chapter must not block the other four chapter slots.

Finish each run by reporting the chapter, branch, range, state, checks, open issues, and whether the next range was scheduled.
