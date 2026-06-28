"""Core ranking engine for the Redrob Senior AI Engineer candidate ranking challenge."""
from datetime import date
from typing import List, Dict, Any

from src.utils import load_candidates, days_since


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Honeypot / non-AI title keywords
_UNRELATED_TITLES = [
    "hr manager", "human resource", "marketing manager", "accountant",
    "content writer", "graphic designer", "business analyst", "civil engineer",
    "mechanical engineer", "operations manager", "customer support",
    "sales executive", "sales manager", "project manager",
]

# Strong AI/ML engineering titles
_TIER1_TITLES = [
    "ml engineer", "machine learning engineer", "ai engineer", "nlp engineer",
    "applied scientist", "search engineer", "retrieval engineer",
    "recommendation",
]

# Adjacent / moderate titles
_TIER075_TITLES = [
    "applied ml", "data scientist", "senior engineer",
    "software engineer", "backend engineer",
]

# Weak adjacent titles
_TIER05_TITLES = [
    "data engineer", "analytics engineer", "ml ops", "mlops",
    "platform engineer", "ai researcher",
]

# Consulting firm names (lowercase) for career penalty
_CONSULTING_FIRMS = [
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "tech mahindra", "deloitte", "ibm",
]

# Career high-signal terms (adds 0.15 each)
_HIGH_SIGNAL_CAREER = [
    "embedding", "retrieval", "ranking", "vector", "faiss", "pinecone",
    "weaviate", "qdrant", "elasticsearch", "opensearch", "sentence-transformer",
    "rag", "recommendation system", "search system", "fine-tun", "llm",
    "language model", "nlp", "information retrieval", "reranker", "rerank",
]

# Career medium-signal terms (adds 0.08 each)
_MEDIUM_SIGNAL_CAREER = [
    "pytorch", "tensorflow", "transformers", "huggingface", "bert", "gpt",
    "neural", "deep learning", "machine learning", "scikit", "xgboost",
    "a/b test", "ndcg", "mrr", "latency optimization",
]

# Skill tiers for trust scoring
_TIER1_SKILLS = {
    "sentence-transformers", "embeddings", "vector search", "faiss", "pinecone",
    "weaviate", "qdrant", "milvus", "elasticsearch", "opensearch", "rag",
    "retrieval", "information retrieval", "reranking", "learning to rank",
    "ndcg", "bm25", "hybrid search", "semantic search",
}

_TIER2_SKILLS = {
    "python", "pytorch", "tensorflow", "transformers", "hugging face",
    "huggingface", "nlp", "natural language processing", "llm",
    "large language models", "fine-tuning", "lora", "qlora", "peft",
    "xgboost", "lightgbm", "ranking", "recommendation systems", "search",
}

_TIER3_SKILLS = {
    "mlflow", "weights & biases", "wandb", "airflow", "spark", "redis",
    "kafka", "docker", "kubernetes", "sql", "nosql", "postgresql", "mongodb",
    "a/b testing", "model evaluation", "distributed systems", "scikit-learn",
    "sklearn", "deep learning", "neural networks",
}

_PROFICIENCY_WEIGHTS = {"beginner": 0.25, "intermediate": 0.5, "advanced": 0.75, "expert": 1.0}

# Normalization denominator: 5 Tier-1 expert skills @ trust ~1.0 → raw ~ 10.0
# trust for perfect skill: (1.0*0.4 + 1.0*0.35 + 1.0*0.25) = 1.0
# 5 * 2.0 * 1.0 = 10.0 → target ~0.9 (leaving headroom for assessment-score bonus)
# 10.0 / 0.9 ≈ 11.11
_SKILL_MAX_POSSIBLE = 11.11  # 5 × 2.0 × 1.0 / 0.9 ≈ 11.11 to target ~0.9 for perfect skills


# ---------------------------------------------------------------------------
# Sub-scorers
# ---------------------------------------------------------------------------

