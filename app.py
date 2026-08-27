"""
app.py - The Compass of Human Perspectives
Presentation & GUI Layer: Streamlit layout, session state lifecycle,
language-specific views, dynamic thematic styling, and crash-safe passport generation.
"""

import os
import sys
from io import BytesIO

# Ensure working directory is in module path
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
# CSS STYLESHEET
# ==============================================================================
def inject_premium_styles(theme: str = "Dark"):
    palette = {
        "bg_color": "#FAF8F5" if theme.lower() == "light" else "#090D16",
        "text_color": "#1E293B" if theme.lower() == "light" else "#E2E8F0",
        "accent_color": "#9A722C" if theme.lower() == "light" else "#D4AF37",
        "card_bg": "#FFFDFB" if theme.lower() == "light" else "rgba(15, 23, 42, 0.65)",
        "card_border": "rgba(154, 114, 44, 0.2)" if theme.lower() == "light" else "rgba(255, 255, 255, 0.1)"
    }
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&family=Noto+Serif+Devanagari:wght@400;600&display=swap');
    .stApp {{
        background-color: {palette['bg_color']} !important;
        color: {palette['text_color']} !important;
        font-family: 'Inter', sans-serif;
    }}
    .cinzel-title {{
        font-family: 'Cinzel', serif;
        font-weight: 700;
        color: {palette['accent_color']};
    }}
    .serif-text {{
        font-family: 'Noto Serif Devanagari', serif;
    }}
    .tension-card {{
        background: {palette['card_bg']};
        border-left: 4px solid {palette['accent_color']};
        padding: 16px 20px;
        margin-bottom: 14px;
        border-radius: 4px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# LOCALIZED UI TEXT
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an exploration of human thought. Across 25 or 100 questions, discover the structural architecture of your worldview.",
        "quick_test": "Quick Odyssey (25 Questions)",
        "full_test": "Full Odyssey (100 Questions)",
        "start_quick": "Start Quick Odyssey (25 Questions)",
        "start_full": "Start Full Odyssey (100 Questions)",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "next_btn": "Next →",
        "reveal_btn": "Reveal My Worldview 🧭",
        "retake_btn": "Retake Odyssey ↺",
        "char_title": "🧭 Profile Characterization",
        "affinities_label": "🏛️ Philosophical Affinities",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal thematic consistency.",
        "passport_btn": "Download Official Passport 🎫"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक गंभीर खोज पर निकलें। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें।",
        "quick_test": "त्वरित यात्रा (25 प्रश्न)",
        "full_test": "पूर्ण यात्रा (100 प्रश्न)",
        "start_quick": "त्वरित यात्रा शुरू करें (25 प्रश्न)",
        "start_full": "पूर्ण यात्रा शुरू करें (100 प्रश्न)",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "next_btn": "अगला →",
        "reveal_btn": "मेरा विश्वदृष्टिकोण प्रकट करें 🧭",
        "retake_btn": "पुनः आरंभ करें ↺",
        "char_title": "🧭 प्रोफ़ाइल लक्षण वर्णन",
        "affinities_label": "🏛️ दार्शनिक समानताएं",
        "challenge_title": "⚡ संज्ञानात्मक तनाव (Cognitive Tensions)",
        "no_tensions": "🟢 कोई संरचनात्मक तनाव नहीं पाया गया। आपका विश्वदृष्टिकोण उच्च विषयगत निरंतरता प्रदर्शित करता है।",
        "passport_btn": "आधिकारिक पासपोर्ट डाउनलोड करें 🎫"
    }
}

