"""
app.py - The Compass of Human Perspectives
Complete Presentation & GUI Layer:
- Dual-theme support: Slate Charcoal / Alabaster Off-White
- Dimension-aware ambient viewport lighting
- Interactive option cards with hover elevation
- Dual-view vector engine (3D Scatter & Radar Chart)
- Side-by-side tradition comparison tool
- Epistemic confidence calibration slider
- Multi-channel social share hub & PIL HD passport synthesis
"""

import os
import sys
import json
import urllib.parse
from io import BytesIO

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
    0:  {"dark": "rgba(14, 165, 233, 0.10)", "light": "#EDF5FA"},   # Metaphysics & Reality
    1:  {"dark": "rgba(168, 85, 247, 0.10)", "light": "#F5EFFB"},   # Consciousness & Mind
    2:  {"dark": "rgba(20, 184, 166, 0.10)", "light": "#EDF8F6"},   # Epistemology & Knowledge
    3:  {"dark": "rgba(16, 185, 129, 0.10)", "light": "#ECF8F2"},   # Truth & Realism
    4:  {"dark": "rgba(217, 119, 6, 0.10)",  "light": "#FAF4E8"},   # Religion & Sacredness
    5:  {"dark": "rgba(124, 58, 237, 0.10)", "light": "#F3EEFA"},   # Death & Finitude
    6:  {"dark": "rgba(244, 63, 94, 0.10)",  "light": "#FCEEF0"},   # Purpose & Meaning
    7:  {"dark": "rgba(59, 130, 246, 0.10)", "light": "#EDF3FC"},   # Ethics & Meta-Ethics
    8:  {"dark": "rgba(6, 182, 212, 0.10)",  "light": "#EBF6F8"},   # Moral Action & Practical Virtue
    9:  {"dark": "rgba(234, 88, 12, 0.10)",  "light": "#FAF0EB"},   # Human Nature & Destiny
    10: {"dark": "rgba(139, 92, 246, 0.10)", "light": "#F2EEFA"},   # Self & Identity
    11: {"dark": "rgba(22, 163, 74, 0.10)",  "light": "#ECF6EE"},   # Free Will & Agency
    12: {"dark": "rgba(34, 197, 94, 0.10)",  "light": "#EFF7F1"},   # Society & Community
    13: {"dark": "rgba(29, 78, 216, 0.10)",  "light": "#EBF1FA"},   # Liberty & Governance
    14: {"dark": "rgba(146, 64, 14, 0.10)",  "light": "#F7F1EB"},   # Authority & Institutional Order
    15: {"dark": "rgba(225, 29, 72, 0.10)",  "light": "#FBEFF2"},   # Equality & Hierarchy
    16: {"dark": "rgba(101, 163, 13, 0.10)", "light": "#F2F7EB"},   # Economics & Distribution
    17: {"dark": "rgba(180, 83, 9, 0.10)",   "light": "#F8F1EA"},   # Culture & Tradition
    18: {"dark": "rgba(220, 38, 38, 0.10)",  "light": "#FCEFEF"},   # Political Change
    19: {"dark": "rgba(30, 58, 138, 0.10)",  "light": "#ECEFF7"},   # Global Scope & Loyalty
    20: {"dark": "rgba(16, 185, 129, 0.10)", "light": "#ECF8F3"},   # Ecology & Environment
    21: {"dark": "rgba(20, 184, 166, 0.10)", "light": "#EBF7F6"},   # Animal Ethics & Sentience
    22: {"dark": "rgba(124, 58, 237, 0.10)", "light": "#F3EEFA"},   # Technology & AI
    23: {"dark": "rgba(6, 182, 212, 0.10)",  "light": "#EBF6F8"},   # Civilizational Future
    24: {"dark": "rgba(249, 115, 22, 0.10)", "light": "#FAF1EB"}    # Pluralism & Openness
}