def title_career_score(candidate: dict) -> float:
    """Score based on current job title + career history AI/ML relevance."""
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])

    # --- title_score ---
    raw_title = profile.get("current_title", "").lower()
    title_score = 0.4  # default for unlisted titles

    if any(kw in raw_title for kw in _UNRELATED_TITLES):
        title_score = 0.1
    elif any(kw in raw_title for kw in _TIER1_TITLES):
        title_score = 1.0
    elif any(kw in raw_title for kw in _TIER075_TITLES):
        title_score = 0.75
    elif any(kw in raw_title for kw in _TIER05_TITLES):
        title_score = 0.5

    # --- career_score ---
    all_career_text = " ".join(
        (r.get("description", "") + " " + r.get("title", "")).lower()
        for r in career
    )

    career_raw = 0.0
    for term in _HIGH_SIGNAL_CAREER:
        if term in all_career_text:
            career_raw += 0.15
    for term in _MEDIUM_SIGNAL_CAREER:
        if term in all_career_text:
            career_raw += 0.08

    # Consulting firm penalty: if ALL companies are consulting firms, 0.5x
    if career:
        all_companies = [r.get("company", "").lower() for r in career]
        if all(
            any(firm in company for firm in _CONSULTING_FIRMS)
            for company in all_companies
        ):
            career_raw *= 0.5

    career_score = min(career_raw, 1.0)

    return (title_score * 0.5) + (career_score * 0.5)


def skill_trust_score(candidate: dict) -> float:
    """Score based on AI/ML skill quality (proficiency, endorsements, duration)."""
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    assessment_scores = signals.get("skill_assessment_scores", {}) or {}

    skill_trust_raw = 0.0

    for skill in skills:
        name_lower = skill.get("name", "").lower()

        # Determine tier weight
        if name_lower in _TIER1_SKILLS:
            tier_weight = 2.0
        elif name_lower in _TIER2_SKILLS:
            tier_weight = 1.5
        elif name_lower in _TIER3_SKILLS:
            tier_weight = 1.0
        else:
            continue  # Not a relevant skill

        proficiency_w = _PROFICIENCY_WEIGHTS.get(skill.get("proficiency", ""), 0.5)
        endorsement_w = min(skill.get("endorsements", 0) / 30.0, 1.0)
        duration_w = min(skill.get("duration_months", 0) / 18.0, 1.0)

        trust = (proficiency_w * 0.4) + (endorsement_w * 0.35) + (duration_w * 0.25)

        # Bonus for skill assessment score
        for sk_name, sk_score in assessment_scores.items():
            if sk_name.lower() == name_lower:
                trust += (sk_score / 100.0) * 0.1
                break

        skill_trust_raw += tier_weight * trust

    return min(skill_trust_raw / _SKILL_MAX_POSSIBLE, 1.0)


def behavioral_score(candidate: dict, ref_date: date) -> float:
    """Score based on platform behavioral signals."""
    signals = candidate.get("redrob_signals", {})

    recruiter_response = signals.get("recruiter_response_rate", 0.0) or 0.0
    interview_rate = signals.get("interview_completion_rate", 0.0) or 0.0
    last_active = signals.get("last_active_date", "") or ""
    github_raw = signals.get("github_activity_score", -1)
    if github_raw is None:
        github_raw = -1

    # Recency: 1.0 if active within 30 days, decay over 365 days
    days_inactive = days_since(last_active, ref_date)
    recency = max(0.0, 1.0 - (days_inactive / 365.0))

    # GitHub: treat -1 as 0
    github_norm = max(0.0, float(github_raw)) / 100.0

    score = (
        recruiter_response * 0.35
        + interview_rate * 0.30
        + recency * 0.20
        + github_norm * 0.15
    )
    return min(score, 1.0)


def experience_score(candidate: dict) -> float:
    """Score based on years of experience (target: 5–9 years)."""
    yoe = candidate.get("profile", {}).get("years_of_experience", 0) or 0.0

    if yoe < 2:
        score = yoe / 2.0 * 0.3
    elif yoe < 5:
        score = 0.3 + (yoe - 2) / 3.0 * 0.5
    elif yoe <= 9:
        score = 0.8 + (1.0 - abs(yoe - 7) / 2.0) * 0.2
    else:
        score = max(0.5, 1.0 - (yoe - 9) / 10.0)

    return min(max(score, 0.0), 1.0)


