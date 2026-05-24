import streamlit as st
from reviewer import review_resume

st.set_page_config(
    page_title="AI Resume Reviewer",
    page_icon="📄",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .header-text {
        background: linear-gradient(90deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: 800;
    }
    .score-card {
        background: linear-gradient(135deg, #1e3a5f, #1a1a2e);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #3b82f6;
    }
    .improvement-card {
        background: #1f2937;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #f59e0b;
    }
    .verdict-box {
        background: linear-gradient(135deg, #064e3b, #1a1a2e);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 2px solid #10b981;
        font-size: 18px;
        color: #ffffff;
        margin-top: 20px;
    }
    .bar-container {
        background: #1f2937;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .bar-label {
        color: #e5e7eb;
        font-size: 14px;
        min-width: 250px;
        flex: 2;
    }
    .bar-track {
        background: #374151;
        border-radius: 20px;
        height: 12px;
        flex: 1;
        overflow: hidden;
    }
    .bar-fill-green {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #10b981, #34d399);
        animation: growBar 1.2s ease-out forwards;
        transform-origin: left;
    }
    .bar-fill-red {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #ef4444, #f87171);
        animation: growBar 1.2s ease-out forwards;
        transform-origin: left;
    }
    .bar-fill-blue {
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        animation: growBar 1.2s ease-out forwards;
        transform-origin: left;
    }
    @keyframes growBar {
        from { width: 0%; }
        to { width: var(--target-width); }
    }
    .bar-percent {
        color: #9ca3af;
        font-size: 13px;
        min-width: 40px;
        text-align: right;
    }
    .section-header {
        color: #ffffff;
        font-size: 20px;
        font-weight: 700;
        margin: 20px 0 10px 0;
    }
    .ats-box {
        background: #1f2937;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #3b82f6;
        color: #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# ── Helper: animated bar ──────────────────────────────────────────────────────
def animated_bar(label, percentage, color="green"):
    css_class = f"bar-fill-{color}"
    return f"""
    <div class="bar-container">
        <div class="bar-label">{label}</div>
        <div class="bar-track">
            <div class="{css_class}" style="--target-width:{percentage}%; width:{percentage}%;"></div>
        </div>
        <div class="bar-percent">{percentage}%</div>
    </div>
    """

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="header-text">📄 AI Resume Reviewer</p>',
            unsafe_allow_html=True)
st.markdown("##### Upload your resume → AI reads it → tells you exactly what to fix")
st.markdown("---")

# ── Input Section ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📎 Upload Your Resume (PDF only)",
        type=["pdf"],
        help="Make sure your resume is a text-based PDF, not a scanned image"
    )

with col2:
    job_role = st.selectbox(
        "🎯 Target Job Role",
        [
            "Software Engineer",
            "Data Analyst",
            "Data Scientist",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "Machine Learning Engineer",
            "DevOps Engineer",
            "Product Manager",
            "UI/UX Designer",
            "Business Analyst",
            "Marketing Manager"
        ]
    )

    analyze_btn = st.button(
        "🔍 Analyze My Resume",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )

if uploaded_file is None:
    st.info("👆 Upload your resume PDF to get started")

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyze_btn and uploaded_file:
    with st.spinner("🤖 AI is reading and analyzing your resume..."):
        result = review_resume(uploaded_file, job_role)

    if not result["success"]:
        st.error(f"❌ Error: {result['error']}")
    else:
        st.success("✅ Analysis Complete!")
        st.markdown("---")

        # ── Score cards ───────────────────────────────────────────────────────
        # Extract numeric scores safely
        def safe_score(val):
            try:
                return float(str(val).strip().split("/")[0].strip())
            except:
                return 5.0

        overall = safe_score(result['overall_score'])
        ats = safe_score(result['ats_score'])
        overall_pct = int(overall * 10)
        ats_pct = int(ats * 10)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="score-card">
                <h1 style="color:#3b82f6;font-size:48px">{result['overall_score']}/10</h1>
                <p style="color:#9ca3af">Overall Score</p>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="score-card">
                <h1 style="color:#10b981;font-size:48px">{result['ats_score']}/10</h1>
                <p style="color:#9ca3af">ATS Score</p>
            </div>""", unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="score-card">
                <h1 style="color:#f59e0b;font-size:48px">{len(result['improvements'])}</h1>
                <p style="color:#9ca3af">Action Items</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Summary ───────────────────────────────────────────────────────────
        st.markdown("### 📋 Overall Summary")
        st.info(result["summary"])

        st.markdown("---")

        # ── Strengths with animated green bars ───────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<p class="section-header">✅ Strengths</p>',
                        unsafe_allow_html=True)
            strengths = result["strengths"]
            total = len(strengths)
            bars_html = ""
            for i, s in enumerate(strengths):
                # spread bars from 95% down to 70%
                pct = int(95 - (i * (25 / max(total - 1, 1))))
                bars_html += animated_bar(s, pct, "green")
            st.markdown(bars_html, unsafe_allow_html=True)

        with col2:
            st.markdown('<p class="section-header">❌ Weaknesses</p>',
                        unsafe_allow_html=True)
            weaknesses = result["weaknesses"]
            total_w = len(weaknesses)
            bars_html_w = ""
            for i, w in enumerate(weaknesses):
                pct = int(75 - (i * (20 / max(total_w - 1, 1))))
                bars_html_w += animated_bar(w, pct, "red")
            st.markdown(bars_html_w, unsafe_allow_html=True)

        st.markdown("---")

        # ── Missing Sections ──────────────────────────────────────────────────
        if result["missing_sections"]:
            st.markdown("### ⚠️ Missing Sections")
            cols = st.columns(len(result["missing_sections"]))
            for i, m in enumerate(result["missing_sections"]):
                with cols[i]:
                    st.warning(f"Missing: {m}")

        st.markdown("---")

        # ── ATS with animated blue bar ────────────────────────────────────────
        st.markdown("### 🤖 ATS Compatibility")

        ats_bar = animated_bar(f"ATS Score: {result['ats_score']}/10",
                               ats_pct, "blue")
        st.markdown(ats_bar, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ats-box">
            {result['ats_feedback']}
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # ── Overall score bar ─────────────────────────────────────────────────
        st.markdown("### 📊 Score Overview")
        overall_bar = animated_bar(f"Overall Resume Score: {result['overall_score']}/10",
                                   overall_pct, "blue")
        st.markdown(overall_bar, unsafe_allow_html=True)

        st.markdown("---")

        # ── Improvements ──────────────────────────────────────────────────────
        st.markdown("### 🚀 Action Items — What To Fix")
        for i, imp in enumerate(result["improvements"], 1):
            st.markdown(f"""
            <div class="improvement-card">
                <strong style="color:#f59e0b">#{i}</strong>
                <span style="color:#e5e7eb"> {imp}</span>
            </div>""", unsafe_allow_html=True)

        # ── Verdict ───────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="verdict-box">
            🎯 <strong>Final Verdict:</strong> {result['verdict']}
        </div>""", unsafe_allow_html=True)

        # ── Raw output ────────────────────────────────────────────────────────
        with st.expander("🔧 View Raw AI Output"):
            st.text(result["raw"])