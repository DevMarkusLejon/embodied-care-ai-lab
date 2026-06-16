# Research Log

This log tracks concrete benchmark and prototype milestones. It is intentionally concise so the repository shows technical progress without turning into a manifesto.

## 2026-06-16

- Created the initial Python package, CLI, schemas, mock adapters, evaluator, reports, tests, and CI.
- Added synthetic Swedish and English women's health benchmark prompts.
- Added explicit ethical scope documentation: no medical advice, no diagnosis, no real patient data, and no clinical validation claims.
- Added a minimal OpenAI-compatible adapter path using environment variables and chat-completions style APIs.
- Expanded scoring so prompt-level `expected_behaviors` map to concrete rule checks.

## Near-Term Evaluation Questions

- Which failure modes are common across languages?
- Do models escalate urgent symptoms reliably without overdiagnosing?
- Do models handle sex-specific context without dismissing symptoms or giving generic reassurance?
- Which checks are too easy to satisfy with superficial boilerplate?
- Where should expert-reviewed rubrics replace keyword heuristics?
