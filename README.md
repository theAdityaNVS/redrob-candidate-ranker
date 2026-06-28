# Redrob Intelligent Candidate Discovery — India Runs Hackathon | Team: Tech Adi

## Overview

This system ranks 100,000 candidate profiles against a Senior AI Engineer job description,
producing a top-100 leaderboard that resists keyword-stuffing attacks.

Most naive rankers fail on two traps the dataset deliberately plants:
1. **Keyword stuffers** — HR Managers who list "PyTorch, FAISS, RAG" in their skills section
   but have zero months of actual usage and zero endorsements.
2. **Dormant profiles** — Strong engineers who stopped engaging on the platform years ago.

Our engine neutralizes both by scoring **skill trust** (proficiency × endorsements × duration)
rather than raw skill count, and by weighting **behavioral signals** heavily.

---

## Architecture

```
Job Description (Senior AI Engineer)
          │
          ▼
  ┌───────────────────┐
  │   Ranking Engine  │   src/engine.py
  │                   │
  │  title_career     │  35% — current title + career history AI/ML depth
  │  skill_trust      │  20% — proficiency × endorsements × duration_months
  │  behavioral       │  20% — recruiter response, interview rate, recency, GitHub
  │  experience_fit   │  10% — 5–9 yr sweet spot scoring curve
  │  availability     │  10% — open_to_work, notice period, relocation, country
  │  education        │   5% — institution tier + relevant field of study
  │                   │
  │  honeypot_mult    │   ×0.05 if keyword-stuffing patterns detected
  └───────────────────┘
          │
          ▼
    Composite Score (0–1)
          │
          ▼
      Top 100 Ranked
      submission.csv / submission.xlsx
```

---

## Scoring Components

| Component | Weight | What It Measures | Anti-Trap Role |
|-----------|--------|-----------------|----------------|
| **Title + Career** | 35% | Current role title tier; AI/ML keywords in past job descriptions | HR Managers with AI skills still score 0.1 on title; career text reveals real depth |
| **Skill Trust** | 20% | `proficiency × (endorsements/30) × (duration_months/18)` per skill | Zero-endorsement bulk skills contribute near-zero even if listed as "expert" |
| **Behavioral** | 20% | Recruiter response rate, interview completion, last-active recency, GitHub activity | Dormant profiles penalized via recency decay over 365 days |
| **Experience Fit** | 10% | Years of experience on a bell curve targeting 5–9 years | Prevents both freshers and overqualified candidates from dominating |
| **Availability** | 10% | open_to_work flag, notice period ≤30d, willing_to_relocate, India location | Prefers candidates who can join quickly |
| **Education** | 5% | Institution tier (tier_1 through tier_4) + relevant field of study | Modest signal; avoids over-penalizing self-taught engineers |

---

## Honeypot Detection

Three pattern-based checks penalize suspicious profiles by multiplying their final score by 0.05:

1. **Expert-stuffed skills** — 4 or more skills listed as "expert" with 0 endorsements AND
   0 duration months. This pattern is physically impossible: no recruiter endorsed them, and
   they claim no time spent on the skill.

2. **YOE vs career history mismatch** — Claimed years_of_experience > 2.5× the sum of all
   career role durations, and claimed YOE > 5. Indicates fabricated experience claims.

3. **Zero-endorsement bulk skills** — More than 12 skills listed with an average endorsement
   count of exactly 0. Genuine senior engineers accumulate at least some endorsements on
   their core skills over a long career.

---

## Setup

```bash
pip install -r requirements.txt
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
python resources/validate_submission.py submission.csv
```

### Reproduce Command

```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

Runtime: ~30 seconds for 100K candidates on CPU. No GPU or network required.

### Validate Output

```bash
python resources/validate_submission.py submission.csv
```

Expected output: validation passes with 100 rows, ranks 1–100, non-increasing scores.

---

## Sandbox Demo

Live demo (Streamlit): [https://adimyth-redrob-ranker.streamlit.app](https://adimyth-redrob-ranker.streamlit.app)

Upload your own `candidates.jsonl` or paste a candidate JSON to see scores broken down
by component in real time.

---

## File Layout

```
.
├── rank.py                        # Entry point: generates submission.csv + .xlsx
├── app.py                         # Streamlit demo app
├── requirements.txt
├── submission_metadata.yaml
├── README.md
├── src/
│   ├── __init__.py
│   ├── engine.py                  # Core scoring logic (all 6 components + honeypot)
│   └── utils.py                   # JSONL loader, date helpers
└── resources/
    ├── candidates.jsonl           # 100K candidate profiles (not committed)
    ├── candidate_schema.json      # Schema reference
    ├── validate_submission.py     # Official validator
    └── sample_submission.csv      # Reference format
```

---

## Key Design Decisions

- **No LLM calls during inference** — fully offline, deterministic, reproducible.
- **Streaming JSONL load** — reads candidates one at a time; constant memory regardless
  of dataset size.
- **Trust-weighted skills over count** — a candidate with 3 endorsed expert skills beats
  one with 20 unverified listings every time.
- **Consulting firm penalty** — candidates whose entire career is at large service
  integrators (TCS, Infosys, Wipro, etc.) receive a 0.5× career score multiplier,
  reflecting typical lack of deep product AI work.
- **CSV formula injection protection** — cells starting with `=`, `+`, `-`, `@` are
  prefixed with a single quote before writing.

---

## Submission Checklist

- [x] `submission.csv` — 100 rows, columns: `candidate_id,rank,score,reasoning`
- [x] `submission.xlsx` — same data, Excel format
- [x] Validator passes (`python resources/validate_submission.py submission.csv`)
- [x] Runtime ≤ 5 minutes on CPU, 16 GB RAM, no network
- [x] GitHub repo public with complete source
- [x] `submission_metadata.yaml` filled out
- [x] Presentation PDF prepared from Redrob template
