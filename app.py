"""
app.py - The Compass of Human Perspectives
Presentation & GUI Layer: Streamlit layout, session state lifecycle,
interactive bilingual components, dynamic thematic styling, and passport generation.
"""

import os
import json
import base64
import urllib.parse
from io import BytesIO
from typing import Optional

import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# IMPORT MODULAR TIERS
# ==============================================================================
from database import WORLDVIEWS, load_questions_dataset, get_worldview_data
from engine import (
    calculate_coordinates_direct,
    calculate_affinities,
    characterize_profile,
    check_tensions,
)

# ==============================================================================
# STREAMLIT CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="The Compass of Human Perspectives",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. THEMATIC PALETTES & CSS INJECTION
# ==============================================================================
def inject_premium_styles(theme: str = "Dark"):
    """Injects high-end responsive CSS stylesheets into the Streamlit viewport."""
    if theme.lower() == "light":
        palette = {
            "bg_color": "#FAF8F5",
            "text_color": "#1E293B",
            "text_secondary": "#475569",
            "text_hindi": "#57534E",
            "accent_color": "#9A722C",
            "card_bg": "#FFFDFB",
            "card_border": "rgba(154, 114, 44, 0.15)",
            "card_hover_border": "rgba(154, 114, 44, 0.45)",
            "card_checked_bg": "rgba(154, 114, 44, 0.08)",
            "shadow": "rgba(154, 114, 44, 0.08)"
        }
    else:
        palette = {
            "bg_color": "#090D16",
            "text_color": "#E2E8F0",
            "text_secondary": "#94A3B8",
            "text_hindi": "#94A3B8",
            "accent_color": "#D4AF37",
            "card_bg": "rgba(15, 23, 42, 0.65)",
            "card_border": "rgba(255, 255, 255, 0.08)",
            "card_hover_border": "rgba(212, 175, 55, 0.5)",
            "card_checked_bg": "rgba(212, 175, 55, 0.1)",
            "shadow": "rgba(0, 0, 0, 0.25)"
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@300;400;500;600;700&family=Noto+Serif+Devanagari:wght@400;500;600;700&display=swap');

    .stApp {{
        background-color: {palette['bg_color']} !important;
        color: {palette['text_color']} !important;
        font-family: 'Inter', sans-serif;
    }}

    .hero-container {{
        text-align: center;
        padding: 40px 20px 20px 20px;
    }}

    .cinzel-title {{
        font-family: 'Cinzel', serif;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: {palette['accent_color']};
    }}

    .serif-text {{
        font-family: 'Noto Serif Devanagari', serif;
    }}

    .choice-card {{
        background: {palette['card_bg']};
        border: 1px solid {palette['card_border']};
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px {palette['shadow']};
    }}

    .choice-card:hover {{
        border-color: {palette['card_hover_border']};
        transform: translateY(-2px);
    }}

    .bilingual-en {{
        font-size: 1.05rem;
        font-weight: 500;
        color: {palette['text_color']};
        margin-bottom: 4px;
    }}

    .bilingual-hi {{
        font-size: 0.95rem;
        color: {palette['text_hindi']};
        font-family: 'Noto Serif Devanagari', serif;
    }}

    .tension-card {{
        background: {palette['card_bg']};
        border-left: 4px solid {palette['accent_color']};
        border-radius: 4px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }}

    .tension-title {{
        font-family: 'Cinzel', serif;
        font-weight: 700;
        font-size: 1.1rem;
        color: {palette['accent_color']};
        margin-bottom: 6px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOCALIZED UI STRINGS
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an intellectually serious exploration of human thought. Across 25 or 100 questions, discover the structural architecture of your worldview and trace your affinities to major global traditions including Stoicism, Advaita Vedanta, Marxism, and Daoism.",
        "start_btn": "Begin the Odyssey →",
        "quick_test": "Quick Odyssey (25 Questions)",
        "full_test": "Full Odyssey (100 Questions)",
        "test_type_label": "Select Odyssey Length:",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "next_btn": "Next →",
        "reveal_btn": "Reveal My Worldview 🧭",
        "retake_btn": "Retake Odyssey ↺",
        "map_title": "📊 4D Worldview Vector Space",
        "char_title": "🧭 Profile Characterization",
        "affinities_label": "🏛️ Philosophical Affinities",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal thematic consistency.",
        "passport_btn": "Download Official Passport 🎫"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज पर निकलें। अपने विश्वदृष्टिकोण की वास्तुकला को जानें और स्टोइसिज्म, अद्वैत वेदांत, मार्क्सवाद और दाओवाद जैसी वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "start_btn": "यात्रा शुरू करें →",
        "quick_test": "त्वरित यात्रा (25 प्रश्न)",
        "full_test": "पूर्ण यात्रा (100 प्रश्न)",
        "test_type_label": "यात्रा की अवधि चुनें:",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "next_btn": "अगला →",
        "reveal_btn": "मेरा विश्वदृष्टिकोण प्रकट करें 🧭",
        "retake_btn": "पुनः आरंभ करें ↺",
        "map_title": "📊 4D विश्वदृष्टिकोण वेक्टर स्पेस",
        "char_title": "🧭 प्रोफ़ाइल लक्षण वर्णन",
        "affinities_label": "🏛️ दार्शनिक समानताएं",
        "challenge_title": "⚡ संज्ञानात्मक तनाव (Cognitive Tensions)",
        "no_tensions": "🟢 कोई संरचनात्मक तनाव नहीं पाया गया। आपका विश्वदृष्टिकोण उच्च विषयगत निरंतरता प्रदर्शित करता है।",
        "passport_btn": "आधिकारिक पासपोर्ट डाउनलोड करें 🎫"
    }
}

# ==============================================================================
# 3. PASSPORT COMPOSITING ENGINE
# ==============================================================================
def generate_passport_image(user_coords, top_affinity, character_tags):
    """Generates an 800x1100 digital philosophical passport asset."""
    w, h = 800, 1100
    img = Image.new("RGB", (w, h), "#090D16")
    draw = ImageDraw.Draw(img)

    # Double Border Frame
    draw.rectangle([25, 25, w - 25, h - 25], outline="#D4AF37", width=2)
    draw.rectangle([35, 35, w - 35, h - 35], outline="rgba(212, 175, 55, 0.4)", width=1)

    # Header
    draw.text((w // 2, 75), "THE COMPASS OF HUMAN PERSPECTIVES", fill="#D4AF37", anchor="mm")
    draw.text((w // 2, 105), "COGNITIVE IDENTITY PASSPORT", fill="#94A3B8", anchor="mm")

    # Primary Affinity
    draw.text((w // 2, 220), top_affinity["name"].upper(), fill="#F8FAFC", anchor="mm")
    draw.text((w // 2, 255), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill="#38BDF8", anchor="mm")

    # Axis Dimension Bars
    labels = [
        ("Transcendence / Physicalism", user_coords[0]),
        ("Collectivism / Individualism", user_coords[1]),
        ("Progressivism / Traditionalism", user_coords[2]),
        ("Empiricism / Rationalism", user_coords[3])
    ]
    
    start_y = 350
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 80)
        draw.text((60, y), lbl, fill="#E2E8F0")
        
        # Track Bar
        draw.rounded_rectangle([60, y + 25, 740, y + 37], radius=6, fill="#1E293B")
        
        # Value Slider [-1, 1] normalized to [0, 680]
        norm_x = 60 + int(((val + 1.0) / 2.0) * 680)
        draw.rounded_rectangle([60, y + 25, max(70, norm_x), y + 37], radius=6, fill="#D4AF37")

    # Footer Tags
    draw.text((w // 2, 750), "PROFILE ATTRIBUTES", fill="#D4AF37", anchor="mm")
    draw.text((w // 2, 790), " • ".join(character_tags), fill="#F8FAFC", anchor="mm")
    draw.text((w // 2, 1040), "NON-CLINICAL PHILOSOPHICAL IDENTITY ARTIFACT", fill="#64748B", anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# 4. RADAR / VECTOR VISUALIZATION
# ==============================================================================
def render_vector_radar(user_coords, top_match_vector):
    """Renders Plotly 4D radar chart comparing user with primary match."""
    categories = [
        'Transcendence (D0)',
        'Collectivism (D1)',
        'Progressivism (D2)',
        'Empiricism (D3)'
    ]
    
    # Scale from [-1, 1] to [0, 100] for clean radial viewing
    user_scaled = [((v + 1.0) / 2.0) * 100.0 for v in user_coords]
    match_scaled = [((v + 1.0) / 2.0) * 100.0 for v in top_match_vector]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_scaled + [user_scaled[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Your Coordinates',
        line_color='#D4AF37'
    ))
    fig.add_trace(go.Scatterpolar(
        r=match_scaled + [match_scaled[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='Tradition Baseline',
        line_color='#38BDF8',
        opacity=0.5
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
            bgcolor="rgba(15, 23, 42, 0.4)"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(color="#E2E8F0")
    )
    return fig

# ==============================================================================
# 5. STATE INITIALIZATION & SYNC
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

# Inject Theme CSS
inject_premium_styles(st.session_state.theme)
ui = UI_TEXT[st.session_state.language]

# Top Nav Bar
col1, col2, col3 = st.columns([6.5, 2.0, 1.5])
with col1:
    st.markdown("<h2 class='cinzel-title' style='margin:0;'>🧭 THE COMPASS OF HUMAN PERSPECTIVES</h2>", unsafe_allow_html=True)
with col2:
    lang = st.selectbox("Language / भाषा", ["English", "Hindi"], index=0 if st.session_state.language == "English" else 1, label_visibility="collapsed")
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()
with col3:
    thm = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, label_visibility="collapsed")
    if thm != st.session_state.theme:
        st.session_state.theme = thm
        st.rerun()

st.write("---")

# Load Active Questions
raw_questions = load_questions_dataset(mode=st.session_state.test_type.lower())

# ==============================================================================
# VIEW 1: LANDING PAGE
# ==============================================================================
if not st.session_state.started and not st.session_state.completed:
    st.markdown(f"""
    <div class='hero-container'>
        <h1 class='cinzel-title' style='font-size: 2.8rem;'>{ui['title']}</h1>
        <p class='serif-text' style='font-size: 1.35rem; color: #94A3B8; font-style: italic;'>“{ui['subtitle']}”</p>
        <p style='max-width: 750px; margin: 25px auto; font-size: 1.1rem; line-height: 1.7;'>{ui['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)

    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        st.info(f"**{ui['quick_test']}**\n\nOne question per core dimension for a 10-minute diagnostic.")
        if st.button("Start Quick Odyssey", use_container_width=True, type="primary"):
            st.session_state.test_type = "Quick"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.rerun()

    with mode_col2:
        st.info(f"**{ui['full_test']}**\n\nDeep-dive master assessment across all 100 questions.")
        if st.button("Start Full Odyssey", use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTIONNAIRE ODYSSEY SLIDESHOW
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    # Progress Indicator
    progress = (idx + 1) / total_q
    st.progress(progress)
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q) + f" — {q.get('dimension', '')}")

    # Question Header
    st.markdown(f"""
    <div style='margin: 20px 0;'>
        <h3 style='margin-bottom: 6px;'>{q['text_en']}</h3>
        <p class='serif-text' style='color: #94A3B8; font-size: 1.15rem;'>{q['text_hi']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Options Selection
    current_choice = st.session_state.answers.get(q["id"], None)
    
    for opt in q["options"]:
        opt_code = opt["code"]
        is_selected = (current_choice == opt_code)
        
        # Interactive Option Container
        if st.button(
            f"{opt_code}. {opt['text_en']}\n\n({opt['text_hi']})",
            key=f"opt_{q['id']}_{opt_code}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.answers[q["id"]] = opt_code
            st.rerun()

    # Nav Buttons
    st.write("")
    nav1, nav2, nav3 = st.columns([2, 5, 2])
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

    st.markdown(f"""
    <div class='hero-container'>
        <h1 class='cinzel-title' style='font-size: 2.5rem;'>{top_match['name']}</h1>
        <p class='serif-text' style='font-size: 1.3rem; color: #D4AF37;'>{top_match['name_hi']} ({top_match['similarity_pct']}% Match)</p>
        <p style='max-width: 800px; margin: 15px auto;'>{top_match['description'] if st.session_state.language == 'English' else top_match['description_hi']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Core Vectors and Radar Map
    r_col1, r_col2 = st.columns([5, 5])
    with r_col1:
        st.markdown(f"### {ui['char_title']}")
        for t in tags:
            st.markdown(f"- **{t}**")
        
        st.write("")
        st.markdown(f"**Thinkers:** {', '.join(top_match.get('thinkers', []))}")
        st.markdown(f"**Coordinates:** `D0: {user_coords[0]}, D1: {user_coords[1]}, D2: {user_coords[2]}, D3: {user_coords[3]}`")

    with r_col2:
        st.plotly_chart(render_vector_radar(user_coords, top_match["vector"]), use_container_width=True)

    # Affinities Breakdown
    st.write("---")
    st.markdown(f"### {ui['affinities_label']}")
    aff_cols = st.columns(3)
    for i, aff in enumerate(affinities[1:7]):
        with aff_cols[i % 3]:
            st.metric(label=aff["name"], value=f"{aff['similarity_pct']}%")

    # Cognitive Tensions
    st.write("---")
    st.markdown(f"### {ui['challenge_title']}")
    if tensions:
        for t in tensions:
            st.markdown(f"""
            <div class='tension-card'>
                <div class='tension-title'>{t['title']}</div>
                <div style='color: inherit; font-size: 0.95rem;'>{t['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(ui["no_tensions"])

    # Downloadable Sharing Asset
    st.write("---")
    passport_data = generate_passport_image(user_coords, top_match, tags)
    d_col1, d_col2 = st.columns([6, 4])
    with d_col1:
        st.download_button(
            label=ui["passport_btn"],
            data=passport_data,
            file_name="philosophical_passport.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )
    with d_col2:
        if st.button(ui["retake_btn"], use_container_width=True):
            st.session_state.completed = False
            st.session_state.started = False
            st.session_state.answers = {}
            st.session_state.current_question_index = 0
            st.rerun()