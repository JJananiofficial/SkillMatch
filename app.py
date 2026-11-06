import html
import re
import streamlit as st
import pandas as pd
from src.pdf_parser import extract_text_from_pdf
from src.skill_extractor import load_skills_dict, extract_skills
from src.matcher import calculate_match_score, calculate_skill_gap
from src.recommender import get_score_interpretation, generate_recommendations

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# --- PAGE CONFIG ---
st.set_page_config(page_title="SkillMatch AI", layout="wide")

# --- CONSTANTS ---
MIN_RESUME_WORDS = 20
MIN_JD_WORDS = 10
MAX_PDF_MB = 10

# ============================================================
#  THEME — black canvas, white type, violet accents
# ============================================================
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

/* ---- Base canvas: deep black with a soft purple bloom ---- */
.stApp {
    background:
        radial-gradient(1100px 520px at 85% -10%, rgba(139, 92, 246, 0.09), transparent 60%),
        radial-gradient(800px 420px at -10% 110%, rgba(124, 58, 237, 0.06), transparent 60%),
        #0a0a0f;
    color: #e5e7eb;
    -webkit-font-smoothing: antialiased;
}
html, body, .stApp, .stMarkdown, p, li, span, label {
    font-family: 'Inter', -apple-system, sans-serif;
}

/* ---- Strip default Streamlit chrome ---- */
#MainMenu, footer, header[data-testid="stHeader"], div[data-testid="stToolbar"] {
    visibility: hidden; height: 0;
}
.block-container { padding: 1.5rem 2rem 5rem; max-width: 1250px; }

