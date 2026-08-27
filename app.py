"""
app.py - The Compass of Human Perspectives
Presentation & GUI Layer
"""

import os
import sys
import json
import urllib.parse
from io import BytesIO

# Ensure current working directory is on Python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw

# ==============================================================================
# 1. ARCHITECTURAL DATA & ENGINE IMPORTS
# ==============================================================================
from database import WORLDVIEWS, load_questions_dataset
from engine import (
    calculate_coordinates_direct,
    calculate_affinities,
    characterize_profile,
    check_tensions,
)

st.set_page_config(
    page_title="The Compass of Human Perspectives",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. 25-DIMENSION CATEGORY LIGHTING PALETTES
# ==============================================================================
DIMENSION_TINTS = {
    0:  {"dark": "rgba(14, 165, 233, 0.12)", "light": "#EBF5FB"},
    1:  {"dark": "rgba(168, 85, 247, 0.12)", "light": "#F5EEFB"},
    2:  {"dark": "rgba(20, 184, 166, 0.12)", "light": "#EBF7F5"},
    3:  {"dark": "rgba(16, 185, 129, 0.12)", "light": "#EBF7F0"},
    4:  {"dark": "rgba(217, 119, 6, 0.12)",  "light": "#FAF3E6"},
    5:  {"dark": "rgba(124, 58, 237, 0.12)", "light": "#F2ECFA"},
    6:  {"dark": "rgba(244, 63, 94, 0.12)",  "light": "#FBECF0"},
    7:  {"dark": "rgba(59, 130, 246, 0.12)", "light": "#EBF2FB"},
    8:  {"dark": "rgba(6, 182, 212, 0.12)",  "light": "#EAF5F7"},
    9:  {"dark": "rgba(234, 88, 12, 0.12)",  "light": "#FAEDE6"},
    10: {"dark": "rgba(139, 92, 246, 0.12)", "light": "#F1ECFA"},
    11: {"dark": "rgba(22, 163, 74, 0.12)",  "light": "#EBF5ED"},
    12: {"dark": "rgba(34, 197, 94, 0.12)",  "light": "#EEF6F0"},
    13: {"dark": "rgba(29, 78, 216, 0.12)",  "light": "#EAF0FA"},
    14: {"dark": "rgba(146, 64, 14, 0.12)",  "light": "#F6EFEA"},
    15: {"dark": "rgba(225, 29, 72, 0.12)",  "light": "#FAECF0"},
    16: {"dark": "rgba(101, 163, 13, 0.12)", "light": "#F0F6EA"},
    17: {"dark": "rgba(180, 83, 9, 0.12)",   "light": "#F7EFE8"},
    18: {"dark": "rgba(220, 38, 38, 0.12)",  "light": "#FBEDED"},
    19: {"dark": "rgba(30, 58, 138, 0.12)",  "light": "#EAEFF6"},
    20: {"dark": "rgba(16, 185, 129, 0.12)", "light": "#EBF7F1"},
    21: {"dark": "rgba(20, 184, 166, 0.12)", "light": "#EAF6F5"},
    22: {"dark": "rgba(124, 58, 237, 0.12)", "light": "#F2ECFA"},
    23: {"dark": "rgba(6, 182, 212, 0.12)",  "light": "#EAF5F7"},
    24: {"dark": "rgba(249, 115, 22, 0.12)", "light": "#FAF0E8"}
}

# ==============================================================================
# 3. RESPONSIVE GLASSMORPHISM & METALLIC BORDER CSS
# ==============================================================================
def inject_custom_theme(theme: str = "Dark", dim_idx: int = 0):
    tint_mode = "dark" if theme.lower() == "dark" else "light"
    active_tint = DIMENSION_TINTS.get(dim_idx, {}).get(tint_mode, "transparent")

    if theme.lower() == "light":
        palette = {
            "bg_base": "#F7F5F0",
            "text_primary": "#1E293B",
            "text_secondary": "#475569",
            "accent_gold": "#9A722C",
            "glass_tile_bg": "rgba(255, 255, 255, 0.65)",
            "glass_tile_border": "rgba(154, 114, 44, 0.22)",
            "glass_tile_hover": "rgba(154, 114, 44, 0.55)",
            "glass_selected_bg": "rgba(154, 114, 44, 0.14)",
            "badge_bg": "#EFECE4",
            "badge_text": "#785B24",
            "border_outer": "#9A722C",
            "border_inner": "#CBD5E1"
        }
    else:
        palette = {
            "bg_base": "#14181F",
            "text_primary": "#E4E8EE",
            "text_secondary": "#94A3B8",
            "accent_gold": "#D4AF37",
            "glass_tile_bg": "rgba(36, 41, 50, 0.60)",
            "glass_tile_border": "rgba(212, 175, 55, 0.22)",
            "glass_tile_hover": "rgba(212, 175, 55, 0.65)",
            "glass_selected_bg": "rgba(212, 175, 55, 0.16)",
            "badge_bg": "#1C2129",
            "badge_text": "#D4AF37",
            "border_outer": "#D4AF37",
            "border_inner": "#94A3B8"
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Devanagari:wght@400;600;700&display=swap');

    /* Viewport Frame with Outer Gold & Inner Silver Borders */
    .stApp {{
        background-color: {palette['bg_base']} !important;
        background-image: radial-gradient(circle at 50% 12%, {active_tint} 0%, transparent 75%) !important;
        background-attachment: fixed;
        color: {palette['text_primary']} !important;
        font-family: 'Inter', sans-serif !important;
        box-sizing: border-box;
        border: 4px solid {palette['border_outer']} !important;
        outline: 2px solid {palette['border_inner']} !important;
        outline-offset: -10px;
        padding: 18px 24px !important;
        min-height: 100vh;
    }}

    @media (max-width: 768px) {{
        .stApp {{
            border: 2.5px solid {palette['border_outer']} !important;
            outline: 1.5px solid {palette['border_inner']} !important;
            outline-offset: -5px;
            padding: 10px 12px !important;
        }}
    }}

    .cinzel-title {{
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.04em;
        line-height: 1.3;
        color: {palette['accent_gold']} !important;
    }}

    .serif-quote {{
        font-family: 'Lora', 'Noto Serif Devanagari', serif !important;
        font-style: italic;
    }}

    /* Category Pill Badge */
    .category-badge {{
        display: inline-block;
        padding: 5px 14px;
        background: {palette['badge_bg']};
        color: {palette['badge_text']};
        border-radius: 20px;
        font-size: 0.80rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
        border: 1px solid {palette['glass_tile_border']};
    }}

    /* Glassmorphic Option Tiles */
    div[data-testid="stButton"] > button {{
        background: {palette['glass_tile_bg']} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1.5px solid {palette['glass_tile_border']} !important;
        border-radius: 14px !important;
        padding: 18px 22px !important;
        color: {palette['text_primary']} !important;
        text-align: left !important;
        justify-content: flex-start !important;
        min-height: 72px !important;
        white-space: normal !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        border-color: {palette['glass_tile_hover']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.20), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }}

    div[data-testid="stButton"] > button[kind="primary"] {{
        background: {palette['glass_selected_bg']} !important;
        border-color: {palette['accent_gold']} !important;
        box-shadow: 0 0 0 1px {palette['accent_gold']}, 0 10px 25px rgba(0, 0, 0, 0.25) !important;
    }}

    .tension-card {{
        padding: 20px 24px !important;
        background: {palette['glass_tile_bg']} !important;
        backdrop-filter: blur(12px) !important;
        border-left: 4px solid {palette['accent_gold']} !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        border-top: 1px solid {palette['glass_tile_border']} !important;
        border-right: 1px solid {palette['glass_tile_border']} !important;
        border-bottom: 1px solid {palette['glass_tile_border']} !important;
    }}

    .social-btn {{
        display: inline-block;
        padding: 10px 18px;
        border-radius: 8px;
        background: {palette['glass_tile_bg']};
        color: {palette['text_primary']} !important;
        border: 1px solid {palette['glass_tile_border']};
        text-decoration: none;
        font-weight: 500;
        font-size: 0.90rem;
        transition: all 0.2s ease;
    }}
    .social-btn:hover {{
        border-color: {palette['accent_gold']};
        transform: translateY(-2px);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. LOCALIZATION DICTIONARY
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an intellectually serious exploration of human thought. Across 25 or 100 questions, discover the structural architecture of your worldview and measure your affinities to major global traditions.",
        "quick_test": "Quick Odyssey (25 Questions)",
        "full_test": "Full Odyssey (100 Questions)",
        "start_quick": "Start Quick Odyssey (25 Questions)",
        "start_full": "Start Full Odyssey (100 Questions)",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "retake_btn": "Retake Odyssey ↺",
        "char_title": "🧭 Diagnostic Dimensions",
        "affinities_label": "🏛️ Major Historical Lineages",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal consistency.",
        "comparison_title": "🔬 Compare With Historical Traditions",
        "confidence_title": "🔍 Epistemic Conviction Calibration",
        "confidence_sub": "Calibrate your intellectual certainty versus your openness to revised evidence:",
        "confidence_low": "Humility (Hold views provisionally)",
        "confidence_high": "Certainty (Hold absolute truths)",
        "share_heading": "📢 Share Your Profile & Identity Card",
        "share_sub": "Share your cognitive identity dossier or permalink with peers:",
        "passport_btn": "Download Official HD Identity Card (PNG) 🎫"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज पर निकलें। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें और प्रमुख वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "quick_test": "त्वरित यात्रा (25 प्रश्न)",
        "full_test": "पूर्ण यात्रा (100 प्रश्न)",
        "start_quick": "त्वरित यात्रा शुरू करें (25 प्रश्न)",
        "start_full": "पूर्ण यात्रा शुरू करें (100 प्रश्न)",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "retake_btn": "पुनः आरंभ करें ↺",
        "char_title": "🧭 प्रोफ़ाइल नैदानिक आयाम",
        "affinities_label": "🏛️ प्रमुख ऐतिहासिक दार्शनिक परंपराएं",
        "challenge_title": "⚡ संज्ञानात्मक तनाव (Cognitive Tensions)",
        "no_tensions": "🟢 कोई संरचनात्मक तनाव नहीं पाया गया। आपका विश्वदृष्टिकोण उच्च विषयगत निरंतरता प्रदर्शित करता है।",
        "comparison_title": "🔬 परंपराओं के साथ तुलना",
        "confidence_title": "🔍 बौद्धिक आत्मविश्वास और विश्वास की गहराई",
        "confidence_sub": "नए साक्ष्यों के आधार पर विचार बदलने की अपनी तत्परता का स्तर निर्धारित करें:",
        "confidence_low": "बौद्धिक विनम्रता (संशोधन के लिए तैयार)",
        "confidence_high": "पूर्ण निश्चितता (अटल विश्वास)",
        "share_heading": "📢 अपनी प्रोफ़ाइल और पहचान पत्र साझा करें",
        "share_sub": "अपना डिजिटल पहचान पत्र या लिंक दूसरों के साथ साझा करें:",
        "passport_btn": "आधिकारिक HD पहचान पत्र (PNG) डाउनलोड करें 🎫"
    }
}

# ==============================================================================
# 5. EXPANDED HD DOSSIER CARD GENERATOR (PIL)
# ==============================================================================
def generate_hd_passport(user_coords, top_affinity, character_tags, language="English"):
    """Generates an 800x1250 HD Philosophical Dossier Identity Card with summaries."""
    w, h = 800, 1250
    img = Image.new("RGB", (w, h), (20, 24, 31))
    draw = ImageDraw.Draw(img)

    # Double Border Frame: Outer Gold, Inner Silver
    draw.rectangle([20, 20, w - 20, h - 20], outline=(212, 175, 55), width=3)
    draw.rectangle([30, 30, w - 30, h - 30], outline=(148, 163, 184), width=1)
    
    for cx, cy in [(20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)]:
        draw.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=(212, 175, 55))

    # Header Titles
    draw.text((w // 2, 65), "THE COMPASS OF HUMAN PERSPECTIVES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 92), "PHILOSOPHICAL COGNITIVE DOSSIER", fill=(148, 163, 184), anchor="mm")

    # Primary Worldview Box
    draw.rounded_rectangle([50, 130, w - 50, 245], radius=10, fill=(30, 36, 46), outline=(212, 175, 55), width=1)
    draw.text((w // 2, 168), top_affinity["name"].upper(), fill=(248, 250, 252), anchor="mm")
    draw.text((w // 2, 205), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(56, 189, 248), anchor="mm")

    # Short Core Description
    desc = top_affinity.get("description", "")
    lines = [desc[i:i+68] for i in range(0, len(desc), 68)][:3]
    for idx, l in enumerate(lines):
        draw.text((w // 2, 275 + (idx * 22)), l.strip(), fill=(203, 213, 225), anchor="mm")

    # 4D Vector Sliders
    labels = [
        ("Transcendence (+) vs Physicalism (-)", user_coords[0]),
        ("Collectivism (+) vs Individualism (-)", user_coords[1]),
        ("Progressivism (+) vs Traditionalism (-)", user_coords[2]),
        ("Empiricism (+) vs Rationalism (-)", user_coords[3])
    ]
    
    start_y = 390
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 90)
        draw.text((60, y), lbl, fill=(226, 232, 240))
        draw.text((740, y), f"{val:+.2f}", fill=(212, 175, 55), anchor="ra")
        draw.rounded_rectangle([60, y + 25, 740, y + 40], radius=7, fill=(45, 55, 72))
        norm_x = 60 + int(((val + 1.0) / 2.0) * 680)
        draw.rounded_rectangle([60, y + 25, max(75, norm_x), y + 40], radius=7, fill=(212, 175, 55))

    # Diagnostic Profile Attributes
    draw.text((w // 2, 800), "PROFILE ATTRIBUTES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 835), " • ".join(character_tags), fill=(248, 250, 252), anchor="mm")

    # Canonical Lineage Thinkers
    thinkers_str = ", ".join(top_affinity.get("thinkers", [])[:3])
    draw.text((w // 2, 900), f"CANONICAL THINKERS: {thinkers_str}", fill=(148, 163, 184), anchor="mm")

    # Verification Simulation Barcode
    for bx in range(80, 720, 10):
        stroke = 3 if (bx % 20 == 0) else 1
        draw.line([(bx, 1050), (bx, 1100)], fill=(212, 175, 55), width=stroke)

    draw.text((w // 2, 1190), "VERIFIED COGNITIVE IDENTITY SPECIFICATION", fill=(100, 116, 139), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# 6. DUAL VECTOR VISUALIZERS (3D + RADAR)
# ==============================================================================
def render_3d_scatter(user_coords, worldviews_dict):
    fig = go.Figure()
    wv_names, wv_x, wv_y, wv_z, wv_desc = [], [], [], [], []
    for name, data in worldviews_dict.items():
        wv_names.append(name)
        wv_x.append(data["vector"][0])
        wv_y.append(data["vector"][1])
        wv_z.append(data["vector"][2])
        wv_desc.append(data.get("description", ""))
        
    fig.add_trace(go.Scatter3d(
        x=wv_x, y=wv_y, z=wv_z,
        mode='markers+text',
        text=wv_names,
        textposition="top center",
        hoverinfo="text+name",
        hovertext=wv_desc,
        name="Schools of Thought",
        marker=dict(size=6, color='#38BDF8', opacity=0.8, line=dict(color='rgba(255,255,255,0.2)', width=1)),
        textfont=dict(color='#CBD5E1', size=9)
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[user_coords[0]], y=[user_coords[1]], z=[user_coords[2]],
        mode='markers+text',
        text=["YOU"],
        textposition="top center",
        name="Your Position",
        marker=dict(size=12, color='#D4AF37', opacity=1.0, symbol='diamond', line=dict(color='#FFFFFF', width=2)),
        textfont=dict(color='#FFFFFF', size=14, family='Cinzel')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, b=0, t=30),
        scene=dict(
            xaxis=dict(title='Transcendence (D0)', backgroundcolor='#14181F', color='#808D9E', showbackground=True),
            yaxis=dict(title='Collectivism (D1)', backgroundcolor='#14181F', color='#808D9E', showbackground=True),
            zaxis=dict(title='Progressivism (D2)', backgroundcolor='#14181F', color='#808D9E', showbackground=True),
        ),
        legend=dict(x=0, y=1, bgcolor='rgba(20,24,31,0.8)')
    )
    return fig

def render_radar_comparison(user_coords, match_coords, match_name):
    categories = ['Transcendence (D0)', 'Collectivism (D1)', 'Progressivism (D2)', 'Empiricism (D3)']
    user_scaled = [((v + 1.0) / 2.0) * 100.0 for v in user_coords]
    match_scaled = [((v + 1.0) / 2.0) * 100.0 for v in match_coords]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_scaled + [user_scaled[0]], theta=categories + [categories[0]],
        fill='toself', name='Your Coordinates', line_color='#D4AF37'
    ))
    fig.add_trace(go.Scatterpolar(
        r=match_scaled + [match_scaled[0]], theta=categories + [categories[0]],
        fill='toself', name=match_name, line_color='#38BDF8', opacity=0.5
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#808D9E"),
            bgcolor="rgba(30, 36, 46, 0.4)"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(color="#E4E8EE")
    )
    return fig

# ==============================================================================
# 7. STATE SYNCHRONIZATION & REFRESH RECOVERY
# ==============================================================================
def sync_state_to_url():
    """Writes the current progress state to the URL query string."""
    try:
        st.query_params["started"] = "true" if st.session_state.started else "false"
        st.query_params["completed"] = "true" if st.session_state.completed else "false"
        st.query_params["test_type"] = st.session_state.test_type
        st.query_params["q_idx"] = str(st.session_state.current_question_index)
        st.query_params["lang"] = st.session_state.language
        st.query_params["theme"] = st.session_state.theme
        st.query_params["answers"] = urllib.parse.quote(json.dumps(st.session_state.answers))
    except Exception:
        pass

def restore_state_from_url():
    """Rehydrates session state if the page is refreshed or loaded via URL."""
    try:
        params = st.query_params
        if "started" in params:
            st.session_state.started = (params["started"].lower() == "true")
        if "completed" in params:
            st.session_state.completed = (params["completed"].lower() == "true")
        if "test_type" in params:
            st.session_state.test_type = params["test_type"]
        if "q_idx" in params:
            st.session_state.current_question_index = int(params["q_idx"])
        if "lang" in params and params["lang"] in ["English", "Hindi"]:
            st.session_state.language = params["lang"]
        if "theme" in params and params["theme"] in ["Dark", "Light"]:
            st.session_state.theme = params["theme"]
        if "answers" in params:
            st.session_state.answers = json.loads(urllib.parse.unquote(params["answers"]))
    except Exception:
        pass

# Initialize State Keys
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "test_type" not in st.session_state:
    st.session_state.test_type = "Quick"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "started" not in st.session_state:
    st.session_state.started = False
if "completed" not in st.session_state:
    st.session_state.completed = False

if "url_rehydrated" not in st.session_state:
    restore_state_from_url()
    st.session_state.url_rehydrated = True

# Load Dynamic Questions
raw_questions = load_questions_dataset(mode=st.session_state.test_type.lower())
active_dim_idx = 0
if st.session_state.started and not st.session_state.completed and raw_questions:
    if st.session_state.current_question_index < len(raw_questions):
        active_dim_idx = raw_questions[st.session_state.current_question_index].get("dimIndex", 0)

inject_custom_theme(st.session_state.theme, active_dim_idx)
ui = UI_TEXT[st.session_state.language]
is_hindi = (st.session_state.language == "Hindi")

# ==============================================================================
# 8. TOP NAVIGATION BAR (WITH HYPERLINKED HOME LOGO)
# ==============================================================================
c1, c2, c3 = st.columns([6.5, 2.0, 1.5])
with c1:
    # Hyperlinked Logo to Return Home
    if st.button("🧭 THE COMPASS OF HUMAN PERSPECTIVES", key="home_brand_link"):
        st.session_state.started = False
        st.session_state.completed = False
        st.session_state.current_question_index = 0
        st.session_state.answers = {}
        sync_state_to_url()
        st.rerun()

with c2:
    lang = st.selectbox("Language / भाषा", ["English", "Hindi"], index=0 if not is_hindi else 1, label_visibility="collapsed")
    if lang != st.session_state.language:
        st.session_state.language = lang
        sync_state_to_url()
        st.rerun()

with c3:
    thm = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, label_visibility="collapsed")
    if thm != st.session_state.theme:
        st.session_state.theme = thm
        sync_state_to_url()
        st.rerun()

st.write("---")

# ==============================================================================
# VIEW 1: LANDING PAGE
# ==============================================================================
if not st.session_state.started and not st.session_state.completed:
    st.markdown(f"""
    <div style='text-align: center; padding: 30px 20px;'>
        <h1 class='cinzel-title' style='font-size: 2.8rem;'>{ui['title']}</h1>
        <p class='serif-quote' style='font-size: 1.35rem; color: #A0AEC0;'>“{ui['subtitle']}”</p>
        <p style='max-width: 760px; margin: 20px auto; font-size: 1.1rem; line-height: 1.7;'>{ui['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        st.info(f"**{ui['quick_test']}**\n\n25 questions (1 per core dimension) for a concise diagnostic.")
        if st.button(ui["start_quick"], use_container_width=True, type="primary"):
            st.session_state.test_type = "Quick"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            sync_state_to_url()
            st.rerun()
    with b2:
        st.info(f"**{ui['full_test']}**\n\n100 questions (4 per core dimension) for maximum diagnostic precision.")
        if st.button(ui["start_full"], use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            sync_state_to_url()
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTIONNAIRE (INSTANT AUTO-ADVANCE TILES & RECOVERY)
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    st.progress((idx + 1) / total_q)
    dim_name = q.get('dimension_hi' if is_hindi else 'dimension', q.get('dimension', ''))
    
    st.markdown(f"<div class='category-badge'>DIMENSION: {dim_name.upper()}</div>", unsafe_allow_html=True)
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q))

    q_text = q['text_hi'] if is_hindi and q.get('text_hi') else q['text_en']
    st.markdown(f"<h3 style='margin: 12px 0 22px 0; line-height: 1.4;'>{q_text}</h3>", unsafe_allow_html=True)

    current_choice = st.session_state.answers.get(q["id"], None)

    # Click-to-Auto-Advance Tiles
    for opt in q["options"]:
        opt_code = opt["code"]
        opt_text = opt['text_hi'] if is_hindi and opt.get('text_hi') else opt['text_en']
        is_selected = (current_choice == opt_code)
        
        tile_label = f"[{opt_code}]  {opt_text}"
        if st.button(
            tile_label,
            key=f"opt_tile_{q['id']}_{opt_code}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            # Record choice
            st.session_state.answers[q["id"]] = opt_code
            
            # Auto-advance immediately
            if idx < total_q - 1:
                st.session_state.current_question_index += 1
            else:
                st.session_state.completed = True
            
            sync_state_to_url()
            st.rerun()

    # Nav Row (Previous Step Control)
    st.write("")
    nav1, _, _ = st.columns([2, 6, 2])
    with nav1:
        if idx > 0 and st.button(ui["prev_btn"], use_container_width=True):
            st.session_state.current_question_index -= 1
            sync_state_to_url()
            st.rerun()

# ==============================================================================
# VIEW 3: PROFILE REVEAL & SOCIAL SHARE HUB
# ==============================================================================
elif st.session_state.completed:
    user_coords = calculate_coordinates_direct(st.session_state.answers, raw_questions, st.session_state.test_type)
    affinities = calculate_affinities(user_coords, WORLDVIEWS)
    tags = characterize_profile(user_coords, st.session_state.language)
    tensions = check_tensions(st.session_state.answers, st.session_state.language)
    top_match = affinities[0]

    title = top_match['name_hi'] if is_hindi else top_match['name']
    desc = top_match['description_hi'] if is_hindi else top_match['description']

    st.markdown(f"""
    <div style='text-align: center; padding: 20px 10px;'>
        <h1 class='cinzel-title' style='font-size: 2.6rem;'>{title}</h1>
        <p class='serif-quote' style='font-size: 1.3rem; color: #D4AF37;'>{top_match['similarity_pct']}% Match Affinity</p>
        <p style='max-width: 800px; margin: 15px auto; font-size: 1.05rem; line-height: 1.6;'>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    r1, r2 = st.columns([5, 5])
    with r1:
        st.markdown(f"### {ui['char_title']}")
        for t in tags:
            st.markdown(f"- **{t}**")
        st.write("")
        st.markdown(f"**Key Thinkers:** {', '.join(top_match.get('thinkers', []))}")
        st.markdown(f"**4D Coordinates:** `D0: {user_coords[0]}, D1: {user_coords[1]}, D2: {user_coords[2]}, D3: {user_coords[3]}`")
    with r2:
        tab1, tab2 = st.tabs(["3D Vector Map", "Radar Comparison"])
        with tab1:
            st.plotly_chart(render_3d_scatter(user_coords, WORLDVIEWS), use_container_width=True)
        with tab2:
            st.plotly_chart(render_radar_comparison(user_coords, top_match["vector"], top_match["name"]), use_container_width=True)

    # Tradition Comparison Tool
    st.write("---")
    st.markdown(f"### {ui['comparison_title']}")
    comp_school = st.selectbox("Select a tradition to compare:", list(WORLDVIEWS.keys()), index=0)
    if comp_school:
        comp_data = WORLDVIEWS[comp_school]
        c_col1, c_col2 = st.columns([6, 4])
        with c_col1:
            st.plotly_chart(render_radar_comparison(user_coords, comp_data["vector"], comp_school), use_container_width=True)
        with c_col2:
            st.markdown(f"**{comp_school}**")
            st.write(comp_data.get("description", ""))
            st.markdown(f"**Thinkers:** {', '.join(comp_data.get('thinkers', []))}")

    # Affinities Grid
    st.write("---")
    st.markdown(f"### {ui['affinities_label']}")
    aff_cols = st.columns(3)
    for i, aff in enumerate(affinities[1:7]):
        with aff_cols[i % 3]:
            nm = aff["name_hi"] if is_hindi else aff["name"]
            st.metric(label=nm, value=f"{aff['similarity_pct']}%")

    # Cognitive Tensions
    st.write("---")
    st.markdown(f"### {ui['challenge_title']}")
    if tensions:
        for t in tensions:
            st.markdown(f"""
            <div class='tension-card'>
                <div style='font-weight:700; color:#D4AF37; margin-bottom:6px;'>{t['title']}</div>
                <div style='line-height:1.6;'>{t['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(ui["no_tensions"])

    # Epistemic Conviction Slider
    st.write("---")
    st.markdown(f"### {ui['confidence_title']}")
    st.caption(ui["confidence_sub"])
    st.slider(
        "Epistemic Confidence Slider",
        min_value=0, max_value=100, value=50, step=5,
        label_visibility="collapsed"
    )
    st.markdown(f"""
    <div style='display: flex; justify-content: space-between; font-size: 0.85rem; color: #808D9E; margin-top: -10px;'>
        <span>👈 {ui['confidence_low']}</span>
        <span>{ui['confidence_high']} 👉</span>
    </div>
    """, unsafe_allow_html=True)

    # Social Sharing Hub & HD Identity Card
    st.write("---")
    st.markdown(f"### {ui['share_heading']}")
    st.caption(ui["share_sub"])

    passport_bytes = generate_hd_passport(user_coords, top_match, tags, st.session_state.language)
    share_msg = f"I took The Compass of Human Perspectives test and matched {top_match['similarity_pct']}% with {top_match['name']}! Discover your philosophical profile here:"
    encoded_share_msg = urllib.parse.quote(share_msg)

    x_url = f"https://twitter.com/intent/tweet?text={encoded_share_msg}"
    wa_url = f"https://api.whatsapp.com/send?text={encoded_share_msg}"
    li_url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://share.streamlit.io"

    st.markdown(f"""
    <div style='display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;'>
        <a href='{x_url}' target='_blank' class='social-btn'>Share on X (Twitter) 🐦</a>
        <a href='{wa_url}' target='_blank' class='social-btn'>Share on WhatsApp 💬</a>
        <a href='{li_url}' target='_blank' class='social-btn'>Share on LinkedIn 💼</a>
    </div>
    """, unsafe_allow_html=True)

    d1, d2 = st.columns([6, 4])
    with d1:
        st.download_button(
            label=ui["passport_btn"],
            data=passport_bytes,
            file_name=f"philosophical_identity_card_{top_match.get('slug', 'result')}.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )
    with d2:
        if st.button(ui["retake_btn"], use_container_width=True):
            st.session_state.completed = False
            st.session_state.started = False
            st.session_state.answers = {}
            st.session_state.current_question_index = 0
            sync_state_to_url()
            st.rerun()