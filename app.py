"""Streamlit sandbox demo for the Redrob candidate ranking engine."""
import streamlit as st
import json
import csv
import io
from datetime import date

st.set_page_config(
    page_title="Redrob Candidate Ranker — Tech Adi",
    page_icon="🎯",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.title("🎯 Redrob Ranker")
    st.caption("India Runs Hackathon — Tech Adi")
    st.divider()
    st.subheader("How it works")
    st.markdown("""
**Anti-honeypot design:**

The dataset contains ~80 honeypot profiles: HR Managers and Marketing Managers with many AI keywords listed as skills. Naive keyword-matching ranks these high.

Our engine ranks by:
1. **Title + Career (35%)** — Actual ML/AI job titles and descriptions in career history
2. **Skill trust (20%)** — Skills weighted by endorsements × proficiency × duration (catches stuffing)
3. **Behavioral (20%)** — Recruiter response rate, interview completion, platform recency
4. **Experience (10%)** — 5–9 year target range for this JD
5. **Availability (10%)** — Notice period, open-to-work flag, willingness to relocate
6. **Education (5%)** — Institution tier + CS/AI field bonus

**Honeypot detection:** profiles with many "expert" skills at 0 endorsements + 0 months duration are flagged and scored ×0.05.
    """)

st.title("🎯 Intelligent Candidate Ranker")
st.caption("Senior AI Engineer — Redrob AI | Hackathon submission by Tech Adi")

st.info(
    "Upload a JSON array or JSONL file of candidate profiles (max 100). "
    "The ranker will score and rank them against the Senior AI Engineer JD.",
    icon="ℹ️"
)

uploaded = st.file_uploader(
    "Upload candidates (JSON array or JSONL, max 100 candidates)",
    type=["json", "jsonl"],
    help="Must match the Redrob candidate schema."
)

if uploaded:
    # Parse file
    content = uploaded.read().decode("utf-8")
    try:
        if uploaded.name.endswith(".jsonl"):
            candidates = [json.loads(line) for line in content.strip().splitlines() if line.strip()]
        else:
            candidates = json.loads(content)
            if isinstance(candidates, dict):
                candidates = [candidates]
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"Could not parse file: {e}")
        st.stop()

    if len(candidates) > 100:
        st.warning(f"Found {len(candidates)} candidates — using first 100.")
        candidates = candidates[:100]

    st.success(f"Loaded {len(candidates)} candidate profiles.")

    if st.button("🚀 Run Ranker", type="primary"):
        from src.engine import rank_candidates_list, score_candidate

        ref_date = date(2026, 6, 28)

        with st.spinner("Scoring candidates..."):
            # Get rankings
            ranked = rank_candidates_list(candidates, top_n=len(candidates))

            # Get score breakdowns
            breakdown_map = {}
            for c in candidates:
                scored = score_candidate(c, ref_date)
                breakdown_map[c["candidate_id"]] = scored

        # Build display table
        rows = []
        for r in ranked:
            cid = r["candidate_id"]
            bd = breakdown_map.get(cid, {})
            profile = bd.get("profile", {})
            rows.append({
                "Rank": r["rank"],
                "Candidate ID": cid,
                "Score": f"{r['score']:.4f}",
                "Title": profile.get("current_title", "—"),
                "Exp (yrs)": profile.get("years_of_experience", "—"),
                "Title+Career": f"{bd.get('title_career', 0):.2f}",
                "Skill Trust": f"{bd.get('skill_trust', 0):.2f}",
                "Behavioral": f"{bd.get('behavioral', 0):.2f}",
                "🚨 Honeypot": "⚠️ YES" if bd.get("is_honeypot") else "✅ No",
                "Reasoning": r["reasoning"],
            })

        import pandas as pd
        df = pd.DataFrame(rows)

        st.subheader(f"Top {len(rows)} Candidates")

        # Highlight honeypots
        def highlight_honeypot(row):
            if row["🚨 Honeypot"] == "⚠️ YES":
                return ["background-color: #3d1f1f"] * len(row)
            elif int(row["Rank"]) <= 10:
                return ["background-color: #1a2d1a"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df.style.apply(highlight_honeypot, axis=1),
            use_container_width=True,
            height=600,
        )

        # Metrics
        col1, col2, col3 = st.columns(3)
        honeypots = sum(1 for r in rows if r["🚨 Honeypot"] == "⚠️ YES")
        with col1:
            st.metric("Candidates Ranked", len(rows))
        with col2:
            st.metric("Honeypots Detected", honeypots)
        with col3:
            top_score = float(rows[0]["Score"]) if rows else 0
            st.metric("Top Score", f"{top_score:.4f}")

        # CSV download
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in ranked:
            writer.writerow([r["candidate_id"], r["rank"], r["score"], r["reasoning"]])

        st.download_button(
            "⬇️ Download Submission CSV",
            data=csv_buf.getvalue(),
            file_name="submission.csv",
            mime="text/csv",
        )
else:
    st.markdown("""
### Sample usage
1. Upload a JSON file with up to 100 candidate profiles
2. Click **Run Ranker**
3. Inspect the ranked table and score breakdowns
4. Download the submission CSV

The candidate file must match the [Redrob candidate schema](https://github.com/adimyth/redrob-candidate-ranker).
    """)