::selection { background: rgba(139, 92, 246, 0.4); }
::-webkit-scrollbar { width: 9px; }
::-webkit-scrollbar-thumb { background: #2a2438; border-radius: 10px; }
::-webkit-scrollbar-track { background: transparent; }

hr {
    border: none; height: 1px; margin: 2.2rem 0;
    background: linear-gradient(90deg, transparent, #2a2438 30%, #2a2438 70%, transparent);
}
.stMarkdown ul li::marker { color: #a78bfa; }

/* ---- Hero ---- */
.hero { text-align: center; padding: 2.6rem 0 1.8rem; }
.hero-badge {
    display: inline-block; padding: 6px 18px; border-radius: 100px;
    border: 1px solid rgba(139, 92, 246, 0.35); background: rgba(139, 92, 246, 0.08);
    color: #c4b5fd; font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 1.1rem;
}
.hero-title {
    font-family: 'Outfit', sans-serif; font-weight: 800; margin: 0;
    font-size: clamp(2.4rem, 5vw, 3.6rem); line-height: 1.08;
    background: linear-gradient(135deg, #ffffff 25%, #c4b5fd 65%, #8b5cf6 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: #9ca3af; font-size: 1.02rem; line-height: 1.65;
    max-width: 560px; margin: 0.9rem auto 0;
}

/* ---- Section headers with violet accent bar ---- */
.section-header { display: flex; align-items: center; gap: 12px; margin: 6px 0 14px; }
.accent-bar {
    width: 4px; height: 24px; border-radius: 3px; flex-shrink: 0;
    background: linear-gradient(180deg, #a78bfa, #7c3aed);
    box-shadow: 0 0 14px rgba(139, 92, 246, 0.55);
}
.section-text { display: flex; flex-direction: column; line-height: 1.2; }
.section-title { font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 600; color: #f3f4f6; }
.section-sub { color: #8b8fa3; font-size: 0.78rem; margin-top: 3px; }

/* ---- Input cards (bordered containers) ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #211c31 !important;
    border-radius: 18px !important;
    background: linear-gradient(180deg, rgba(255,255,255,0.025), rgba(255,255,255,0.005)) !important;
}

/* ---- Text areas ---- */
.stTextArea textarea, div[data-testid="stTextArea"] textarea {
    background: #0e0c16; color: #e5e7eb;
    border: 1px solid #2a2438; border-radius: 12px;
    font-size: 0.9rem; line-height: 1.6;
    transition: border-color .2s, box-shadow .2s;
}
.stTextArea textarea:focus, div[data-testid="stTextArea"] textarea:focus {
    border-color: #8b5cf6;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

/* ---- Radio as segmented pills ---- */
div[role="radiogroup"] { gap: 8px; }
div[role="radiogroup"] label {
    background: #0e0c16; border: 1px solid #2a2438; border-radius: 10px;
    padding: 7px 16px; transition: all .2s; cursor: pointer;
}
div[role="radiogroup"] label p { color: #d1d5db; font-size: 0.88rem; }
div[role="radiogroup"] label:hover { border-color: #8b5cf6; }
div[role="radiogroup"] label[data-checked="true"] {
    border-color: #8b5cf6; background: rgba(139, 92, 246, 0.1);
}
div[role="radiogroup"] label[data-checked="true"] p { color: #e9d5ff; }

/* ---- File uploader ---- */
div[data-testid="stFileUploaderDropzone"] {
    background: #0e0c16; border: 1.5px dashed #332c4a; border-radius: 12px;
    transition: all .2s;
}
div[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #8b5cf6; background: rgba(139, 92, 246, 0.04);
}
div[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #fff; border: none; border-radius: 8px; font-weight: 600;
}

/* ---- Buttons ---- */
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 55%, #c084fc 100%);
    color: #ffffff; border: none; border-radius: 14px;
    padding: 0.95rem 2rem;
    font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 600;
    box-shadow: 0 6px 26px rgba(124, 58, 237, 0.35);
    transition: all .3s cubic-bezier(.4, 0, .2, 1);
}
.stButton > button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 36px rgba(124, 58, 237, 0.55);
}
.stButton > button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
    width: 100%;
    background: rgba(255,255,255,0.03); color: #d1d5db;
    border: 1px solid #2a2438; border-radius: 14px;
    padding: 0.95rem 1.2rem; transition: all .25s;
}
.stButton > button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
    border-color: #8b5cf6; color: #ffffff; background: rgba(139, 92, 246, 0.08);
}
.stDownloadButton > button, button[data-testid="stBaseButton-download"] {
    background: rgba(139, 92, 246, 0.08); color: #c4b5fd;
    border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 12px;
    padding: 0.55rem 1.4rem; font-weight: 600; transition: all .25s;
}
.stDownloadButton > button:hover, button[data-testid="stBaseButton-download"]:hover {
    background: rgba(139, 92, 246, 0.18); border-color: #8b5cf6; color: #fff;
}

/* ---- Score ring ---- */
.ring-wrap { display: flex; justify-content: center; padding: 8px 0 4px; }
.score-ring {
    width: 168px; height: 168px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 44px rgba(139, 92, 246, 0.28);
}
.ring-inner {
    width: 136px; height: 136px; border-radius: 50%; background: #0c0a14;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.ring-value {
    font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 700;
    color: #ffffff; line-height: 1;
}
.ring-label {
    font-size: 0.68rem; color: #8b8fa3; margin-top: 6px;
    letter-spacing: 0.14em; text-transform: uppercase;
}

/* ---- Metric cards ---- */
.metric-card {
    background: linear-gradient(160deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid #221c33; border-radius: 14px; padding: 14px 18px;
}
.metric-card.accent {
    border-color: rgba(139, 92, 246, 0.45);
    background: linear-gradient(160deg, rgba(139,92,246,0.14), rgba(139,92,246,0.03));
}
.metric-label {
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: #8b8fa3; font-weight: 600; margin-bottom: 6px;
}
.metric-value { font-family: 'Outfit', sans-serif; font-size: 1.85rem; font-weight: 700; color: #f3f4f6; line-height: 1; }
.metric-card.accent .metric-value { color: #a78bfa; }

/* ---- Meter bar ---- */
.meter-row { display: flex; justify-content: space-between; align-items: baseline; margin: 14px 0 8px; }
.meter-label { color: #8b8fa3; font-size: 0.82rem; font-weight: 500; }
.meter-value { font-family: 'Outfit', sans-serif; color: #a78bfa; font-weight: 700; font-size: 0.95rem; }
.meter { height: 8px; background: #1a1626; border-radius: 100px; overflow: hidden; }
.meter-fill {
    height: 100%; border-radius: 100px;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #c084fc);
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.5);
    animation: grow 1.2s cubic-bezier(.25, .8, .25, 1);
}
@keyframes grow { from { width: 0; } }

/* ---- Callout ---- */
.callout {
    background: linear-gradient(135deg, rgba(139,92,246,0.09), rgba(139,92,246,0.02));
    border: 1px solid rgba(139, 92, 246, 0.3); border-left: 3px solid #8b5cf6;
    border-radius: 12px; padding: 14px 18px; color: #d1d5db;
    font-size: 0.92rem; line-height: 1.6; margin-top: 16px;
}
.callout b { color: #e9d5ff; }

/* ---- Skill cards & pills ---- */
.skill-card {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px; border-radius: 14px; margin-bottom: 14px;
}
.skill-card.matched { background: rgba(139,92,246,0.1); border: 1px solid rgba(139,92,246,0.35); }
.skill-card.missing { background: rgba(255,255,255,0.02); border: 1px solid #2a2438; }
.skill-card-title { font-family: 'Outfit', sans-serif; font-weight: 600; color: #e5e7eb; }
.skill-count {
    margin-left: auto; font-family: 'Outfit', sans-serif; font-weight: 700;
    color: #a78bfa; background: rgba(139,92,246,0.12);
    padding: 2px 11px; border-radius: 100px; font-size: 0.8rem;
}
.pill-wrap { line-height: 2.1; }
.pill {
    display: inline-block; padding: 5px 14px; border-radius: 100px; margin: 2px;
    font-size: 0.83rem; font-weight: 500; transition: all .2s;
}
.pill-matched {
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.45);
    color: #d8b4fe;
}
.pill-matched:hover { background: rgba(139, 92, 246, 0.28); transform: translateY(-1px); }
.pill-missing {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid #333042; color: #9ca3af;
}
.pill-missing:hover { border-color: #8b5cf6; color: #e5e7eb; }
.empty-list, .all-clear {
    color: #6b7280; font-size: 0.88rem; line-height: 1.6;
    padding: 10px 2px;
}
.all-clear { color: #a78bfa; }
.chart-title { font-family: 'Outfit', sans-serif; font-weight: 600; color: #f3f4f6; margin-bottom: 6px; }

/* ---- Empty state ---- */
.empty-state {
    text-align: center; padding: 3.5rem 2rem; margin-top: 1rem;
    border: 1.5px dashed #2a2438; border-radius: 20px;
    background: rgba(255, 255, 255, 0.01);
}
.empty-glyph {
    font-size: 2rem; color: #8b5cf6; margin-bottom: 0.6rem;
    text-shadow: 0 0 26px rgba(139, 92, 246, 0.7);
}
.empty-state h3 { font-family: 'Outfit', sans-serif; color: #e5e7eb; margin: 0 0 0.4rem; font-size: 1.15rem; }
.empty-state p { color: #6b7280; font-size: 0.92rem; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
    background: #0d0b15; border-right: 1px solid #1c1828;
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
.brand { display: flex; align-items: center; gap: 11px; padding: 2px 0 20px; }
.brand-mark {
    width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0;
    background: linear-gradient(135deg, #7c3aed, #a855f7);
    color: #fff; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.05rem;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 18px rgba(124, 58, 237, 0.45);
}
.brand-name { font-family: 'Outfit', sans-serif; font-size: 1.05rem; color: #f3f4f6; }
.brand-name b { color: #a78bfa; }
.side-heading {
    font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: #8b8fa3; font-weight: 600; margin: 20px 0 12px;
}
.step { display: flex; gap: 12px; margin-bottom: 15px; }
.step-num {
    width: 28px; height: 28px; border-radius: 9px; flex-shrink: 0;
    background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.35);
    color: #a78bfa; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.78rem;
    display: flex; align-items: center; justify-content: center; margin-top: 1px;
}
.step-title { color: #e5e7eb; font-weight: 600; font-size: 0.88rem; }
.step-desc { color: #8b8fa3; font-size: 0.8rem; margin-top: 2px; line-height: 1.5; }
.side-box {
    border: 1px dashed #2a2438; border-radius: 14px;
    padding: 14px 16px; margin-top: 8px;
}
.side-box-title {
    color: #a78bfa; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px;
}
.side-box p { color: #8b8fa3; font-size: 0.8rem; line-height: 1.55; margin: 0; }
"""

st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)


# ============================================================
#  LOGIC
# ============================================================
@st.cache_data
def get_skills_dict():
    return load_skills_dict()


def run_analysis(resume_text, jd_text):
    """Run the full pipeline once and return a results dict."""
    # 1. Get pure text similarity
    text_similarity_score = calculate_match_score(resume_text, jd_text)
    
    # 2. Extract Skills
    skills_dict = get_skills_dict()
    resume_skills = extract_skills(resume_text, skills_dict)
    jd_skills = extract_skills(jd_text, skills_dict)
    matched, missing = calculate_skill_gap(resume_skills, jd_skills)

    # 3. Calculate a Hybrid Match Score (75% Skills, 25% Text Context)
    jd_total = len(jd_skills)
    if jd_total > 0:
        skill_score = (len(matched) / jd_total) * 100
        # Blend the two scores together
        final_score = int((skill_score * 0.75) + (text_similarity_score * 0.25))
    else:
        # If no skills are found in JD, just rely on text similarity
        final_score = text_similarity_score

    return {
        "score": final_score,
        "jd_skills": jd_skills,
        "matched": matched,
        "missing": missing,
        "interpretation": get_score_interpretation(final_score),
        "recommendations": generate_recommendations(matched, missing),
    }


def validate_inputs(resume_text, jd_text):
    """Return a warning message if inputs are invalid, else None."""
    if not resume_text.strip():
        return "⚠️ Please upload a resume or enter resume text."
    if not jd_text.strip():
        return "⚠️ Please enter a job description."
    if len(resume_text.split()) < MIN_RESUME_WORDS:
        return "⚠️ Resume text is too short. Please provide a complete resume."
    if len(jd_text.split()) < MIN_JD_WORDS:
        return "⚠️ Job description is too short to extract skills from."
    return None


def build_report(results):
    """Plain-text report for download."""
    matched = results["matched"] or ["(none)"]
    missing = results["missing"] or ["(none)"]
    return "\n".join([
        "SKILLMATCH AI — ANALYSIS REPORT",
        "=" * 40,
        f"Match Score: {results['score']}%",
        "",
        "MATCHED SKILLS:", *[f"  + {s}" for s in matched],
        "",
        "MISSING SKILLS:", *[f"  - {s}" for s in missing],
        "",
        "INTERPRETATION:", results["interpretation"].replace("**", ""),
        "",
        "RECOMMENDATIONS:", results["recommendations"].replace("**", ""),
    ])


# ============================================================
#  RENDERING HELPERS
# ============================================================
def md_inline_to_html(text):
    """Convert **bold** to <b> so it renders inside custom HTML blocks."""
    text = html.escape(str(text))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.replace("*", "")


def section_header(title, subtitle=None):
    sub = f'<span class="section-sub">{html.escape(subtitle)}</span>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <span class="accent-bar"></span>
            <div class="section-text">
                <span class="section-title">{html.escape(title)}</span>
                {sub}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, accent=False):
    cls = "metric-card accent" if accent else "metric-card"
    return f"""
    <div class="{cls}">
        <div class="metric-label">{html.escape(label)}</div>
        <div class="metric-value">{html.escape(str(value))}</div>
    </div>"""


def render_score_ring(score, label="Match Score"):
    pct = max(0.0, min(float(score), 100.0))
    turns = pct / 100
    st.markdown(
        f"""
        <div class="ring-wrap">
            <div class="score-ring" style="background: conic-gradient(#8b5cf6 0turn {turns:.3f}turn, #221c33 {turns:.3f}turn 1turn);">
                <div class="ring-inner">
                    <span class="ring-value">{pct:.0f}%</span>
                    <span class="ring-label">{html.escape(label)}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_meter(label, pct):
    pct = max(0.0, min(float(pct), 100.0))
    st.markdown(
        f"""
        <div class="meter-row">
            <span class="meter-label">{html.escape(label)}</span>
            <span class="meter-value">{pct:.0f}%</span>
        </div>
        <div class="meter"><div class="meter-fill" style="width: {pct:.1f}%;"></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_card(title, count, variant, icon):
    st.markdown(
        f"""
        <div class="skill-card {variant}">
            <span>{icon}</span>
            <span class="skill-card-title">{html.escape(title)}</span>
            <span class="skill-count">{count}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_pills(skills, variant):
    if not skills:
        st.markdown('<div class="empty-list">None found.</div>', unsafe_allow_html=True)
        return
    pills = "".join(
        f'<span class="pill pill-{variant}">{html.escape(skill)}</span>' for skill in skills
    )
    st.markdown(f'<div class="pill-wrap">{pills}</div>', unsafe_allow_html=True)


def render_callout(text):
    st.markdown(f'<div class="callout">{md_inline_to_html(text)}</div>', unsafe_allow_html=True)


def render_breakdown_chart(matched_count, missing_count):
    if not PLOTLY_AVAILABLE:
        st.bar_chart(pd.DataFrame(
            {"Count": [matched_count, missing_count]}, index=["Matched", "Missing"]
        ))
        return
    fig = px.pie(
        values=[matched_count, missing_count],
        names=["Matched", "Missing"],
        hole=0.62,
        color_discrete_map={"Matched": "#8b5cf6", "Missing": "#2e2840"},
    )
    fig.update_traces(
        textinfo="value",
        textfont={"color": "#e5e7eb", "size": 15},
        hovertemplate="<b>%{label}</b>: %{value} skills<extra></extra>",
        marker={"line": {"width": 2, "color": "#0a0a0f"}},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#9ca3af", "family": "Inter"},
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        showlegend=True,
        legend={"orientation": "h", "y": -0.04, "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_results(results):
    score = results["score"]
    jd_total = len(results["jd_skills"])
    matched, missing = results["matched"], results["missing"]
    match_rate = (len(matched) / jd_total * 100) if jd_total else 0

    section_header("Results Dashboard", f"Based on {jd_total} skills detected in the job description")

    # --- Score ring + key numbers ---
    ring_col, stats_col = st.columns([1, 2], gap="large")

    with ring_col:
        render_score_ring(score)

    with stats_col:
        k1, k2, k3 = st.columns(3)
        k1.markdown(metric_card("Skills in JD", jd_total), unsafe_allow_html=True)
        k2.markdown(metric_card("Matched", len(matched), accent=True), unsafe_allow_html=True)
        k3.markdown(metric_card("Missing", len(missing)), unsafe_allow_html=True)

        render_meter("Skill coverage of the job description", match_rate)
        render_callout(results["interpretation"])

    # --- Download (centered) ---
    d1, d2, d3 = st.columns([2, 1, 2])
    with d2:
        st.download_button(
            "Download Report",
            data=build_report(results),
            file_name="skillmatch_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("---")

    # --- Skill analysis ---
    section_header("Skill Analysis", "Your resume vs. the job requirements")
    c1, c2, c3 = st.columns([1, 1, 1.2], gap="large")

    with c1:
        render_skill_card("Matched Skills", len(matched), "matched", "✅")
        render_skill_pills(matched, "matched")

    with c2:
        render_skill_card("Missing Skills", len(missing), "missing", "❌")
        if missing:
            render_skill_pills(missing, "missing")
        else:
            st.markdown(
                '<div class="all-clear">No missing skills — you match every extracted requirement.</div>',
                unsafe_allow_html=True,
            )

    with c3:
        st.markdown('<div class="chart-title">Match Breakdown</div>', unsafe_allow_html=True)
        if jd_total:
            render_breakdown_chart(len(matched), len(missing))
        else:
            st.markdown(
                '<div class="empty-list">No known skills were detected in this job description.</div>',
                unsafe_allow_html=True,
            )

    # --- Recommendation ---
    st.markdown("---")
    section_header("Recommendation", "Personalized suggestions based on your gaps")
    st.markdown(results["recommendations"])


# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <span class="brand-mark">S</span>
            <span class="brand-name">SkillMatch <b>AI</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-heading">How it works</div>', unsafe_allow_html=True)
    steps = [
        ("01", "Add your resume", "Upload a PDF or paste the text."),
        ("02", "Add the job description", "Copy it straight from the listing."),
        ("03", "Analyze the match", "See your score, gaps and next steps."),
    ]
    for num, title, desc in steps:
        st.markdown(
            f"""
            <div class="step">
                <span class="step-num">{num}</span>
                <div>
                    <div class="step-title">{html.escape(title)}</div>
                    <div class="step-desc">{html.escape(desc)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="side-box">
            <div class="side-box-title">Privacy</div>
            <p>Everything runs locally in this app. Your resume is never sent to any external service.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
#  HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Resume Analysis</div>
        <h1 class="hero-title">SkillMatch AI</h1>
        <p class="hero-sub">
            Match your resume against any job description in seconds.
            Discover your skill gaps and get clear, personalized recommendations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
#  INPUTS
# ============================================================
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        section_header("Resume", "Upload a PDF or paste your text")
        resume_mode = st.radio("Choose input method:", ("Upload PDF", "Paste Text"), horizontal=True)
        resume_text = ""

        if resume_mode == "Upload PDF":
            uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
            if uploaded_file is not None:
                if uploaded_file.size > MAX_PDF_MB * 1024 * 1024:
                    st.error(f"File too large — please keep it under {MAX_PDF_MB} MB.")
                else:
                    try:
                        resume_text = extract_text_from_pdf(uploaded_file)
                        if not resume_text.strip():
                            st.error("Couldn't extract text — the PDF may be scanned or image-based. Try pasting the text instead.")
                    except Exception as exc:
                        st.error(f"Error reading PDF: {exc}")
        else:
            resume_text = st.text_area("Paste your resume text here:", height=280)

        if resume_text:
            st.caption(f"{len(resume_text.split())} words")

with col2:
    with st.container(border=True):
        section_header("Job Description", "Paste the full listing for best results")
        jd_text = st.text_area("Paste the job description here:", height=344)
        if jd_text:
            st.caption(f"{len(jd_text.split())} words")


# ============================================================
#  ACTIONS
# ============================================================
st.markdown("---")
btn_col, reset_col = st.columns([4, 1], gap="small")
analyze_clicked = btn_col.button("Analyze Match", type="primary", use_container_width=True)
reset_clicked = reset_col.button("Clear Results", use_container_width=True)

if reset_clicked:
    st.session_state.pop("results", None)
    st.session_state.pop("input_sig", None)

if analyze_clicked:
    error_msg = validate_inputs(resume_text, jd_text)
    if error_msg:
        st.warning(error_msg)
    else:
        with st.spinner("Analyzing text and extracting skills..."):
            st.session_state.results = run_analysis(resume_text, jd_text)
            st.session_state.input_sig = hash((resume_text, jd_text))


# ============================================================
#  RESULTS / EMPTY STATE
# ============================================================
if "results" in st.session_state:
    if st.session_state.get("input_sig") != hash((resume_text, jd_text)):
        st.warning("Inputs have changed since the last analysis — results below may be outdated.")
    render_results(st.session_state.results)
else:
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-glyph">◈</div>
            <h3>No analysis yet</h3>
            <p>Add your resume and a job description above,<br>then hit <b>Analyze Match</b> to see your results here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )