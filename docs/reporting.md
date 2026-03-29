# Reporting And Exports

`act0r` generates deterministic operator artifacts per run.

Primary outputs:

- Markdown report: `<output_dir>/<run_id>.md`
- JSON export: `<output_dir>/<run_id>.json`
- PDF export: `<output_dir>/<run_id>.pdf`
- Shareable bundle: `<output_dir>/<run_id>.bundle.zip`

## Required sections

- Run metadata
- Scenario summary
- Expected safe behavior
- Observed behavior
- Tool calls
- Violations
- Evaluation scores
- Final assessment
- Recommendations

## Output behavior

- deterministic section order
- concise tables/lists for operator readability
- deterministic ZIP entry ordering for bundles
- local-only generation (no remote conversion services)
