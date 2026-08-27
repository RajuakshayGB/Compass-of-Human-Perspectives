"""
app.py - The Compass of Human Perspectives
Presentation & GUI Layer: Streamlit layout, session state lifecycle,
category-tinted viewports, elevated interactive option tiles, and passport generation.
"""

import os
import sys
from io import BytesIO

# Ensure working directory is on the Python module search path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw

from database import WORLDVIEWS, load_questions_dataset, get_worldview_data
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
# 1. 25-DIMENSION AMBIENT TINT PALETTES
# ==============================================================================
DIMENSION_TINTS = {
    0:  {"dark": "rgba(14, 165, 233, 0.08)", "light": "#EDF5FA"},   # Metaphysics & Reality (Slate Blue)
    1:  {"dark": "rgba(168, 85, 247, 0.08)", "light": "#F5EFFB"},   # Consciousness & Mind (Lilac)
    2:  {"dark": "rgba(20, 184, 166, 0.08)", "light": "#EDF8F6"},   # Epistemology & Knowledge (Teal)
    3:  {"dark": "rgba(16, 185, 129, 0.08)", "light": "#ECF8F2"},   # Truth & Realism (Emerald)
    4:  {"dark": "rgba(217, 119, 6, 0.08)",  "light": "#FAF4E8"},   # Religion & Sacredness (Amber)
    5:  {"dark": "rgba(124, 58, 237, 0.08)", "light": "#F3EEFA"},   # Death & Finitude (Violet)
    6:  {"dark": "rgba(244, 63, 94, 0.08)",  "light": "#FCEEF0"},   # Purpose & Meaning (Rose)
    7:  {"dark": "rgba(59, 130, 246, 0.08)", "light": "#EDF3FC"},   # Ethics & Meta-Ethics (Blue)
    8:  {"dark": "rgba(6, 182, 212, 0.08)",  "light": "#EBF6F8"},   # Moral Action & Practical Virtue (Sky)
    9:  {"dark": "rgba(234, 88, 12, 0.08)",  "light": "#FAF0EB"},   # Human Nature & Destiny (Terracotta)
    10: {"dark": "rgba(139, 92, 246, 0.08)", "light": "#F2EEFA"},   # Self & Identity (Indigo)
    11: {"dark": "rgba(22, 163, 74, 0.08)",  "light": "#ECF6EE"},   # Free Will & Agency (Forest Green)
    12: {"dark": "rgba(34, 197, 94, 0.08)",  "light": "#EFF7F1"},   # Society & Community (Sage)
    13: {"dark": "rgba(29, 78, 216, 0.08)",  "light": "#EBF1FA"},   # Liberty & Governance (Royal Blue)
    14: {"dark": "rgba(146, 64, 14, 0.08)",  "light": "#F7F1EB"},   # Authority & Institutional Order (Bronze)
    15: {"dark": "rgba(225, 29, 72, 0.08)",  "light": "#FBEFF2"},   # Equality & Hierarchy (Crimson)
    16: {"dark": "rgba(101, 163, 13, 0.08)", "light": "#F2F7EB"},   # Economics & Distribution (Olive)
    17: {"dark": "rgba(180, 83, 9, 0.08)",   "light": "#F8F1EA"},   # Culture & Tradition (Sienna)
    18: {"dark": "rgba(220, 38, 38, 0.08)",  "light": "#FCEFEF"},   # Political Change (Coral)
    19: {"dark": "rgba(30, 58, 138, 0.08)",  "light": "#ECEFF7"},   # Global Scope & Loyalty (Navy)
    20: {"dark": "rgba(16, 185, 129, 0.08)", "light": "#ECF8F3"},   # Ecology & Environment (Pure Green)
    21: {"dark": "rgba(20, 184, 166, 0.08)", "light": "#EBF7F6"},   # Animal Ethics & Sentience (Mint)
    22: {"dark": "rgba(124, 58, 237, 0.08)", "light": "#F3EEFA"},   # Technology & AI (Electric Violet)
    23: {"dark": "rgba(6, 182, 212, 0.08)",  "light": "#EBF6F8"},   # Civilizational Future (Turquoise)
    24: {"dark": "rgba(249, 115, 22, 0.08)", "light": "#FAF1EB"}    # Pluralism & Openness (Peach)
}

