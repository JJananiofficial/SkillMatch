# SkillMatch AI

**An AI-assisted resume and job-description matching application built with Python and Streamlit.**

SkillMatch AI compares resume content with a job description, identifies listed skills, calculates a text-similarity score, highlights matched and missing skills, and provides practical recommendations.

## Features

- Upload a resume in PDF format or enter resume text.
- Paste a job description for comparison.
- Extract skills using a configurable skills dictionary (`data/skills.json`).
- Calculate a TF-IDF-style cosine similarity score.
- Identify matched skills and skill gaps.
- Generate recommendations based on missing skills.
- View a results dashboard with a skill breakdown.

## Technology stack

- Python
- Streamlit
- pandas and NumPy
- pypdf for PDF text extraction
- Plotly for interactive visualisation

## Run locally

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Skillmatch-ai
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Start the application

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually `http://localhost:8501`.

## Run tests

From the project root, run:

```bash
python -m unittest discover -v
```

## Project structure

```text
Skillmatch-ai/
├── app.py
├── data/
│   └── skills.json
├── sample/
│   ├── sample_job_description.txt
│   └── sample_resume.txt
├── src/
│   ├── matcher.py
│   ├── pdf_parser.py
│   ├── recommender.py
│   ├── skill_extractor.py
│   └── text_processor.py
├── tests/
│   ├── test_matcher.py
│   └── test_skill_extractor.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Configuration

Add or edit skills in `data/skills.json`. Skills are matched against the extracted resume and job-description text.

## Important limitations

- The match percentage is a text-similarity indicator, not a probability of getting an interview or a measure of a candidate's overall suitability.
- Skill extraction depends on the terms configured in `data/skills.json`; synonyms and context may not always be recognised.
- PDF extraction works best with text-based PDFs. Scanned image-only PDFs may require OCR, which is not currently included.
- Recommendations are rule-based and should be treated as guidance, not hiring decisions.
- Do not upload sensitive personal information or use this tool as the sole basis for employment decisions.

## Sample files

The `sample/` folder contains fictional example resume and job-description text for local testing. Do not treat the sample profile as a real candidate.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
