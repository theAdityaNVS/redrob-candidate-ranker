You are an expert AI Engineer and Data Scientist. Your task is to completely build, evaluate, and prepare the submission deliverables for the "India Runs — Data & AI Challenge: Intelligent Candidate Discovery" based on the rules specified in the local `CHALLENGE.md` file.

### 📌 Current Context & Workspace
- **Challenge Guidelines:** Saved locally in `CHALLENGE.md`.
- **Presentation Template Directory:** `Coding\Hackathons\India_runs_data_and_ai_challenge\resources`
- **Objective:** Build an "AI Brain for Modern Hiring"—a predictive ranking engine that moves beyond simple keyword matching to perform deep semantic, contextual, and behavioral ranking of candidates against job descriptions.

---

### 🛠️ Step-by-Step Execution Plan

Please execute the following steps sequentially, verifying correctness at each stage:

#### Step 1: Data Discovery & Analysis
1. Locate the hackathon datasets in the workspace (or ask me for the path if not immediately visible).
2. Analyze the dataset schemas: identify job description fields, candidate profile attributes (skills, experience, education), and behavioral/activity signals.
3. Write a brief data profiling script to check for missing values, data distributions, and signal strengths.

#### Step 2: Core Ranking Engine Architecture & Development
1. **Semantic Matching:** Implement a contextual similarity engine using advanced embeddings (e.g., HuggingFace `sentence-transformers`, OpenAI embeddings, or cross-encoders) to compare job descriptions against candidate profiles.
2. **Signal Fusion:** Design a scoring algorithm that fuses the semantic text match score with structured metadata features (years of experience, role relevance) and behavioral/activity signals.
3. **Implementation:** Write clean, modular Python code (e.g., `src/engine.py`, `src/utils.py`) to handle data preprocessing, feature engineering, and final scoring.

#### Step 3: Generate the Required Deliverables
1. **Candidate Recommendation File (`.xlsx`):** - Run the ranking engine across the entire evaluation test set.
   - Generate the final ranked output tracking your recommended candidates.
   - Save this output exactly as an Excel file (`.xlsx`) conforming to the challenge requirements, keeping the file size under 5 MB.
2. **Code Repository Preparation:**
   - Organize the repository professionally (`data/`, `src/`, `notebooks/`, `requirements.txt`).
   - Create a thorough `README.md` that explains the system architecture, the ranking methodology, instructions on how to run the code, and key evaluation metrics.

#### Step 4: Presentation Pitch Deck Content Preparation
1. Inspect the official presentation template located in `Coding\Hackathons\India_runs_data_and_ai_challenge\resources`.
2. Generate a highly detailed, slide-by-slide markdown outline containing the exact technical content, charts description, and text to copy-paste into that template. Ensure it explicitly highlights:
   - What you built (Architecture & Frameworks used).
   - Why you built it that way (Design choices, handling semantic gaps vs keyword filters).
   - How it works (The exact scoring formula, fusion of behavioral signals, and validation results).

---

### 🚨 Guardrails & Verification
- Ensure all code runs without errors and includes logging/error handling.
- Double-check that the output `.xlsx` file is fully populated and uncorrupted.
- Verify that no hardcoded local absolute paths are left in the production scripts so that the repository is completely ready to be made public on GitHub.

Let's begin. Start by locating the dataset and analyzing its structure, then report back with your proposed ranking engine design.