# ==============================================================================
# FIXED PASSPORT COMPOSITING ENGINE
# ==============================================================================
def generate_passport_image(user_coords, top_affinity, character_tags):
    """Generates an 800x1100 digital philosophical passport without string color crashes."""
    w, h = 800, 1100
    img = Image.new("RGB", (w, h), (9, 13, 22))
    draw = ImageDraw.Draw(img)

    # Frame Borders (using solid integer tuples to avoid Pillow string errors)
    draw.rectangle([25, 25, w - 25, h - 25], outline=(212, 175, 55), width=2)
    draw.rectangle([35, 35, w - 35, h - 35], outline=(100, 85, 35), width=1)

    # Header
    draw.text((w // 2, 75), "THE COMPASS OF HUMAN PERSPECTIVES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 105), "COGNITIVE IDENTITY PASSPORT", fill=(148, 163, 184), anchor="mm")

    # Primary Affinity Match
    draw.text((w // 2, 220), top_affinity["name"].upper(), fill=(248, 250, 252), anchor="mm")
    draw.text((w // 2, 255), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(56, 189, 248), anchor="mm")

    # Coordinates Track Bars
    labels = [
        ("Transcendence / Physicalism", user_coords[0]),
        ("Collectivism / Individualism", user_coords[1]),
        ("Progressivism / Traditionalism", user_coords[2]),
        ("Empiricism / Rationalism", user_coords[3])
    ]
    
    start_y = 350
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 80)
        draw.text((60, y), lbl, fill=(226, 232, 240))
        draw.rounded_rectangle([60, y + 25, 740, y + 37], radius=6, fill=(30, 41, 59))
        norm_x = 60 + int(((val + 1.0) / 2.0) * 680)
        draw.rounded_rectangle([60, y + 25, max(70, norm_x), y + 37], radius=6, fill=(212, 175, 55))

    # Tags
    draw.text((w // 2, 750), "PROFILE ATTRIBUTES", fill=(212, 175, 55), anchor="mm")
    draw.text((w // 2, 790), " • ".join(character_tags), fill=(248, 250, 252), anchor="mm")
    draw.text((w // 2, 1040), "NON-CLINICAL PHILOSOPHICAL IDENTITY ARTIFACT", fill=(100, 116, 139), anchor="mm")

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
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"), bgcolor="rgba(15, 23, 42, 0.4)"),
        paper_bgcolor='rgba(0,0,0,0)', showlegend=True, margin=dict(l=40, r=40, t=20, b=20),
        font=dict(color="#E2E8F0")
    )
    return fig

# ==============================================================================
# STATE INITIALIZATION
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

inject_premium_styles(st.session_state.theme)
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

raw_questions = load_questions_dataset(mode=st.session_state.test_type.lower())

# ==============================================================================
# VIEW 1: LANDING PAGE
# ==============================================================================
if not st.session_state.started and not st.session_state.completed:
    st.markdown(f"""
    <div style='text-align: center; padding: 30px 20px;'>
        <h1 class='cinzel-title' style='font-size: 2.8rem;'>{ui['title']}</h1>
        <p class='serif-text' style='font-size: 1.35rem; color: #94A3B8; font-style: italic;'>“{ui['subtitle']}”</p>
        <p style='max-width: 750px; margin: 20px auto; font-size: 1.1rem; line-height: 1.7;'>{ui['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        st.info(f"**{ui['quick_test']}**\n\n25 questions (1 per core dimension).")
        if st.button(ui["start_quick"], use_container_width=True, type="primary"):
            st.session_state.test_type = "Quick"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.rerun()
    with b2:
        st.info(f"**{ui['full_test']}**\n\n100 questions (4 per core dimension).")
        if st.button(ui["start_full"], use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTION SLIDESHOW
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    st.progress((idx + 1) / total_q)
    dim_name = q.get('dimension_hi' if is_hindi else 'dimension', '')
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q) + f" — {dim_name}")

    q_text = q['text_hi'] if is_hindi and q.get('text_hi') else q['text_en']
    st.markdown(f"<h3 style='margin: 20px 0;'>{q_text}</h3>", unsafe_allow_html=True)

    current_choice = st.session_state.answers.get(q["id"], None)
    for opt in q["options"]:
        opt_code = opt["code"]
        opt_text = opt['text_hi'] if is_hindi and opt.get('text_hi') else opt['text_en']
        is_selected = (current_choice == opt_code)
        
        if st.button(
            f"{opt_code}. {opt_text}",
            key=f"opt_{q['id']}_{opt_code}",
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
# VIEW 3: PROFILE REVEAL
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
        <h1 class='cinzel-title' style='font-size: 2.5rem;'>{title}</h1>
        <p class='serif-text' style='font-size: 1.3rem; color: #D4AF37;'>{top_match['similarity_pct']}% Affinity</p>
        <p style='max-width: 800px; margin: 15px auto;'>{desc}</p>
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
                <div style='font-weight:700; color:#D4AF37; margin-bottom:5px;'>{t['title']}</div>
                <div>{t['description']}</div>
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