def availability_score(candidate: dict) -> float:
    """Score based on availability and location signals."""
    signals = candidate.get("redrob_signals", {})
    profile = candidate.get("profile", {})

    score = 0.0

    if signals.get("open_to_work_flag", False):
        score += 0.35

    notice = signals.get("notice_period_days", 999) or 999
    if notice <= 30:
        score += 0.30
    elif notice <= 60:
        score += 0.20
    elif notice <= 90:
        score += 0.10

    if signals.get("willing_to_relocate", False):
        score += 0.15

    country = (profile.get("country", "") or "").lower().strip()
    if country in ("india", "in"):
        score += 0.15
    else:
        score += 0.05

    completeness = (signals.get("profile_completeness_score", 50) or 50) / 100.0
    score += completeness * 0.05

    return min(score, 1.0)


def education_score(candidate: dict) -> float:
    """Score based on education tier and field of study."""
    education = candidate.get("education", [])
    tier_weights = {
        "tier_1": 1.0, "tier_2": 0.7, "tier_3": 0.45,
        "tier_4": 0.25, "unknown": 0.3,
    }

    if not education:
        return 0.3

    best_tier = max(
        tier_weights.get(edu.get("tier", "unknown"), 0.3)
        for edu in education
    )

    field_bonus = 0.0
    for edu in education:
        field = (edu.get("field_of_study", "") or "").lower()
        if any(kw in field for kw in [
            "computer science", " cs", "artificial intelligence",
            "machine learning", "data science", "nlp",
            "software", "electrical", "electronics", "information",
        ]):
            field_bonus = 0.15
            break

    return min(best_tier + field_bonus, 1.0)


def detect_honeypot(candidate: dict) -> float:
    """Return 0.05 if honeypot detected, 1.0 otherwise."""
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])
    profile = candidate.get("profile", {})

    # Check 1: Many "expert" skills with 0 endorsements AND 0 duration
    expert_stuffed = sum(
        1 for s in skills
        if s.get("proficiency") == "expert"
        and s.get("endorsements", 0) == 0
        and s.get("duration_months", 0) == 0
    )
    if expert_stuffed >= 4:
        return 0.05

    # Check 2: Claimed YOE vs career history sum — if wildly mismatched
    claimed_yoe = profile.get("years_of_experience", 0) or 0
    total_career_months = sum(r.get("duration_months", 0) or 0 for r in career)
    if claimed_yoe > 0 and total_career_months > 0:
        career_years = total_career_months / 12.0
        if claimed_yoe > career_years * 2.5 and claimed_yoe > 5:
            return 0.05

    # Check 3: Many skills but average endorsements == 0
    if len(skills) > 12:
        avg_endorsements = sum(s.get("endorsements", 0) or 0 for s in skills) / len(skills)
        if avg_endorsements == 0:
            return 0.05

    return 1.0


# ---------------------------------------------------------------------------
# Composite scorer
# ---------------------------------------------------------------------------

def score_candidate(candidate: dict, ref_date: date) -> dict:
    """Score a candidate and return a dict with all scoring components."""
    honeypot_mult = detect_honeypot(candidate)

    tc = title_career_score(candidate)
    st = skill_trust_score(candidate)
    beh = behavioral_score(candidate, ref_date)
    exp = experience_score(candidate)
    avail = availability_score(candidate)
    edu = education_score(candidate)

    final = (
        0.35 * tc
        + 0.20 * st
        + 0.20 * beh
        + 0.10 * exp
        + 0.10 * avail
        + 0.05 * edu
    ) * honeypot_mult

    return {
        "candidate_id": candidate["candidate_id"],
        "score": round(final, 4),
        "title_career": round(tc, 4),
        "skill_trust": round(st, 4),
        "behavioral": round(beh, 4),
        "experience": round(exp, 4),
        "availability": round(avail, 4),
        "education": round(edu, 4),
        "is_honeypot": honeypot_mult < 1.0,
        # Stored for reasoning generation
        "profile": {
            "current_title": candidate["profile"].get("current_title", ""),
            "years_of_experience": candidate["profile"].get("years_of_experience", 0),
            "country": candidate["profile"].get("country", ""),
        },
        "redrob_signals": {
            "recruiter_response_rate": candidate.get("redrob_signals", {}).get(
                "recruiter_response_rate", 0.0
            ),
            "open_to_work_flag": candidate.get("redrob_signals", {}).get(
                "open_to_work_flag", False
            ),
        },
    }


