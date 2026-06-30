# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Challenge Overview

**India Runs — Data & AI Challenge: Intelligent Candidate Discovery** (Redrob)
- **Deadline**: 02/07/2026 11:59 PM IST
- **Goal**: Build a predictive ranking engine that semantically ranks candidates against a job description
- **Output**: Top 100 candidates ranked by score, submitted as `.csv` (portal also accepts `.xlsx`)

## Dataset

`resources/candidates.jsonl` — 100,000 candidate profiles (JSONL, one object per line)

Each candidate has these top-level keys (schema in `resources/candidate_schema.json`):
- `candidate_id` — format `CAND_XXXXXXX`
- `profile` — headline, summary, location, years_of_experience, current_title, current_company, etc.
- `career_history` — array of past roles with descriptions
- `skills` — name, proficiency (`beginner/intermediate/advanced/expert`), endorsements, duration_months
- `education` — institution, degree, field_of_study, tier (`tier_1` through `tier_4`)
- `certifications`, `languages`
- `redrob_signals` — platform behavioral signals: profile_completeness_score, open_to_work_flag, recruiter_response_rate, interview_completion_rate, offer_acceptance_rate, github_activity_score, skill_assessment_scores, notice_period_days, expected_salary_range_inr_lpa, etc.

## Submission Format

The submission CSV must pass `resources/validate_submission.py`. Rules enforced:
- Exactly 100 data rows (ranks 1–100, each appearing exactly once)
- Columns in exact order: `candidate_id,rank,score,reasoning`
- Scores must be non-increasing by rank; ties broken by `candidate_id` ascending
- `candidate_id` must match `CAND_XXXXXXX` pattern, no duplicates

Validate before submitting:
```bash
python resources/validate_submission.py <your_submission>.csv
```

## Repository Layout (to build)

```
src/
  engine.py       # Core ranking logic
  utils.py        # Data loading, preprocessing helpers
data/             # Symlink or copy of resources/candidates.jsonl
notebooks/        # Exploratory analysis
rank.py           # Entry point: python rank.py --candidates ./candidates.jsonl --out ./submission.csv
requirements.txt
submission_metadata.yaml   # Fill from resources/submission_metadata_template.yaml
```

## Submission Metadata

Fill out `submission_metadata.yaml` (from `resources/submission_metadata_template.yaml`) with:
- `reproduce_command`: must run end-to-end in ≤5 min on CPU, 16GB RAM, **no network**
- `sandbox_link`: hosted demo (HuggingFace Spaces, Streamlit Cloud, etc.)
- `uses_gpu_for_inference: false` and `has_network_during_ranking: false` are hard requirements

## Three Deliverables

1. **GitHub repo** (public) — organized source code + README
2. **Presentation PDF** — use template at `resources/Idea Submission Template _ Redrob.pptx`, must match Team ID
3. **Ranked output** — `.xlsx` or `.csv`, ≤5 MB, top 100 candidates

## Scoring Signals to Consider

From the schema and `sample_submission.csv` reasoning patterns:
- **AI/ML skill count** — number of core AI skills matched against the JD
- **Years of experience** relative to JD requirements
- **Recruiter response rate** — behavioral engagement signal
- **Skill proficiency levels** and endorsement counts
- `open_to_work_flag`, `notice_period_days`, `willing_to_relocate`
- `github_activity_score` (0–100, -1 if no GitHub)
- `interview_completion_rate`, `offer_acceptance_rate`
- Education institution tier for roles requiring strong academic background

## Key Constraints

- No API calls during ranking (offline inference only)
- CPU-only inference required; GPU not permitted
- Dataset is 100K profiles — batch efficiently; avoid loading all embeddings into RAM at once if using transformers
- No hardcoded absolute paths in production scripts