# ==============================================================================
# 2. ENHANCED GREY/OFF-WHITE STYLING & TILE ARCHITECTURE
# ==============================================================================
def inject_custom_styles(theme: str = "Dark", dim_idx: int = 0):
    """Injects bespoke CSS for refined Grey / Off-White palettes with category tints."""
    tint_mode = "dark" if theme.lower() == "dark" else "light"
    active_tint = DIMENSION_TINTS.get(dim_idx, {}).get(tint_mode, "transparent")

    if theme.lower() == "light":
        # Refined Warm Off-White / Alabaster
        palette = {
            "bg_base": "#F7F5F0",
            "text_primary": "#2D3748",
            "text_secondary": "#5A6A80",
            "text_sub": "#718096",
            "accent_gold": "#9A722C",
            "tile_bg": "#FFFFFF",
            "tile_border": "#E2DCD2",
            "tile_hover_border": "#9A722C",
            "tile_selected_bg": "#F4EDE1",
            "tile_selected_border": "#9A722C",
            "tension_bg": "#FFFFFF",
            "badge_bg": "#EFECE4",
            "badge_text": "#785B24"
        }
    else:
        # Refined Neutral Grey / Deep Slate-Grey
        palette = {
            "bg_base": "#1A1E24",
            "text_primary": "#E4E8EE",
            "text_secondary": "#A0AEC0",
            "text_sub": "#808D9E",
            "accent_gold": "#D4AF37",
            "tile_bg": "#242932",
            "tile_border": "#353D4A",
            "tile_hover_border": "#D4AF37",
            "tile_selected_bg": "#2E3642",
            "tile_selected_border": "#D4AF37",
            "tension_bg": "#242932",
            "badge_bg": "#1C2129",
            "badge_text": "#D4AF37"
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Noto+Serif+Devanagari:wght@400;600&display=swap');

    /* Viewport Base Background with Category Ambient Tint */
    .stApp {{
        background-color: {palette['bg_base']} !important;
        background-image: radial-gradient(circle at 50% 15%, {active_tint} 0%, transparent 75%) !important;
        background-attachment: fixed;
        color: {palette['text_primary']} !important;
        font-family: 'Inter', sans-serif;
    }}

    .cinzel-title {{
        font-family: 'Cinzel', serif;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: {palette['accent_gold']};
    }}

    .serif-text {{
        font-family: 'Noto Serif Devanagari', serif;
    }}

    /* Question Dimension Category Header Badge */
    .category-badge {{
        display: inline-block;
        padding: 5px 14px;
        background: {palette['badge_bg']};
        color: {palette['badge_text']};
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        border: 1px solid {palette['tile_border']};
    }}

    /* Interactive Option Tile Styling */
    div[data-testid="stButton"] > button {{
        background-color: {palette['tile_bg']} !important;
        border: 1.5px solid {palette['tile_border']} !important;
        border-radius: 12px !important;
        padding: 16px 22px !important;
        color: {palette['text_primary']} !important;
        text-align: left !important;
        justify-content: flex-start !important;
        min-height: 72px !important;
        white-space: normal !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.22s ease-in-out !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        border-color: {palette['tile_hover_border']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12) !important;
    }}

    /* Selected Option Tile Highlight */
    div[data-testid="stButton"] > button[kind="primary"] {{
        background-color: {palette['tile_selected_bg']} !important;
        border-color: {palette['tile_selected_border']} !important;
        box-shadow: 0 0 0 1px {palette['tile_selected_border']}, 0 8px 20px rgba(0, 0, 0, 0.18) !important;
    }}

    .tension-card {{
        background: {palette['tension_bg']};
        border-left: 4px solid {palette['accent_gold']};
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. UI LOCALIZED DICTIONARY
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an intellectual exploration of human thought. Across 25 or 100 questions, discover the structural architecture of your worldview and measure your affinities to major philosophical traditions.",
        "quick_test": "Quick Odyssey (25 Questions)",
        "full_test": "Full Odyssey (100 Questions)",
        "start_quick": "Start Quick Odyssey (25 Questions)",
        "start_full": "Start Full Odyssey (100 Questions)",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "next_btn": "Next →",
        "reveal_btn": "Reveal My Worldview 🧭",
        "retake_btn": "Retake Odyssey ↺",
        "char_title": "🧭 Profile Attributes",
        "affinities_label": "🏛️ Philosophical Affinities",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal thematic consistency.",
        "passport_btn": "Download Official Passport 🎫"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक गहन खोज पर निकलें। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को समझें और वैश्विक दार्शनिक परंपराओं के साथ अपनी समानता देखें।",
        "quick_test": "त्वरित यात्रा (25 प्रश्न)",
        "full_test": "पूर्ण यात्रा (100 प्रश्न)",
        "start_quick": "त्वरित यात्रा शुरू करें (25 प्रश्न)",
        "start_full": "पूर्ण यात्रा शुरू करें (100 प्रश्न)",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "next_btn": "अगला →",
        "reveal_btn": "मेरा विश्वदृष्टिकोण प्रकट करें 🧭",
        "retake_btn": "पुनः आरंभ करें ↺",
        "char_title": "🧭 प्रोफ़ाइल लक्षण",
        "affinities_label": "🏛️ दार्शनिक समानताएं",
        "challenge_title": "⚡ संज्ञानात्मक तनाव (Cognitive Tensions)",
        "no_tensions": "🟢 कोई संरचनात्मक तनाव नहीं पाया गया। आपका विश्वदृष्टिकोण उच्च विषयगत निरंतरता प्रदर्शित करता है।",
        "passport_btn": "आधिकारिक पासपोर्ट डाउनलोड करें 🎫"
    }
}

# ==============================================================================
# 4. PASSPORT GENERATION ENGINE
# ==============================================================================
def generate_passport_image(user_coords, top_affinity, character_tags):
    """Generates an 800x1100 digital philosophical passport asset."""
    w, h = 800, 1100
    img = Image.new("RGB", (w, h), (26, 30, 36))
    draw = ImageDraw.Draw(img)

    # Frame Borders
    draw.rectangle([25, 25, w - 25, h - 25], outline=(212, 175, 55), width=2)
    draw.rectangle([35, 35, w - 35, h - 35], outline=(100, 85, 35), width=1)

    # Header
    draw.text((w // 2, 75), "THE COMPASS OF HUMAN PERSPECTIVES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 105), "COGNITIVE IDENTITY PASSPORT", fill=(160, 174, 192), anchor="mm")

    # Primary Affinity
    draw.text((w // 2, 220), top_affinity["name"].upper(), fill=(240, 244, 248), anchor="mm")
    draw.text((w // 2, 255), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(56, 189, 248), anchor="mm")

    # Coordinate Sliders
    labels = [
        ("Transcendence / Physicalism", user_coords[0]),
        ("Collectivism / Individualism", user_coords[1]),
        ("Progressivism / Traditionalism", user_coords[2]),
        ("Empiricism / Rationalism", user_coords[3])
    ]
    
    start_y = 350
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 80)
        draw.text((60, y), lbl, fill=(228, 232, 238))
        draw.rounded_rectangle([60, y + 25, 740, y + 37], radius=6, fill=(45, 55, 72))
        norm_x = 60 + int(((val + 1.0) / 2.0) * 680)
        draw.rounded_rectangle([60, y + 25, max(70, norm_x), y + 37], radius=6, fill=(212, 175, 55))

    # Footer
    draw.text((w // 2, 750), "PROFILE ATTRIBUTES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 790), " • ".join(character_tags), fill=(240, 244, 248), anchor="mm")
    draw.text((w // 2, 1040), "NON-CLINICAL PHILOSOPHICAL IDENTITY ARTIFACT", fill=(128, 141, 158), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def render_vector_radar(user_coords, top_match_vector):
    categories = ['Transcendence (D0)', 'Collectivism (D1)', 'Progressivism (D2)', 'Empiricism (D3)']
    user_scaled = [((v + 1.0) / 2.0) * 100.0 for v in user_coords]
    match_scaled = [((v + 1.0) / 2.0) * 100.0 for v in top_match_vector]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_scaled + [user_scaled[0]], theta=categories + [categories[0]],
        fill='toself', name='Your Coordinates', line_color='#D4AF37'
    ))
    fig.add_trace(go.Scatterpolar(
        r=match_scaled + [match_scaled[0]], theta=categories + [categories[0]],
        fill='toself', name='Tradition Baseline', line_color='#38BDF8', opacity=0.5
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
# 5. STATE INITIALIZATION & CONTROLS
# ==============================================================================
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

raw_questions = load_questions_dataset(mode=st.session_state.test_type.lower())
active_dim_idx = 0
if st.session_state.started and not st.session_state.completed and raw_questions:
    active_dim_idx = raw_questions[st.session_state.current_question_index].get("dimIndex", 0)

inject_custom_styles(st.session_state.theme, active_dim_idx)
ui = UI_TEXT[st.session_state.language]
is_hindi = (st.session_state.language == "Hindi")

# Navigation Header
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
        <p class='serif-text' style='font-size: 1.35rem; color: #A0AEC0; font-style: italic;'>“{ui['subtitle']}”</p>
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
            st.rerun()
    with b2:
        st.info(f"**{ui['full_test']}**\n\n100 questions (4 per core dimension) for a deep assessment.")
        if st.button(ui["start_full"], use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTION SLIDESHOW (TILED OPTIONS WITH AMBIENT CATEGORY TINT)
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    # Progress & Category Badge
    st.progress((idx + 1) / total_q)
    dim_name = q.get('dimension_hi' if is_hindi else 'dimension', q.get('dimension', ''))
    
    badge_html = f"<div class='category-badge'>DIMENSION: {dim_name.upper()}</div>"
    st.markdown(badge_html, unsafe_allow_html=True)
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q))

    # Question Text
    q_text = q['text_hi'] if is_hindi and q.get('text_hi') else q['text_en']
    st.markdown(f"<h3 style='margin: 14px 0 24px 0; line-height: 1.4;'>{q_text}</h3>", unsafe_allow_html=True)

    current_choice = st.session_state.answers.get(q["id"], None)

    # Elevated Option Tiles
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
        <p class='serif-text' style='font-size: 1.3rem; color: #D4AF37;'>{top_match['similarity_pct']}% Match Affinity</p>
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
        st.plotly_chart(render_vector_radar(user_coords, top_match["vector"]), use_container_width=True)

    st.write("---")
    st.markdown(f"### {ui['affinities_label']}")
    aff_cols = st.columns(3)
    for i, aff in enumerate(affinities[1:7]):
        with aff_cols[i % 3]:
            nm = aff["name_hi"] if is_hindi else aff["name"]
            st.metric(label=nm, value=f"{aff['similarity_pct']}%")

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

    st.write("---")
    passport_data = generate_passport_image(user_coords, top_match, tags)
    d1, d2 = st.columns([6, 4])
    with d1:
        st.download_button(
            label=ui["passport_btn"],
            data=passport_data,
            file_name="philosophical_passport.png",
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