# ---------------------------------------------------------------------------
# Reasoning generator
# ---------------------------------------------------------------------------

def generate_reasoning(scored: dict, rank: int) -> str:
    """Build a non-templated reasoning string from scored components."""
    title = scored["profile"].get("current_title", "Unknown")
    yoe = scored["profile"].get("years_of_experience", 0)
    response_rate = scored["redrob_signals"].get("recruiter_response_rate", 0.0) or 0.0
    open_flag = scored["redrob_signals"].get("open_to_work_flag", False)

    parts = [f"{title} with {yoe:.1f} yrs"]

    if scored["title_career"] >= 0.75:
        parts.append("strong AI/ML engineering background in title and career history")
    elif scored["title_career"] >= 0.5:
        parts.append("adjacent engineering background with AI/ML exposure")
    elif scored["title_career"] < 0.3:
        parts.append("non-technical background with limited ML relevance")

    if scored["skill_trust"] > 0.6:
        parts.append("strong AI/retrieval skill stack with endorsements")
    elif scored["skill_trust"] > 0.3:
        parts.append("relevant AI skills")
    else:
        parts.append("limited AI/ML skills")

    if response_rate > 0.6:
        parts.append(f"high recruiter engagement ({response_rate:.0%})")
    elif response_rate < 0.2:
        parts.append(f"low response rate ({response_rate:.0%}) reduces availability signal")

    if open_flag:
        parts.append("actively seeking")

    exp_score = scored.get("experience", 0)
    if exp_score >= 0.9:
        parts.append("ideal experience range 5-9 yrs")
    elif exp_score < 0.5:
        parts.append("experience outside preferred range")

    if scored["is_honeypot"]:
        parts.append("FLAGGED: suspicious profile pattern (keyword stuffing detected)")

    if rank <= 10:
        parts.append("top-10 caliber fit")

    return "; ".join(parts) + "."


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _finalize_rankings(scored_list: list, top_n: int) -> list:
    """Sort, slice to top_n, and attach rank + reasoning."""
    scored_list.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    results = []
    for rank_idx, item in enumerate(scored_list[:top_n], start=1):
        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank_idx,
            "score": item["score"],
            "reasoning": generate_reasoning(item, rank_idx),
        })
    return results


# ---------------------------------------------------------------------------
# Public ranking functions
# ---------------------------------------------------------------------------

def rank_candidates(candidates_path: str, top_n: int = 100) -> List[dict]:
    """
    Stream-process all candidates from a JSONL file, score each, return top_n with reasoning.
    ref_date is hardcoded to 2026-06-28 (challenge date).
    """
    ref_date = date(2026, 6, 28)

    all_scores = []
    for candidate in load_candidates(candidates_path):
        scored = score_candidate(candidate, ref_date)
        all_scores.append(scored)

    return _finalize_rankings(all_scores, top_n)


def rank_candidates_list(candidates: List[dict], top_n: int = 100) -> List[dict]:
    """
    Score candidates from a Python list (for Streamlit demo).
    Same logic as rank_candidates but accepts a list instead of a file path.
    ref_date is hardcoded to 2026-06-28 (challenge date).
    """
    ref_date = date(2026, 6, 28)

    all_scores = []
    for candidate in candidates:
        scored = score_candidate(candidate, ref_date)
        all_scores.append(scored)

    return _finalize_rankings(all_scores, top_n)