# ==============================================================================
# 3. LUXURY EDITORIAL CSS INJECTOR
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
            "card_bg": "#FFFFFF",
            "card_border": "#E2DCD2",
            "card_hover_border": "#9A722C",
            "card_checked_bg": "#F4EDE1",
            "card_checked_border": "#9A722C",
            "badge_bg": "#EFECE4",
            "badge_text": "#785B24",
            "shadow": "rgba(154, 114, 44, 0.08)"
        }
    else:
        palette = {
            "bg_base": "#1A1E24",
            "text_primary": "#E4E8EE",
            "text_secondary": "#94A3B8",
            "accent_gold": "#D4AF37",
            "tile_bg": "#242932",
            "tile_border": "#353D4A",
            "tile_hover_border": "#D4AF37",
            "tile_selected_bg": "#2E3642",
            "tile_selected_border": "#D4AF37",
            "card_bg": "#242932",
            "card_border": "#353D4A",
            "badge_bg": "#1C2129",
            "badge_text": "#D4AF37",
            "shadow": "rgba(0, 0, 0, 0.25)"
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Devanagari:wght@400;600;700&display=swap');

    .stApp {{
        background-color: {palette['bg_base']} !important;
        background-image: radial-gradient(circle at 50% 12%, {active_tint} 0%, transparent 75%) !important;
        background-attachment: fixed;
        color: {palette['text_primary']} !important;
        font-family: 'Inter', sans-serif !important;
        transition: background-color 0.4s ease, color 0.3s ease;
    }}

    .cinzel-title {{
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.04em;
        line-height: 1.4;
        color: {palette['accent_gold']} !important;
    }}

    .serif-quote {{
        font-family: 'Lora', 'Noto Serif Devanagari', serif !important;
        font-style: italic;
    }}

    .category-badge {{
        display: inline-block;
        padding: 6px 16px;
        background: {palette['badge_bg']};
        color: {palette['badge_text']};
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 14px;
        border: 1px solid {palette['card_border']};
    }}

    div[data-testid="stButton"] > button {{
        background-color: {palette['card_bg']} !important;
        border: 1.5px solid {palette['card_border']} !important;
        border-radius: 12px !important;
        padding: 18px 22px !important;
        color: {palette['text_primary']} !important;
        text-align: left !important;
        justify-content: flex-start !important;
        min-height: 70px !important;
        white-space: normal !important;
        box-shadow: 0 4px 12px {palette['shadow']} !important;
        transition: all 0.22s ease-in-out !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        border-color: {palette['accent_gold']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px {palette['shadow']} !important;
    }}

    div[data-testid="stButton"] > button[kind="primary"] {{
        background-color: {palette['tile_selected_bg'] if theme.lower() == 'dark' else palette['card_checked_bg']} !important;
        border-color: {palette['accent_gold']} !important;
        box-shadow: 0 0 0 1px {palette['accent_gold']}, 0 8px 20px {palette['shadow']} !important;
    }}

    .stat-card {{
        background: {palette['card_bg']};
        border: 1px solid {palette['card_border']};
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 6px 16px {palette['shadow']};
        height: 100%;
    }}

    .tension-card {{
        padding: 22px 26px !important;
        background: {palette['card_bg']} !important;
        border-left: 4px solid {palette['accent_gold']} !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        border-top: 1px solid {palette['card_border']} !important;
        border-right: 1px solid {palette['card_border']} !important;
        border-bottom: 1px solid {palette['card_border']} !important;
        box-shadow: 0 4px 15px {palette['shadow']} !important;
    }}

    .social-btn {{
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        background: {palette['card_bg']};
        color: {palette['text_primary']} !important;
        border: 1px solid {palette['card_border']};
        text-decoration: none;
        font-weight: 500;
        font-size: 0.92rem;
        transition: all 0.2s ease;
    }}
    .social-btn:hover {{
        border-color: {palette['accent_gold']};
        transform: translateY(-2px);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. LOCALIZATION STRINGS
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an intellectually serious, non-judgmental exploration of human thought. Across 25 or 100 questions, discover the structural architecture of your worldview and trace your affinities to major global philosophical traditions.",
        "quick_test": "Quick Odyssey (25 Questions)",
        "full_test": "Full Odyssey (100 Questions)",
        "start_quick": "Start Quick Odyssey (25 Questions)",
        "start_full": "Start Full Odyssey (100 Questions)",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "next_btn": "Next →",
        "reveal_btn": "Reveal My Worldview 🧭",
        "retake_btn": "Retake Odyssey ↺",
        "char_title": "🧭 Profile Diagnostic Dimensions",
        "affinities_label": "🏛️ Major Historical Lineages",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal thematic consistency.",
        "comparison_title": "🔬 Compare With Traditions",
        "confidence_title": "🔍 Epistemic Conviction Calibration",
        "confidence_sub": "Calibrate your intellectual certainty versus your openness to revised evidence:",
        "confidence_low": "Humility (Hold views provisionally)",
        "confidence_high": "Certainty (Hold absolute truths)",
        "share_heading": "📢 Share Your Profile & Digital Passport",
        "share_sub": "Share your cognitive identity card or permalink with peers:",
        "passport_btn": "Download Official HD Passport (PNG) 🎫"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज पर निकलें। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें और स्टोइसिज्म, अद्वैत वेदांत, मार्क्सवाद और दाओवाद जैसी वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "quick_test": "त्वरित यात्रा (25 प्रश्न)",
        "full_test": "पूर्ण यात्रा (100 प्रश्न)",
        "start_quick": "त्वरित यात्रा शुरू करें (25 प्रश्न)",
        "start_full": "पूर्ण यात्रा शुरू करें (100 प्रश्न)",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "next_btn": "अगला →",
        "reveal_btn": "मेरा विश्वदृष्टिकोण प्रकट करें 🧭",
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
        "share_heading": "📢 अपनी प्रोफ़ाइल और पासपोर्ट साझा करें",
        "share_sub": "अपना डिजिटल पहचान पासपोर्ट या लिंक दूसरों के साथ साझा करें:",
        "passport_btn": "आधिकारिक HD पासपोर्ट (PNG) डाउनलोड करें 🎫"
    }
}

# ==============================================================================
# 5. HD PIL PASSPORT ENGINE
# ==============================================================================
def generate_hd_passport(user_coords, top_affinity, character_tags):
    """Generates an 800x1150 HD Philosophical Digital Passport image."""
    w, h = 800, 1150
    img = Image.new("RGB", (w, h), (26, 30, 36))
    draw = ImageDraw.Draw(img)

    # Frame Borders & Corner Brackets
    draw.rectangle([25, 25, w - 25, h - 25], outline=(212, 175, 55), width=2)
    draw.rectangle([35, 35, w - 35, h - 35], outline=(95, 80, 40), width=1)
    
    for cx, cy in [(25, 25), (w - 25, 25), (25, h - 25), (w - 25, h - 25)]:
        draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(212, 175, 55))

    # Headers
    draw.text((w // 2, 75), "THE COMPASS OF HUMAN PERSPECTIVES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 105), "COGNITIVE IDENTITY ARTIFACT", fill=(160, 174, 192), anchor="mm")

    # Match Box
    draw.rounded_rectangle([60, 160, w - 60, 290], radius=12, fill=(36, 41, 50), outline=(53, 61, 74))
    draw.text((w // 2, 205), top_affinity["name"].upper(), fill=(240, 244, 248), anchor="mm")
    draw.text((w // 2, 245), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(56, 189, 248), anchor="mm")

    # Sliders
    labels = [
        ("Transcendence / Physicalism (D0)", user_coords[0]),
        ("Collectivism / Individualism (D1)", user_coords[1]),
        ("Progressivism / Traditionalism (D2)", user_coords[2]),
        ("Empiricism / Rationalism (D3)", user_coords[3])
    ]
    
    start_y = 350
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 85)
        draw.text((60, y), lbl, fill=(228, 232, 238))
        draw.rounded_rectangle([60, y + 25, 740, y + 39], radius=7, fill=(45, 55, 72))
        norm_x = 60 + int(((val + 1.0) / 2.0) * 680)
        draw.rounded_rectangle([60, y + 25, max(75, norm_x), y + 39], radius=7, fill=(212, 175, 55))

    # Attributes & Thinkers
    draw.text((w // 2, 750), "PROFILE ATTRIBUTES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 790), " • ".join(character_tags), fill=(240, 244, 248), anchor="mm")
    thinkers_str = ", ".join(top_affinity.get("thinkers", [])[:3])
    draw.text((w // 2, 855), f"CANONICAL LINEAGE: {thinkers_str}", fill=(160, 174, 192), anchor="mm")

    # Barcode Simulator
    for bx in range(80, 720, 12):
        stroke = 4 if (bx % 24 == 0) else 2
        draw.line([(bx, 970), (bx, 1020)], fill=(212, 175, 55), width=stroke)

    draw.text((w // 2, 1090), "NON-CLINICAL PHILOSOPHICAL IDENTITY SPECIFICATION", fill=(128, 141, 158), anchor="mm")

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
        wv_desc.append(data["description"])
        
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
            xaxis=dict(title='Transcendence (D0)', backgroundcolor='#1C2129', color='#808D9E', showbackground=True),
            yaxis=dict(title='Collectivism (D1)', backgroundcolor='#1C2129', color='#808D9E', showbackground=True),
            zaxis=dict(title='Progressivism (D2)', backgroundcolor='#1C2129', color='#808D9E', showbackground=True),
        ),
        legend=dict(x=0, y=1, bgcolor='rgba(26,30,36,0.8)')
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
            bgcolor="rgba(36, 41, 50, 0.4)"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(color="#E4E8EE")
    )
    return fig

# ==============================================================================
# 7. STATE SYNCHRONIZATION
# ==============================================================================
def load_url_parameters():
    try:
        params = st.query_params
        if "answers" in params:
            st.session_state.answers = json.loads(urllib.parse.unquote(params["answers"]))
            st.session_state.completed = True
            st.session_state.started = True
        if "lang" in params and params["lang"] in ["English", "Hindi"]:
            st.session_state.language = params["lang"]
        if "theme" in params and params["theme"] in ["Dark", "Light"]:
            st.session_state.theme = params["theme"]
    except Exception:
        pass

def generate_share_url():
    encoded_answers = urllib.parse.quote(json.dumps(st.session_state.answers))
    return f"?answers={encoded_answers}&lang={st.session_state.language}&theme={st.session_state.theme}"

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

if "url_checked" not in st.session_state:
    load_url_parameters()
    st.session_state.url_checked = True

raw_questions = load_questions_dataset(mode=st.session_state.test_type.lower())
active_dim_idx = 0
if st.session_state.started and not st.session_state.completed and raw_questions:
    active_dim_idx = raw_questions[st.session_state.current_question_index].get("dimIndex", 0)

inject_custom_theme(st.session_state.theme, active_dim_idx)
ui = UI_TEXT[st.session_state.language]
is_hindi = (st.session_state.language == "Hindi")

# Header Bar
c1, c2, c3 = st.columns([6.5, 2.0, 1.5])
with c1:
    st.markdown("<h2 class='cinzel-title' style='margin:0;'>🧭 THE COMPASS OF HUMAN PERSPECTIVES</h2>", unsafe_allow_html=True)
with c2:
    lang = st.selectbox("Language / भाषा", ["English", "Hindi"], index=0 if not is_hindi else 1, label_visibility="collapsed")
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()
with c3:
    thm = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, label_visibility="collapsed")
    if thm != st.session_state.theme:
        st.session_state.theme = thm
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
        st.info(f"**{ui['quick_test']}**\n\n25 questions (1 per core dimension) for a concise 10-minute diagnostic.")
        if st.button(ui["start_quick"], use_container_width=True, type="primary"):
            st.session_state.test_type = "Quick"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            st.rerun()
    with b2:
        st.info(f"**{ui['full_test']}**\n\n100 questions (4 per core dimension) for a comprehensive profile map.")
        if st.button(ui["start_full"], use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTIONNAIRE SLIDESHOW
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    st.progress((idx + 1) / total_q)
    dim_name = q.get('dimension_hi' if is_hindi else 'dimension', q.get('dimension', ''))
    
    badge_html = f"<div class='category-badge'>DIMENSION: {dim_name.upper()}</div>"
    st.markdown(badge_html, unsafe_allow_html=True)
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q))

    q_text = q['text_hi'] if is_hindi and q.get('text_hi') else q['text_en']
    st.markdown(f"<h3 style='margin: 14px 0 24px 0; line-height: 1.4;'>{q_text}</h3>", unsafe_allow_html=True)

    current_choice = st.session_state.answers.get(q["id"], None)

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
            st.session_state.answers[q["id"]] = opt_code
            st.rerun()

    st.write("")
    nav1, _, nav3 = st.columns([2, 5, 2])
    with nav1:
        if idx > 0 and st.button(ui["prev_btn"], use_container_width=True):
            st.session_state.current_question_index -= 1
            st.rerun()
    with nav3:
        if idx < total_q - 1:
            if st.button(ui["next_btn"], use_container_width=True, disabled=(current_choice is None)):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button(ui["reveal_btn"], use_container_width=True, type="primary", disabled=(current_choice is None)):
                st.session_state.completed = True
                st.rerun()

# ==============================================================================
# VIEW 3: PROFILE REVEAL & DIAGNOSTIC MIRROR
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
    <div style='text-align: center; padding: 25px 20px;'>
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

    # Tradition Comparison Selector
    st.write("---")
    st.markdown(f"### {ui['comparison_title']}")
    comp_school = st.selectbox("Select a tradition to compare with your profile:", list(WORLDVIEWS.keys()), index=0)
    if comp_school:
        comp_data = WORLDVIEWS[comp_school]
        c_col1, c_col2 = st.columns([6, 4])
        with c_col1:
            st.plotly_chart(render_radar_comparison(user_coords, comp_data["vector"], comp_school), use_container_width=True)
        with c_col2:
            st.markdown(f"**{comp_school}**")
            st.write(comp_data["description"])
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

    # Epistemic Confidence Calibration
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

    # Social Sharing Hub & HD Passport
    st.write("---")
    st.markdown(f"### {ui['share_heading']}")
    st.caption(ui["share_sub"])

    passport_bytes = generate_hd_passport(user_coords, top_match, tags)
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
            file_name=f"philosophical_passport_{top_match['slug']}.png",
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
            st.rerun()