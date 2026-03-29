# Markdown Reporting (MVP)

`act0r` generates one Markdown report file per run.

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
- output path pattern: `<output_dir>/<run_id>.md`
