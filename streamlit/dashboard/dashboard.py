import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ast
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DS/AI Job Market Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME / COLORS
# ─────────────────────────────────────────────
C_PRIMARY   = "#7F77DD"
C_GREEN     = "#1D9E75"
C_ORANGE    = "#EF9F27"
C_RED       = "#E24B4A"
C_DARK      = "#D85A30"
C_LIGHT     = "#D3D1C7"

PALETTE_KKNI   = [C_GREEN, C_PRIMARY, C_DARK]
PALETTE_MATCH  = [C_GREEN, C_ORANGE, C_RED]
PALETTE_FAMILY = px.colors.qualitative.Pastel

KKNI_ORDER = [
    "Operator Pemula", "Operator", "Teknisi Junior", "Asisten Teknisi",
    "Teknisi/Analis Muda", "Teknisi/Analis Madya",
    "Ahli Pertama / Perdana", "Ahli Utama / Lead", "Pemimpin / C-Level",
]
KKNI_LEVEL_MAP = {
    "Operator Pemula": 1, "Operator": 2, "Teknisi Junior": 3,
    "Asisten Teknisi": 4, "Teknisi/Analis Muda": 5,
    "Teknisi/Analis Madya": 6, "Ahli Pertama / Perdana": 7,
    "Ahli Utama / Lead": 8, "Pemimpin / C-Level": 9,
}

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Main background */
.stApp { background-color: #0f1117; color: #e6e6e6; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #1a1d26; }
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 { color: #c9c4ff; }

/* KPI cards */
.kpi-card {
    background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
    border: 1px solid #3a3d55;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
}
.kpi-label { font-size: 0.82rem; color: #9999bb; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value { font-size: 2.1rem; font-weight: 700; color: #c9c4ff; line-height: 1.1; }
.kpi-sub   { font-size: 0.78rem; color: #6c6e8a; margin-top: 4px; }

/* Section headers */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #c9c4ff;
    border-left: 4px solid #7F77DD;
    padding-left: 12px;
    margin: 24px 0 16px 0;
}

/* Insight boxes */
.insight-box {
    background: #1a1d26;
    border: 1px solid #2e3148;
    border-left: 4px solid #7F77DD;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #c0c0d8;
    margin-top: 12px;
    line-height: 1.6;
}

/* Tab styling */
button[data-baseweb="tab"] { font-size: 0.9rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
current_dir = os.path.dirname(os.path.abspath(__file__))

def load_data():
    job_path      = os.path.join(current_dir, 'job_clean.csv')
    pontik_path   = os.path.join(current_dir, "pontik_enriched.csv")
    cand_path     = os.path.join(current_dir, "resume_candidate_clean.csv")
    job_req_path  = os.path.join(current_dir, "resume_job_req_clean.csv")
    
    job      = pd.read_csv(job_path)
    pontik   = pd.read_csv(pontik_path)
    cand     = pd.read_csv(cand_path)
    job_req  = pd.read_csv(job_req_path)
    
    return job, pontik, cand, job_req

df_job, df_pontik, df_cand, df_job_req = load_data()
    

    # Parse skill_list column (stored as string repr of list)
    def parse_list_col(val):
        if pd.isna(val): return []
        try:
            parsed = ast.literal_eval(val)
            return parsed if isinstance(parsed, list) else []
        except:
            return []

    job["skill_list_parsed"] = job["skill_list"].apply(parse_list_col)

    cand["skills_parsed_list"] = cand["skills_parsed"].apply(parse_list_col)

    # Derive overlap category
    overlap_map = {0: "0 skill", 1: "1 skill", 2: "2 skill", 3: "3 skill", 4: "4+ skill", 5: "4+ skill"}
    cand["overlap_cat"] = cand["overlap_with_job_skills"].map(overlap_map).fillna("0 skill")

    return job, pontik, cand, job_req

job, pontik, cand, job_req = load_data()

SKILL_COLS  = ["skills_python", "skills_sql", "skills_ml", "skills_deep_learning", "skills_cloud"]
SKILL_NAMES = ["Python", "SQL", "Machine Learning", "Deep Learning", "Cloud"]


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 DS/AI Market\n### Dashboard")
    st.markdown("---")

    st.markdown("**Filter Pasar Kerja**")
    job_titles = ["Semua"] + sorted(job["job_title"].unique().tolist())
    sel_title  = st.selectbox("Job Title", job_titles)

    exp_levels = ["Semua"] + sorted(job["experience_level"].unique().tolist())
    sel_exp    = st.selectbox("Experience Level", exp_levels)

    st.markdown("---")
    st.markdown("**Filter Kandidat**")
    match_cats  = ["Semua"] + ["High Match", "Mid Match", "Low Match"]
    sel_match   = st.selectbox("Match Category", match_cats)

    st.markdown("---")
    st.caption("📊 Sumber data: pontik_enriched · job_clean · resume_candidate_clean · resume_job_req_clean")
    st.caption("🔍 5 Pertanyaan Bisnis DS/AI")


# ─────────────────────────────────────────────
# FILTERED DATAFRAMES
# ─────────────────────────────────────────────
job_f = job.copy()
if sel_title != "Semua":
    job_f = job_f[job_f["job_title"] == sel_title]
if sel_exp != "Semua":
    job_f = job_f[job_f["experience_level"] == sel_exp]

cand_f = cand.copy()
if sel_match != "Semua":
    cand_f = cand_f[cand_f["match_category"] == sel_match]


# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.markdown("# 🧠 DS/AI Job Market Intelligence")
st.markdown("Analisis pasar kerja Data Science & AI berdasarkan data lowongan, standar KKNI Pontik, dan profil kandidat.")
st.markdown("---")


# ─────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

avg_score   = cand["matched_score"].mean()
high_pct    = (cand["match_category"] == "High Match").mean() * 100
total_jobs  = len(job_f)
total_cand  = len(cand_f)
total_roles = len(pontik)

for col, label, val, sub in [
    (k1, "Total Lowongan",        f"{total_jobs:,}",     f"filtered · {sel_title}"),
    (k2, "Total Kandidat",        f"{total_cand:,}",     f"filtered · {sel_match}"),
    (k3, "Peran KKNI (DSC)",      f"{total_roles}",      "dari framework pontik"),
    (k4, "Avg Matched Score",     f"{avg_score:.2f}",    "seluruh kandidat"),
    (k5, "High Match Rate",       f"{high_pct:.1f}%",    "score ≥ 0.75"),
]:
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS → 5 PERTANYAAN BISNIS
# ─────────────────────────────────────────────
tabs = st.tabs([
    "📊 BQ1 · Distribusi KKNI",
    "🛠️ BQ2 · Skill per Job Title",
    "🎯 BQ3 · Matched Score",
    "🔗 BQ4 · Relevansi Skill",
    "⚖️ BQ5 · Gap Analysis",
])


# ══════════════════════════════════════════════
# BQ1 · Distribusi level KKNI di pasar kerja DS/AI
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-header">BQ1 · Distribusi Level KKNI di Pasar Kerja DS/AI</div>', unsafe_allow_html=True)
    st.markdown("Bagaimana sebaran level KKNI lowongan pekerjaan dan ketersediaan peran di framework Pontik?")

    col_a, col_b = st.columns(2)

    # ── Panel kiri: Distribusi KKNI dari job_clean ──
    with col_a:
        st.markdown("##### Jumlah Lowongan per Level KKNI (Job Market)")
        kkni_dist = job_f.groupby(["kkni_level_mapped", "kkni_label"]).size().reset_index(name="count")
        kkni_dist = kkni_dist.sort_values("kkni_level_mapped")

        fig_bar = px.bar(
            kkni_dist,
            x="kkni_label", y="count",
            color="kkni_label",
            color_discrete_sequence=PALETTE_KKNI,
            text="count",
            labels={"kkni_label": "Level KKNI", "count": "Jumlah Lowongan"},
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(
            showlegend=False,
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6",
            xaxis=dict(tickangle=-15),
            margin=dict(t=30, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Panel kanan: Heatmap job_title × experience_level ──
    with col_b:
        st.markdown("##### Heatmap: Job Title × Experience Level")
        pivot = job_f.groupby(["job_title", "experience_level"]).size().unstack(fill_value=0)
        for col in ["Entry", "Mid", "Senior"]:
            if col not in pivot.columns:
                pivot[col] = 0
        pivot = pivot[["Entry", "Mid", "Senior"]]

        fig_heat = px.imshow(
            pivot,
            text_auto=True,
            color_continuous_scale="Purples",
            labels=dict(x="Experience Level", y="Job Title", color="Count"),
            aspect="auto",
        )
        fig_heat.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6",
            margin=dict(t=30, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Baris bawah: Distribusi KKNI dari Pontik ──
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown("##### Peran di Pontik per Job Family")
        fam_dist = pontik["job_family"].value_counts().reset_index()
        fam_dist.columns = ["job_family", "count"]
        fig_fam = px.bar(
            fam_dist.sort_values("count"),
            x="count", y="job_family",
            orientation="h",
            color="count",
            color_continuous_scale="purples",
            text="count",
        )
        fig_fam.update_traces(textposition="outside")
        fig_fam.update_layout(
            showlegend=False, coloraxis_showscale=False,
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6", margin=dict(t=30, b=10),
            xaxis_title="Jumlah Peran", yaxis_title="",
        )
        st.plotly_chart(fig_fam, use_container_width=True)

    with col_d:
        st.markdown("##### Distribusi KKNI Level di Pontik (DSC)")
        lvl_dist = pontik.groupby(["kkni_level", "kkni_label"]).size().reset_index(name="count")
        lvl_dist = lvl_dist.sort_values("kkni_level")
        fig_lvl = px.bar(
            lvl_dist,
            x="kkni_label", y="count",
            color="kkni_level",
            color_continuous_scale="Teal",
            text="count",
        )
        fig_lvl.update_traces(textposition="outside")
        fig_lvl.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6", margin=dict(t=30, b=10),
            xaxis=dict(tickangle=-20), xaxis_title="", yaxis_title="Jumlah Peran",
        )
        st.plotly_chart(fig_lvl, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Pasar kerja DS/AI didominasi level <strong>Mid (KKNI 6)</strong> dan
    <strong>Senior (KKNI 7)</strong> — level Entry sangat terbatas. Di Pontik, distribusi peran terkonsentrasi
    di <strong>Data Operations & Data Engineering</strong>. Ini mengindikasikan kebutuhan tenaga teknis menengah–lanjut
    yang tinggi di ekosistem DS/AI.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# BQ2 · Skill paling banyak diminta per job title
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">BQ2 · Skill yang Paling Banyak Diminta per Job Title</div>', unsafe_allow_html=True)
    st.markdown("Skill teknikal apa yang dominan untuk setiap job title di pasar DS/AI?")

    # ── Stacked bar: skill demand keseluruhan ──
    st.markdown("##### Persentase Permintaan Skill per Job Title")

    all_titles = sorted(job["job_title"].unique().tolist())
    skill_rows = []
    for title in all_titles:
        sub = job[job["job_title"] == title]
        n = len(sub)
        for col, name in zip(SKILL_COLS, SKILL_NAMES):
            skill_rows.append({
                "job_title": title,
                "skill": name,
                "pct": round(sub[col].sum() / n * 100, 1),
                "count": sub[col].sum(),
            })
    skill_df = pd.DataFrame(skill_rows)

    fig_stack = px.bar(
        skill_df,
        x="pct", y="job_title",
        color="skill",
        orientation="h",
        barmode="group",
        text="pct",
        color_discrete_sequence=[C_PRIMARY, C_GREEN, C_ORANGE, C_RED, C_DARK],
        labels={"pct": "% lowongan yang meminta", "job_title": ""},
    )
    fig_stack.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig_stack.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6", legend_title="Skill",
        margin=dict(t=20, b=10), height=420,
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    # ── Per-title detail (pilih dari selectbox) ──
    st.markdown("##### Detail Skill Demand per Job Title")
    sel_detail = st.selectbox("Pilih Job Title", all_titles, key="bq2_select")

    sub_detail = job[job["job_title"] == sel_detail]
    freq = sub_detail[SKILL_COLS].sum()
    freq.index = SKILL_NAMES
    freq = freq.sort_values()
    n_jobs = len(sub_detail)

    fig_detail = go.Figure(go.Bar(
        x=freq.values,
        y=freq.index,
        orientation="h",
        marker_color=[C_PRIMARY if v == freq.max() else C_LIGHT for v in freq.values],
        text=[f"{v} ({v/n_jobs*100:.0f}%)" for v in freq.values],
        textposition="outside",
    ))
    fig_detail.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6",
        xaxis_title="Jumlah lowongan", yaxis_title="",
        xaxis_range=[0, n_jobs * 1.25],
        margin=dict(t=20, b=10), height=280,
        title=f"Skill demand · {sel_detail} ({n_jobs} lowongan)",
    )
    st.plotly_chart(fig_detail, use_container_width=True)

    # ── Radar chart keseluruhan ──
    st.markdown("##### Radar: Profil Skill Tiap Job Title")
    radar_rows = []
    for title in all_titles:
        sub = job[job["job_title"] == title]
        n   = len(sub)
        for col, name in zip(SKILL_COLS, SKILL_NAMES):
            radar_rows.append({"job_title": title, "skill": name, "pct": sub[col].sum() / n * 100})
    radar_df = pd.DataFrame(radar_rows)

    fig_radar = go.Figure()
    colors_radar = [C_PRIMARY, C_GREEN, C_ORANGE, C_RED, C_DARK, "#a78bfa"]
    for i, title in enumerate(all_titles):
        d = radar_df[radar_df["job_title"] == title]
        fig_radar.add_trace(go.Scatterpolar(
            r=d["pct"].tolist() + [d["pct"].tolist()[0]],
            theta=d["skill"].tolist() + [d["skill"].tolist()[0]],
            fill="toself", name=title,
            line=dict(color=colors_radar[i % len(colors_radar)]),
            opacity=0.6,
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#333"), bgcolor="#0f1117"),
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6", showlegend=True,
        legend=dict(orientation="h", y=-0.1),
        height=440, margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong> <strong>Python</strong> adalah skill paling universal — diminta hampir di semua job title.
    <strong>SQL</strong> dominan di Data Analyst & Business Analyst. <strong>ML & Deep Learning</strong>
    terkonsentrasi di AI Engineer, ML Engineer, dan Data Scientist. <strong>Cloud</strong> menjadi
    pembeda utama antara job title senior vs junior.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# BQ3 · Distribusi matched_score kandidat
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-header">BQ3 · Seberapa Tinggi Matched Score Kandidat?</div>', unsafe_allow_html=True)
    st.markdown("Distribusi dan pola matched score kandidat terhadap lowongan DS/AI.")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Distribusi Matched Score (Histogram)")
        mean_score = cand_f["matched_score"].mean()
        median_score = cand_f["matched_score"].median()

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=cand_f["matched_score"].dropna(),
            nbinsx=40,
            marker_color=C_PRIMARY, opacity=0.85,
            name="Frekuensi",
        ))
        fig_hist.add_vline(x=mean_score, line_dash="dash", line_color=C_DARK,
                           annotation_text=f"Mean: {mean_score:.2f}", annotation_position="top right")
        fig_hist.add_vline(x=0.75, line_dash="dot", line_color=C_GREEN,
                           annotation_text="High Match (0.75)", annotation_position="top left")
        fig_hist.add_vline(x=0.50, line_dash="dot", line_color=C_ORANGE,
                           annotation_text="Mid Match (0.50)", annotation_position="bottom left")
        fig_hist.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6", showlegend=False,
            xaxis_title="Matched Score", yaxis_title="Frekuensi",
            margin=dict(t=20, b=10), height=320,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        st.markdown("##### Distribusi Match Category")
        cat_counts = cand_f["match_category"].value_counts()
        # Pastikan urutan konsisten
        order  = ["High Match", "Mid Match", "Low Match"]
        values = [cat_counts.get(c, 0) for c in order]

        fig_pie = go.Figure(go.Pie(
            labels=order, values=values,
            marker=dict(colors=[C_GREEN, C_ORANGE, C_RED]),
            hole=0.42,
            textinfo="label+percent",
            insidetextorientation="radial",
        ))
        fig_pie.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6", showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(t=20, b=10), height=320,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Box plot per job target ──
    st.markdown("##### Box Plot Matched Score per Job Target")
    top_jobs = cand_f["job_target"].value_counts().nlargest(8).index.tolist()
    box_df   = cand_f[cand_f["job_target"].isin(top_jobs)]
    fig_box  = px.box(
        box_df, x="matched_score", y="job_target",
        color="match_category",
        color_discrete_map={"High Match": C_GREEN, "Mid Match": C_ORANGE, "Low Match": C_RED},
        labels={"matched_score": "Matched Score", "job_target": ""},
    )
    fig_box.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6", margin=dict(t=20, b=10),
        height=360, legend_title="Kategori",
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # ── Summary stats ──
    st.markdown("##### Statistik Deskriptif Matched Score")
    stats = cand_f["matched_score"].describe().round(3)
    stats_df = pd.DataFrame({"Statistik": stats.index, "Nilai": stats.values})
    st.dataframe(stats_df, use_container_width=True, hide_index=True, height=280)

    st.markdown(f"""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Rata-rata matched score kandidat adalah <strong>{cand['matched_score'].mean():.2f}</strong>,
    dengan mayoritas masuk kategori <strong>Mid Match (50–75%)</strong>. Hanya sebagian kecil yang berhasil meraih
    High Match. Distribusi cenderung <em>right-skewed</em> — banyak kandidat berada di kisaran 0.55–0.75,
    menandakan potensi yang perlu ditingkatkan lewat pelatihan skill spesifik.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# BQ4 · Relevansi skill kandidat vs job DS/AI
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">BQ4 · Relevansi Skill Kandidat vs Skill yang Diminta Job DS/AI</div>', unsafe_allow_html=True)
    st.markdown("Seberapa relevan skill yang dimiliki kandidat dengan 5 skill utama yang diminta pasar?")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Distribusi Jumlah Skill Overlap (dari 5 skill)")
        overlap_dist = cand_f["overlap_with_job_skills"].value_counts().sort_index().reset_index()
        overlap_dist.columns = ["overlap", "jumlah_kandidat"]
        overlap_dist["overlap_label"] = overlap_dist["overlap"].astype(str) + " skill cocok"

        fig_ov_bar = px.bar(
            overlap_dist,
            x="overlap_label", y="jumlah_kandidat",
            color="overlap",
            color_continuous_scale="Teal",
            text="jumlah_kandidat",
        )
        fig_ov_bar.update_traces(textposition="outside")
        fig_ov_bar.update_layout(
            coloraxis_showscale=False, showlegend=False,
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6",
            xaxis_title="Jumlah Skill yang Cocok", yaxis_title="Jumlah Kandidat",
            margin=dict(t=20, b=10), height=320,
        )
        st.plotly_chart(fig_ov_bar, use_container_width=True)

    with col_b:
        st.markdown("##### Avg Matched Score vs Jumlah Skill Overlap")
        overlap_score = (
            cand_f.groupby("overlap_with_job_skills")["matched_score"]
            .agg(["mean", "count"]).reset_index()
        )
        overlap_score.columns = ["overlap", "avg_score", "count"]

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=overlap_score["overlap"],
            y=overlap_score["avg_score"],
            mode="lines+markers+text",
            marker=dict(size=10, color=C_PRIMARY),
            line=dict(width=2.5, color=C_PRIMARY),
            text=overlap_score["avg_score"].round(3).astype(str),
            textposition="top center",
            name="Avg Score",
        ))
        fig_line.add_hrect(y0=0.75, y1=1, fillcolor=C_GREEN, opacity=0.08, line_width=0)
        fig_line.add_hrect(y0=0.50, y1=0.75, fillcolor=C_ORANGE, opacity=0.08, line_width=0)
        fig_line.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6",
            xaxis_title="Jumlah Skill Overlap",
            yaxis_title="Rata-rata Matched Score",
            yaxis_range=[0, 1],
            xaxis=dict(tickmode="linear"),
            margin=dict(t=20, b=10), height=320,
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # ── Match category per overlap level ──
    st.markdown("##### Komposisi Match Category per Jumlah Skill Overlap")
    ov_cat = (
        cand_f.groupby(["overlap_with_job_skills", "match_category"])
        .size().reset_index(name="count")
    )
    ov_cat_pivot = ov_cat.pivot(index="overlap_with_job_skills", columns="match_category", values="count").fillna(0)
    # Normalise to percentage
    ov_cat_pct = ov_cat_pivot.div(ov_cat_pivot.sum(axis=1), axis=0) * 100

    fig_cat_stack = go.Figure()
    cat_colors = {"High Match": C_GREEN, "Mid Match": C_ORANGE, "Low Match": C_RED}
    for cat in ["High Match", "Mid Match", "Low Match"]:
        if cat in ov_cat_pct.columns:
            fig_cat_stack.add_trace(go.Bar(
                x=ov_cat_pct.index.astype(str),
                y=ov_cat_pct[cat],
                name=cat,
                marker_color=cat_colors.get(cat, C_LIGHT),
                text=ov_cat_pct[cat].round(1).astype(str) + "%",
                textposition="inside",
            ))
    fig_cat_stack.update_layout(
        barmode="stack",
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6",
        xaxis_title="Jumlah Skill Overlap",
        yaxis_title="% Kandidat",
        legend_title="Match Category",
        margin=dict(t=20, b=10), height=340,
    )
    st.plotly_chart(fig_cat_stack, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Terdapat korelasi positif yang jelas antara jumlah skill overlap dan matched score.
    Kandidat dengan <strong>3–4 skill cocok</strong> secara signifikan lebih banyak masuk kategori High Match.
    Namun mayoritas kandidat hanya memiliki <strong>1–2 skill</strong> yang relevan,
    menandakan gap pelatihan yang perlu ditangani — terutama di area ML, Deep Learning, dan Cloud.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# BQ5 · Gap Analysis: posisi KKNI vs kandidat
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-header">BQ5 · Gap Analysis: Posisi KKNI Tersedia vs Kandidat yang Relevan</div>', unsafe_allow_html=True)
    st.markdown("Level KKNI mana yang paling banyak posisinya di Pontik, tapi paling sedikit kandidatnya?")

    # Prepare gap dataframe
    KKNI_LABEL_MAP = {
        1: "Operator Pemula", 2: "Operator", 3: "Teknisi Junior",
        4: "Asisten Teknisi", 5: "Teknisi/Analis Muda",
        6: "Teknisi/Analis Madya", 7: "Ahli Pertama / Perdana",
        8: "Ahli Utama / Lead", 9: "Pemimpin / C-Level",
    }

    pontik_dist = pontik.groupby(["kkni_level", "kkni_label"]).size().reset_index(name="n_roles")

    cand_dist = (
        cand["kkni_level_inferred"].dropna().astype(int)
        .value_counts().reset_index()
    )
    cand_dist.columns = ["kkni_level", "n_candidates"]

    gap_df = pontik_dist.merge(cand_dist, on="kkni_level", how="left").fillna(0)
    gap_df["n_candidates"] = gap_df["n_candidates"].astype(int)
    gap_df["gap"] = gap_df["n_roles"] - gap_df["n_candidates"].clip(upper=gap_df["n_roles"])
    gap_df["gap_ratio"] = np.where(
        gap_df["n_candidates"] > 0,
        (gap_df["n_roles"] / gap_df["n_candidates"]).round(2),
        np.inf,
    )
    gap_df = gap_df.sort_values("kkni_level")

    # ── Grouped bar ──
    st.markdown("##### Jumlah Posisi (Pontik) vs Kandidat per Level KKNI")
    fig_gap = go.Figure()
    fig_gap.add_trace(go.Bar(
        name="Posisi Tersedia (Pontik)",
        x=gap_df["kkni_label"], y=gap_df["n_roles"],
        marker_color=C_PRIMARY, text=gap_df["n_roles"], textposition="outside",
    ))
    fig_gap.add_trace(go.Bar(
        name="Kandidat Relevan",
        x=gap_df["kkni_label"], y=gap_df["n_candidates"],
        marker_color=C_GREEN, text=gap_df["n_candidates"], textposition="outside",
    ))
    fig_gap.update_layout(
        barmode="group",
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6",
        xaxis=dict(tickangle=-20), xaxis_title="",
        yaxis_title="Jumlah",
        legend=dict(orientation="h", y=1.08),
        margin=dict(t=30, b=10), height=380,
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # ── Gap ratio bubble chart ──
        st.markdown("##### Gap Ratio per Level KKNI")
        gap_plot = gap_df[gap_df["gap_ratio"] != np.inf].copy()
        fig_bubble = px.scatter(
            gap_plot,
            x="kkni_label",
            y="gap_ratio",
            size="n_roles",
            color="gap_ratio",
            color_continuous_scale="RdYlGn_r",
            text="gap_ratio",
            labels={"gap_ratio": "Rasio (Posisi/Kandidat)", "kkni_label": ""},
            size_max=50,
        )
        fig_bubble.update_traces(textposition="top center")
        fig_bubble.add_hline(y=1, line_dash="dot", line_color="white",
                              annotation_text="Seimbang (1:1)", annotation_position="top right")
        fig_bubble.update_layout(
            plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
            font_color="#e6e6e6",
            xaxis=dict(tickangle=-20),
            coloraxis_showscale=False,
            margin=dict(t=20, b=10), height=340,
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_b:
        # ── Tabel gap ──
        st.markdown("##### Tabel Ringkasan Gap")
        gap_show = gap_df[["kkni_label", "kkni_level", "n_roles", "n_candidates", "gap_ratio"]].copy()
        gap_show.columns = ["Level KKNI", "Level", "Posisi Pontik", "Kandidat", "Gap Ratio"]
        gap_show["Gap Ratio"] = gap_show["Gap Ratio"].replace(np.inf, "∞")
        st.dataframe(
            gap_show.reset_index(drop=True),
            use_container_width=True, hide_index=True, height=340,
        )

    # ── Waterfall ──
    st.markdown("##### Surplus / Deficit Kandidat per Level KKNI")
    gap_df["surplus"] = gap_df["n_candidates"] - gap_df["n_roles"]
    colors_wf = [C_GREEN if v >= 0 else C_RED for v in gap_df["surplus"]]

    fig_wf = go.Figure(go.Bar(
        x=gap_df["kkni_label"],
        y=gap_df["surplus"],
        marker_color=colors_wf,
        text=gap_df["surplus"].apply(lambda v: f"+{v}" if v >= 0 else str(v)),
        textposition="outside",
    ))
    fig_wf.add_hline(y=0, line_color="white", line_width=1)
    fig_wf.update_layout(
        plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
        font_color="#e6e6e6",
        xaxis=dict(tickangle=-20), xaxis_title="",
        yaxis_title="Surplus (+) / Deficit (−) Kandidat",
        margin=dict(t=20, b=10), height=320,
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <strong>Insight:</strong> Level <strong>Ahli Pertama / Perdana (KKNI 7)</strong> dan
    <strong>Ahli Utama / Lead (KKNI 8)</strong> menunjukkan gap terbesar — banyak posisi tersedia di Pontik
    tapi sedikit kandidat yang kualifikasinya sesuai. Sebaliknya, level <strong>Teknisi/Analis Muda (KKNI 5)</strong>
    memiliki surplus kandidat yang cukup tinggi. Ini menunjukkan bahwa industri membutuhkan lebih banyak
    <strong>upskilling kandidat junior</strong> menuju level menengah-senior.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#555; font-size:0.8rem;'>"
    "DS/AI Job Market Dashboard · Data: job_clean · pontik_enriched · resume_candidate_clean · resume_job_req_clean"
    "</div>",
    unsafe_allow_html=True,
)
