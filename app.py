"""
app.py - Worldview Compass
Presentation & UI Layer
"""

import os
import sys
import json
import base64
import urllib.parse
from io import BytesIO

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw

# ==============================================================================
# 1. CORE DATA & SCORING LOGIC IMPORTS (WITH CACHED DATASET LOADER)
# ==============================================================================
from database import WORLDVIEWS, load_questions_dataset
from engine import (
    calculate_coordinates_direct,
    calculate_affinities,
    characterize_profile,
    check_tensions,
)

@st.cache_data
def get_cached_questions_dataset(mode: str):
    return load_questions_dataset(mode=mode)

st.set_page_config(
    page_title="Worldview Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. LOGO ENCODER & REGISTRY
# ==============================================================================
def get_base64_logo():
    logo_paths = [
        "app_logo.png",
        os.path.join(current_dir, "app_logo.png"),
        "/workspace/app_logo.png"
    ]
    for path in logo_paths:
        if path and os.path.exists(path):
            try:
                with open(path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except Exception:
                pass
    return None

PHILOSOPHER_QUOTES = {
    "Secular Scientific Humanism": {
        "thinkers": [("Carl Sagan", 0.45), ("John Dewey", 0.30), ("Richard Dawkins", 0.25)],
        "quote": "“For small creatures such as we the vastness is bearable only through love and reason.” — Carl Sagan"
    },
    "Stoicism": {
        "thinkers": [("Marcus Aurelius", 0.50), ("Seneca", 0.30), ("Epictetus", 0.20)],
        "quote": "“You have power over your mind - not outside events. Realize this, and you will find strength.” — Marcus Aurelius"
    },
    "Advaita Vedanta": {
        "thinkers": [("Adi Shankara", 0.55), ("Ramana Maharshi", 0.30), ("Gaudapada", 0.15)],
        "quote": "“Brahman is the only truth, the world is an illusion, and there is ultimately no difference between Brahman and the individual self.” — Adi Shankara"
    },
    "Marxism": {
        "thinkers": [("Karl Marx", 0.50), ("Friedrich Engels", 0.30), ("Rosa Luxemburg", 0.20)],
        "quote": "“The philosophers have only interpreted the world in various ways; the point is to change it.” — Karl Marx"
    },
    "Daoism": {
        "thinkers": [("Laozi", 0.60), ("Zhuangzi", 0.40)],
        "quote": "“Nature does not hurry, yet everything is accomplished.” — Laozi"
    },
    "Early Buddhism": {
        "thinkers": [("Siddhartha Gautama", 0.65), ("Nagarjuna", 0.35)],
        "quote": "“Peace comes from within. Do not seek it without. Everything that arises passes away.” — Siddhartha Gautama"
    },
    "Christian Theism": {
        "thinkers": [("Thomas Aquinas", 0.40), ("Augustine of Hippo", 0.35), ("C.S. Lewis", 0.25)],
        "quote": "“To one who has faith, no explanation is necessary. To one without faith, no explanation is possible.” — Thomas Aquinas"
    },
    "Ubuntu": {
        "thinkers": [("Desmond Tutu", 0.55), ("Nelson Mandela", 0.45)],
        "quote": "“A person is a person through other persons. None of us comes into the world fully formed.” — Desmond Tutu"
    },
    "Confucianism": {
        "thinkers": [("Confucius", 0.55), ("Mencius", 0.30), ("Xunzi", 0.15)],
        "quote": "“To know what is right and not to do it is the worst cowardice.” — Confucius"
    },
    "Deep Ecology": {
        "thinkers": [("Arne Naess", 0.50), ("Aldo Leopold", 0.30), ("Rachel Carson", 0.20)],
        "quote": "“The flourishing of human and non-human life on Earth has intrinsic value.” — Arne Naess"
    },
    "Transhumanism": {
        "thinkers": [("Nick Bostrom", 0.45), ("Ray Kurzweil", 0.35), ("Max More", 0.20)],
        "quote": "“Humanity need not be the endpoint of evolution, but the beginning of conscious transcendence.” — Nick Bostrom"
    },
    "Existentialism": {
        "thinkers": [("Jean-Paul Sartre", 0.40), ("Albert Camus", 0.35), ("Friedrich Nietzsche", 0.25)],
        "quote": "“Man is condemned to be free; because once thrown into the world, he is responsible for everything he does.” — Jean-Paul Sartre"
    },
    "Classical Liberalism": {
        "thinkers": [("John Locke", 0.45), ("Adam Smith", 0.35), ("John Stuart Mill", 0.20)],
        "quote": "“The only purpose for which power can be rightfully exercised over any member of a civilized community, against his will, is to prevent harm to others.” — John Stuart Mill"
    }
}

# ==============================================================================
# 3. 25-DIMENSION CATEGORY LIGHTING PALETTES
# ==============================================================================
DIMENSION_TINTS = {
    0:  {"dark": "rgba(14, 165, 233, 0.12)", "light": "#E0F2FE"},
    1:  {"dark": "rgba(168, 85, 247, 0.12)", "light": "#F3E8FF"},
    2:  {"dark": "rgba(20, 184, 166, 0.12)", "light": "#CCFBF1"},
    3:  {"dark": "rgba(16, 185, 129, 0.12)", "light": "#D1FAE5"},
    4:  {"dark": "rgba(217, 119, 6, 0.12)",  "light": "#FEF3C7"},
    5:  {"dark": "rgba(124, 58, 237, 0.12)", "light": "#EDE9FE"},
    6:  {"dark": "rgba(244, 63, 94, 0.12)",  "light": "#FFE4E6"},
    7:  {"dark": "rgba(59, 130, 246, 0.12)", "light": "#DBEAFE"},
    8:  {"dark": "rgba(6, 182, 212, 0.12)",  "light": "#CFFAFE"},
    9:  {"dark": "rgba(234, 88, 12, 0.12)",  "light": "#FFEDD5"},
    10: {"dark": "rgba(139, 92, 246, 0.12)", "light": "#EDE9FE"},
    11: {"dark": "rgba(22, 163, 74, 0.12)",  "light": "#DCFCE7"},
    12: {"dark": "rgba(34, 197, 94, 0.12)",  "light": "#DCFCE7"},
    13: {"dark": "rgba(29, 78, 216, 0.12)",  "light": "#DBEAFE"},
    14: {"dark": "rgba(146, 64, 14, 0.12)",  "light": "#FEEBC8"},
    15: {"dark": "rgba(225, 29, 72, 0.12)",  "light": "#FFE4E6"},
    16: {"dark": "rgba(101, 163, 13, 0.12)", "light": "#ECFCCB"},
    17: {"dark": "rgba(180, 83, 9, 0.12)",   "light": "#FEF3C7"},
    18: {"dark": "rgba(220, 38, 38, 0.12)",  "light": "#FEE2E2"},
    19: {"dark": "rgba(30, 58, 138, 0.12)",  "light": "#DBEAFE"},
    20: {"dark": "rgba(16, 185, 129, 0.12)", "light": "#D1FAE5"},
    21: {"dark": "rgba(20, 184, 166, 0.12)", "light": "#CCFBF1"},
    22: {"dark": "rgba(124, 58, 237, 0.12)", "light": "#EDE9FE"},
    23: {"dark": "rgba(6, 182, 212, 0.12)",  "light": "#CFFAFE"},
    24: {"dark": "rgba(249, 115, 22, 0.12)", "light": "#FFEDD5"}
}

# ==============================================================================
# 4. HIGH-CONTRAST THEME INJECTOR & ANIMATIONS
# ==============================================================================
def inject_custom_theme(theme: str = "Dark", dim_idx: int = 0):
    tint_mode = "dark" if theme.lower() == "dark" else "light"
    active_tint = DIMENSION_TINTS.get(dim_idx, {}).get(tint_mode, "transparent")

    if theme.lower() == "light":
        palette = {
            "bg_base": "#F8F6F0",
            "text_primary": "#0F172A",
            "text_secondary": "#334155",
            "accent_gold": "#855D10",
            "glass_tile_bg": "#FFFFFF",
            "glass_tile_border": "#D1C7B7",
            "glass_tile_hover": "#855D10",
            "glass_selected_bg": "#F5EFEB",
            "badge_bg": "#E8E1D5",
            "badge_text": "#5C4008",
            "border_outer": "#855D10",
            "border_inner": "#94A3B8",
            "gauge_bg": "#E2DCD2",
            "gauge_fill": "#855D10",
            "shadow": "0 6px 18px rgba(0, 0, 0, 0.08)"
        }
    else:
        palette = {
            "bg_base": "#0B0F17",
            "text_primary": "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent_gold": "#D4AF37",
            "glass_tile_bg": "rgba(22, 28, 38, 0.85)",
            "glass_tile_border": "rgba(212, 175, 55, 0.28)",
            "glass_tile_hover": "rgba(212, 175, 55, 0.85)",
            "glass_selected_bg": "rgba(212, 175, 55, 0.22)",
            "badge_bg": "#151C26",
            "badge_text": "#D4AF37",
            "border_outer": "#D4AF37",
            "border_inner": "#64748B",
            "gauge_bg": "#1E2633",
            "gauge_fill": "#D4AF37",
            "shadow": "0 10px 30px rgba(0, 0, 0, 0.50)"
        }

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Devanagari:wght@400;600;700&display=swap');

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .stApp {{
        background-color: {palette['bg_base']} !important;
        background-image: radial-gradient(circle at 50% 8%, {active_tint} 0%, transparent 75%) !important;
        background-attachment: fixed;
        color: {palette['text_primary']} !important;
        font-family: 'Inter', sans-serif !important;
        box-sizing: border-box;
        border: 4px solid {palette['border_outer']} !important;
        outline: 2px solid {palette['border_inner']} !important;
        outline-offset: -10px;
        padding: 18px 24px !important;
        min-height: 100vh;
        animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @media (max-width: 768px) {{
        .stApp {{
            border: 2px solid {palette['border_outer']} !important;
            outline: 1.5px solid {palette['border_inner']} !important;
            outline-offset: -5px;
            padding: 8px 10px !important;
        }}
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: {palette['text_primary']};
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
        color: {palette['text_secondary']} !important;
    }}

    .category-badge {{
        display: inline-block;
        padding: 5px 15px;
        background: {palette['badge_bg']};
        color: {palette['badge_text']} !important;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
        border: 1px solid {palette['glass_tile_border']};
    }}

    .top-nav-btn div[data-testid="stButton"] > button {{
        min-height: 42px !important;
        max-height: 42px !important;
        padding: 6px 14px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        margin-top: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div[data-testid="stButton"] > button {{
        background: {palette['glass_tile_bg']} !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1.5px solid {palette['glass_tile_border']} !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        color: {palette['text_primary']} !important;
        text-align: left !important;
        justify-content: flex-start !important;
        min-height: 68px !important;
        white-space: normal !important;
        box-shadow: {palette['shadow']} !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        border-color: {palette['glass_tile_hover']} !important;
        transform: translateY(-2px) !important;
        color: {palette['accent_gold']} !important;
    }}

    div[data-testid="stButton"] > button[kind="primary"] {{
        background: {palette['glass_selected_bg']} !important;
        border-color: {palette['accent_gold']} !important;
        box-shadow: 0 0 0 1px {palette['accent_gold']}, {palette['shadow']} !important;
    }}

    .highlight-card {{
        padding: 20px;
        border-radius: 14px;
        border: 1.5px solid {palette['glass_tile_border']};
        background: {palette['glass_tile_bg']};
        backdrop-filter: blur(14px);
        box-shadow: {palette['shadow']};
        margin-bottom: 14px;
    }}

    .dimension-box {{
        margin-bottom: 16px;
        padding: 14px 18px;
        border-radius: 12px;
        background: {palette['glass_tile_bg']};
        border: 1px solid {palette['glass_tile_border']};
    }}

    .gauge-track {{
        width: 100%;
        height: 8px;
        background: {palette['gauge_bg']};
        border-radius: 4px;
        position: relative;
        margin: 10px 0;
        overflow: hidden;
    }}

    .gauge-fill {{
        height: 100%;
        background: {palette['gauge_fill']};
        border-radius: 4px;
        transition: width 0.3s ease;
    }}

    .tension-card {{
        padding: 18px 22px !important;
        background: {palette['glass_tile_bg']} !important;
        backdrop-filter: blur(12px) !important;
        border-left: 4px solid {palette['accent_gold']} !important;
        border-radius: 8px !important;
        margin-bottom: 14px !important;
        border-top: 1px solid {palette['glass_tile_border']} !important;
        border-right: 1px solid {palette['glass_tile_border']} !important;
        border-bottom: 1px solid {palette['glass_tile_border']} !important;
    }}

    .social-btn {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        height: 42px;
        padding: 0 18px;
        border-radius: 8px;
        background: {palette['glass_tile_bg']};
        color: {palette['text_primary']} !important;
        border: 1.5px solid {palette['glass_tile_border']};
        text-decoration: none;
        font-weight: 600;
        font-size: 0.88rem;
        box-shadow: {palette['shadow']};
        transition: all 0.2s ease;
    }}
    .social-btn:hover {{
        border-color: {palette['accent_gold']};
        transform: translateY(-2px);
    }}
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 5. LOCALIZED CONTENT DICTIONARY
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "Worldview Compass",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "An intellectually serious, non-judgmental exploration of your foundational assumptions. Discover your coordinates in a 4D philosophical spectrum and trace your affinities to major global traditions.",
        "quick_label": "⚡ Quick Odyssey\n\n25 Questions • ~8 mins\nSamples 1 question per core dimension for an efficient diagnostic.",
        "full_label": "🏛️ Full Odyssey\n\n100 Questions • ~25 mins\nComprehensive assessment across all 100 questions for maximum precision.",
        "progress_label": "Question {current} of {total} ({pct}% complete • ~{time_left} mins remaining)",
        "prev_btn": "← Previous",
        "home_retake_btn": "🧭 Home / Retake",
        "char_title": "🧭 Diagnostic Dimensions & Polarity Gauges",
        "thinker_breakdown_title": "🧬 Philosophical Twin & Lineage Match",
        "affinities_label": "🏛️ Major Historical Lineages & Affinity Ranking",
        "challenge_title": "⚡ Dialectical Cognitive Tensions",
        "no_tensions": "🟢 No structural tensions detected. Your worldview displays high internal consistency.",
        "comparison_title": "🔬 Compare With Other Traditions",
        "comparison_sub": "Your primary matched tradition ({matched_school}) is shown above. Select traditions below to compare:",
        "matrix_title": "⚔️ Philosophical Compatibility & Friend Duel",
        "matrix_sub": "Paste a friend's share URL to generate your side-by-side compatibility matrix and AI debate battlegrounds:",
        "confidence_title": "🔍 Epistemic Conviction Calibration",
        "confidence_sub": "Calibrate your intellectual certainty versus your openness to revised evidence:",
        "confidence_low": "Humility (Hold views provisionally)",
        "confidence_high": "Certainty (Hold absolute truths)",
        "share_heading": "📢 Share Your Profile & Identity Artifacts",
        "share_sub": "Download your comprehensive high-resolution identity card image or share your cognitive profile:",
        "passport_btn": "Download Comprehensive Identity Card (PNG) 🎫"
    },
    "Hindi": {
        "title": "विचार कम्पास (Worldview Compass)",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें और प्रमुख वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "quick_label": "⚡ त्वरित यात्रा\n\n25 प्रश्न • ~8 मिनट\nत्वरित मूल्यांकन के लिए 25 मूल आयामों से 1 प्रतिनिधि प्रश्न।",
        "full_label": "🏛️ पूर्ण यात्रा\n\n100 प्रश्न • ~25 मिनट\nसमग्र विश्लेषण के लिए सभी 100 प्रश्नों का विस्तृत मूल्यांकन।",
        "progress_label": "प्रश्न {current} का {total} ({pct}% पूर्ण • ~{time_left} मिनट शेष)",
        "prev_btn": "← पिछला",
        "home_retake_btn": "🧭 होम / पुनः आरंभ",
        "char_title": "🧭 प्रोफ़ाइल नैदानिक आयाम एवं ध्रुवीयता विश्लेषण",
        "thinker_breakdown_title": "🧬 दार्शनिक विचारक समानता और उद्धरण",
        "affinities_label": "🏛️ प्रमुख ऐतिहासिक दार्शनिक परंपराएं एवं समानता रैंकिंग",
        "challenge_title": "⚡ संज्ञानात्मक तनाव (Cognitive Tensions)",
        "no_tensions": "🟢 कोई संरचनात्मक तनाव नहीं पाया गया। आपका विश्वदृष्टिकोण उच्च विषयगत निरंतरता प्रदर्शित करता है।",
        "comparison_title": "🔬 अन्य परंपराओं के साथ तुलना करें",
        "comparison_sub": "आपकी प्राथमिक परंपरा ({matched_school}) ऊपर प्रदर्शित है। किसी अन्य परंपरा से तुलना करने के लिए नीचे चुनें:",
        "matrix_title": "⚔️ दार्शनिक अनुकूलता एवं मित्र संवाद मैट्रिक्स",
        "matrix_sub": "मित्र का शेयर लिंक पेस्ट करें और अपनी आपसी अनुकूलता व वैचारिक बहस के बिंदु जानें:",
        "confidence_title": "🔍 बौद्धिक आत्मविश्वास और विश्वास की गहराई",
        "confidence_sub": "नए साक्ष्यों के आधार पर विचार बदलने की अपनी तत्परता का स्तर निर्धारित करें:",
        "confidence_low": "बौद्धिक विनम्रता (संशोधन के लिए तैयार)",
        "confidence_high": "पूर्ण निश्चितता (अटल विश्वास)",
        "share_heading": "📢 अपनी प्रोफ़ाइल और दस्तावेज साझा करें",
        "share_sub": "अपना विस्तृत डिजिटल पहचान पत्र डाउनलोड करें या साझा करें:",
        "passport_btn": "व्यापक पहचान पत्र डाउनलोड करें (PNG) 🎫"
    }
}

HOMEPAGE_SECTIONS = [
    {
        "icon": "🌌",
        "title_en": "Metaphysics & Mind",
        "title_hi": "तत्वमीमांसा और मन",
        "desc_en": "Examines reality's fundamental fabric, consciousness, and free will vs determinism[cite: 5].",
        "desc_hi": "वास्तविकता के मूल स्वरूप, चेतना और स्वतंत्र इच्छा का अन्वेषण करता है[cite: 5]."
    },
    {
        "icon": "⚖️",
        "title_en": "Ethics & Society",
        "title_hi": "नैतिकता और समाज",
        "desc_en": "Maps moral virtue, relational duties (Ubuntu), and systemic governance models[cite: 5].",
        "desc_hi": "नैतिक कर्तव्यों, सामुदायिक संबंधों और शासन प्रणालियों का विश्लेषण करता है[cite: 5]."
    },
    {
        "icon": "🌱",
        "title_en": "Ecology & Future",
        "title_hi": "पारिस्थितिकी और भविष्य",
        "desc_en": "Surveys biocentric environmental ethics, animal sentience, and AI horizons[cite: 5].",
        "desc_hi": "पर्यावरण नैतिकता, पशु अधिकार और कृत्रिम बुद्धिमत्ता का विश्लेषण करता है[cite: 5]."
    }
]

# ==============================================================================
# 6. HD IDENTITY CARD (PNG) COMPOSITOR (HIGH RESOLUTION & DETAILED CONTENT)
# ==============================================================================
def generate_hd_passport(user_coords, top_affinity, character_tags, affinities, tensions, custom_handle=""):
    w, h = 1000, 1600
    img = Image.new("RGB", (w, h), (249, 248, 245))
    draw = ImageDraw.Draw(img)

    # Dual Metallic Border Frame
    draw.rectangle([25, 25, w - 25, h - 25], outline=(197, 160, 89), width=4)
    draw.rectangle([38, 38, w - 38, h - 38], outline=(148, 163, 184), width=1)
    
    for cx, cy in [(25, 25), (w - 25, 25), (25, h - 25), (w - 25, h - 25)]:
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(197, 160, 89))

    # Center-Aligned Header Box
    draw.rounded_rectangle([70, 55, w - 70, 135], radius=10, fill=(255, 255, 255), outline=(226, 218, 203), width=1)
    draw.text((w // 2, 80), "WORLDVIEW COMPASS: COMPREHENSIVE COGNITIVE DOSSIER", fill=(133, 93, 16), anchor="mm")
    
    subtitle_text = f"VERIFIED SPECIFICATION • {custom_handle.upper()}" if custom_handle else "VERIFIED PHILOSOPHICAL IDENTITY SPECIFICATION"
    draw.text((w // 2, 110), subtitle_text, fill=(100, 116, 139), anchor="mm")

    # Primary Worldview Card Box
    draw.rounded_rectangle([60, 155, w - 60, 285], radius=12, fill=(255, 255, 255), outline=(197, 160, 89), width=2)
    draw.text((w // 2, 192), top_affinity["name"].upper(), fill=(15, 23, 42), anchor="mm")
    draw.text((w // 2, 230), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(2, 132, 199), anchor="mm")

    desc = top_affinity.get("description", "")
    lines = [desc[i:i+85] for i in range(0, len(desc), 85)][:2]
    for idx, l in enumerate(lines):
        draw.text((w // 2, 252 + (idx * 20)), l.strip(), fill=(51, 65, 85), anchor="mm")

    # 4D Continuous Coordinates Section
    draw.text((w // 2, 320), "DIMENSIONAL POLARITY METRICS (4D SPECTRUM)", fill=(133, 93, 16), anchor="mm")
    labels = [
        ("Metaphysics (Transcendence vs Physicalism)", user_coords[0]),
        ("Society (Collectivism vs Individualism)", user_coords[1]),
        ("Culture (Progressivism vs Traditionalism)", user_coords[2]),
        ("Epistemology (Empiricism vs Rationalism)", user_coords[3])
    ]
    
    start_y = 350
    for idx, (lbl, val) in enumerate(labels):
        y = start_y + (idx * 75)
        draw.text((70, y), lbl, fill=(15, 23, 42))
        draw.text((930, y), f"{val:+.2f}", fill=(133, 93, 16), anchor="ra")
        draw.rounded_rectangle([70, y + 22, 930, y + 36], radius=6, fill=(226, 218, 203))
        norm_x = 70 + int(((val + 1.0) / 2.0) * 860)
        draw.rounded_rectangle([70, y + 22, max(85, norm_x), y + 36], radius=6, fill=(197, 160, 89))

    # Top Historical Lineages Section
    draw.text((w // 2, 675), "TOP HISTORICAL LINEAGE AFFINITIES", fill=(133, 93, 16), anchor="mm")
    aff_str = "  •  ".join([f"{a['name']} ({a['similarity_pct']}%)" for a in affinities[:4]])
    draw.text((w // 2, 710), aff_str, fill=(15, 23, 42), anchor="mm")

    # Profile Attributes & Thinkers
    draw.text((w // 2, 770), "PROFILE ATTRIBUTES & CANONICAL THINKERS", fill=(133, 93, 16), anchor="mm")
    draw.text((w // 2, 805), " • ".join(character_tags), fill=(15, 23, 42), anchor="mm")
    thinkers_str = ", ".join(top_affinity.get("thinkers", [])[:3])
    draw.text((w // 2, 840), f"Canonical Lineage Thinkers: {thinkers_str}", fill=(71, 85, 105), anchor="mm")

    # Dialectical Tensions Summary
    draw.text((w // 2, 900), "DIALECTICAL COGNITIVE TENSIONS & CONSISTENCY", fill=(133, 93, 16), anchor="mm")
    if tensions:
        t_summary = f"Primary Detected Tension: {tensions[0]['title']}"
    else:
        t_summary = "No major structural tensions detected. High internal consistency."
    draw.text((w // 2, 935), t_summary, fill=(180, 83, 9), anchor="mm")

    # Decorative Barcode Seal
    for bx in range(100, 900, 12):
        stroke = 4 if (bx % 24 == 0) else 2
        draw.line([(bx, 1420), (bx, 1470)], fill=(197, 160, 89), width=stroke)

    draw.text((w // 2, 1530), "NON-CLINICAL PHILOSOPHICAL IDENTITY SPECIFICATION • WORLDVIEW COMPASS", fill=(148, 163, 184), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==============================================================================
# 7. VECTOR VISUALIZERS (3D + MULTI-TRADITION RADAR COMPARISON)
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

def render_multi_radar_comparison(user_coords, comparisons: list, chart_theme="Dark", user_label="Your Coordinates"):
    categories = ['Transcendence', 'Collectivism', 'Progressivism', 'Empiricism']
    user_scaled = [((v + 1.0) / 2.0) * 100.0 for v in user_coords]

    is_light = (chart_theme.lower() == "light")
    text_col = "#0F172A" if is_light else "#E4E8EE"
    grid_col = "#94A3B8" if is_light else "#64748B"
    bg_col = "rgba(255, 255, 255, 0.4)" if is_light else "rgba(30, 36, 46, 0.4)"
    user_color = "#855D10" if is_light else "#D4AF37"

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=user_scaled + [user_scaled[0]], theta=categories + [categories[0]],
        fill='toself', name=user_label, line_color=user_color
    ))

    colors = ['#0284C7', '#10B981', '#8B5CF6', '#F59E0B']
    for idx, (comp_name, comp_coords) in enumerate(comparisons):
        comp_scaled = [((v + 1.0) / 2.0) * 100.0 for v in comp_coords]
        fig.add_trace(go.Scatterpolar(
            r=comp_scaled + [comp_scaled[0]], theta=categories + [categories[0]],
            fill='toself', name=comp_name, line_color=colors[idx % len(colors)], opacity=0.45
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color=grid_col),
            bgcolor=bg_col
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(color=text_col)
    )
    return fig

# ==============================================================================
# 8. STATE SYNCHRONIZATION
# ==============================================================================
def sync_state_to_url():
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

raw_questions = get_cached_questions_dataset(mode=st.session_state.test_type.lower())
active_dim_idx = 0
if st.session_state.started and not st.session_state.completed and raw_questions:
    if st.session_state.current_question_index < len(raw_questions):
        active_dim_idx = raw_questions[st.session_state.current_question_index].get("dimIndex", 0)

inject_custom_theme(st.session_state.theme, active_dim_idx)
ui = UI_TEXT[st.session_state.language]
is_hindi = (st.session_state.language == "Hindi")

# ==============================================================================
# 9. UNIFORM TOP HEADER LAYOUT (PARALLEL ALIGNMENT)
# ==============================================================================
c1, c2, c3, c4 = st.columns([4.5, 2.5, 1.5, 1.5])
with c1:
    b64_logo = get_base64_logo()
    if b64_logo:
        logo_html = f"""
        <div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">
            <img src="data:image/png;base64,{b64_logo}" width="32" height="32" style="border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
            <span style='font-family: "Cinzel", serif; font-weight: 700; font-size: 1.15rem; color: inherit; letter-spacing: 0.04em;'>WORLDVIEW COMPASS</span>
        </div>
        """
    else:
        logo_html = """
        <div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">
            <span style='font-size: 1.5rem;'>🧭</span>
            <span style='font-family: "Cinzel", serif; font-weight: 700; font-size: 1.15rem; color: inherit; letter-spacing: 0.04em;'>WORLDVIEW COMPASS</span>
        </div>
        """
    st.markdown(logo_html, unsafe_allow_html=True)

with c2:
    st.markdown("<div class='top-nav-btn'>", unsafe_allow_html=True)
    if st.button(ui["home_retake_btn"], key="top_home_retake_btn", use_container_width=True):
        st.session_state.completed = False
        st.session_state.started = False
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        sync_state_to_url()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    st.markdown("<div class='top-nav-btn'>", unsafe_allow_html=True)
    target_lang = "हिन्दी" if st.session_state.language == "English" else "English"
    if st.button(f"🌐 {target_lang}", key="lang_switch_btn", use_container_width=True):
        st.session_state.language = "Hindi" if st.session_state.language == "English" else "English"
        sync_state_to_url()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    st.markdown("<div class='top-nav-btn'>", unsafe_allow_html=True)
    target_theme_label = "☀️ Light" if st.session_state.theme == "Dark" else "🌙 Dark"
    if st.button(target_theme_label, key="theme_switch_btn", use_container_width=True):
        st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"
        sync_state_to_url()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# ==============================================================================
# VIEW 1: LANDING HOMEPAGE
# ==============================================================================
if not st.session_state.started and not st.session_state.completed:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px 10px 10px 10px;'>
        <h1 class='cinzel-title' style='font-size: 2.8rem;'>{ui['title']}</h1>
        <p class='serif-quote' style='font-size: 1.35rem;'>“{ui['subtitle']}”</p>
        <p style='max-width: 780px; margin: 16px auto; font-size: 1.08rem; line-height: 1.7;'>{ui['tagline']}</p>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    for col, data in zip([s1, s2, s3], HOMEPAGE_SECTIONS):
        with col:
            title = data["title_hi"] if is_hindi else data["title_en"]
            desc = data["desc_hi"] if is_hindi else data["desc_en"]
            st.markdown(f"""
            <div class='highlight-card'>
                <div style='font-size: 1.7rem; margin-bottom: 6px;'>{data['icon']}</div>
                <div style='font-weight: 700; font-size: 1.15rem; margin-bottom: 6px;'>{title}</div>
                <div style='font-size: 0.90rem; line-height: 1.5; opacity: 0.9;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    b1, b2 = st.columns(2)
    with b1:
        if st.button(ui["quick_label"], use_container_width=True, type="primary"):
            st.session_state.test_type = "Quick"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            sync_state_to_url()
            st.rerun()

    with b2:
        if st.button(ui["full_label"], use_container_width=True):
            st.session_state.test_type = "Full"
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            sync_state_to_url()
            st.rerun()

# ==============================================================================
# VIEW 2: QUESTIONNAIRE (WITH QUESTION JUMP GRID & TIME ESTIMATE METRICS)
# ==============================================================================
elif st.session_state.started and not st.session_state.completed:
    total_q = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]

    pct_complete = int(((idx + 1) / total_q) * 100)
    time_remaining = max(1, int((total_q - idx) * (0.32 if total_q == 25 else 0.25)))

    st.progress((idx + 1) / total_q)
    dim_name = q.get('dimension_hi' if is_hindi else 'dimension', q.get('dimension', ''))
    
    st.markdown(f"<div class='category-badge'>DIMENSION: {dim_name.upper()}</div>", unsafe_allow_html=True)
    st.caption(ui["progress_label"].format(current=idx + 1, total=total_q, pct=pct_complete, time_left=time_remaining))

    with st.expander("📌 Jump to Question Grid", expanded=False):
        cols_grid = st.columns(10)
        for q_num in range(1, total_q + 1):
            target_idx = q_num - 1
            q_id_check = raw_questions[target_idx]["id"]
            is_answered = q_id_check in st.session_state.answers
            btn_type = "primary" if is_answered else "secondary"
            if cols_grid[(q_num - 1) % 10].button(f"{q_num}", key=f"jump_{q_num}", type=btn_type, use_container_width=True):
                st.session_state.current_question_index = target_idx
                sync_state_to_url()
                st.rerun()

    q_text = q['text_hi'] if is_hindi and q.get('text_hi') else q['text_en']
    st.markdown(f"<h3 style='margin: 12px 0 24px 0; line-height: 1.4;'>{q_text}</h3>", unsafe_allow_html=True)

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
            if idx < total_q - 1:
                st.session_state.current_question_index += 1
            else:
                st.session_state.completed = True
            
            sync_state_to_url()
            st.rerun()

    st.write("")
    nav1, _, _ = st.columns([2, 6, 2])
    with nav1:
        if idx > 0 and st.button(ui["prev_btn"], use_container_width=True):
            st.session_state.current_question_index -= 1
            sync_state_to_url()
            st.rerun()

# ==============================================================================
# VIEW 3: PROFILE REVEAL & COMPREHENSIVE INSIGHTS DOSSIER
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
        <p style='max-width: 820px; margin: 15px auto; font-size: 1.05rem; line-height: 1.6;'>{desc}</p>
    </div>
    """, unsafe_allow_html=True)

    twin_data = PHILOSOPHER_QUOTES.get(top_match["name"], {
        "thinkers": [(t, round(1.0 / len(top_match.get("thinkers", [t])), 2)) for t in top_match.get("thinkers", ["Thinker"])],
        "quote": "“Truth emerges from the open dialectic of reason and experience.”"
    })

    st.markdown(f"### {ui['thinker_breakdown_title']}")
    th_cols = st.columns(len(twin_data["thinkers"]))
    for col, (thinker_name, weight) in zip(th_cols, twin_data["thinkers"]):
        with col:
            thinker_pct = round(top_match['similarity_pct'] * weight, 1)
            st.markdown(f"""
            <div class='highlight-card' style='text-align:center; padding:15px;'>
                <div style='font-size:1.4rem; color:#D4AF37;'>🏛️</div>
                <div style='font-weight:700; font-size:1.05rem;'>{thinker_name}</div>
                <div style='color:#38BDF8; font-weight:600; font-size:1.15rem; margin-top:4px;'>{thinker_pct}% Match</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin: 10px 0 25px 0; padding: 14px 20px; border-left: 3px solid #D4AF37; background: rgba(212, 175, 55, 0.06); border-radius: 4px;'>
        <span class='serif-quote' style='font-size: 1.05rem;'>{twin_data['quote']}</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.markdown(f"### {ui['affinities_label']}")
    st.caption("Detailed ranking of how your coordinates align with all major world traditions:")
    
    aff_cols = st.columns(3)
    for i, aff in enumerate(affinities[:6]):
        with aff_cols[i % 3]:
            nm = aff["name_hi"] if is_hindi else aff["name"]
            sim = aff['similarity_pct']
            tier = "Primary Match" if sim >= 80 else ("Strong Kinship" if sim >= 65 else "Moderate Alignment")
            st.markdown(f"""
            <div class='highlight-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <strong style='font-size:1.05rem;'>{nm}</strong>
                    <span style='color:#D4AF37; font-weight:700; font-size:1.1rem;'>{sim}%</span>
                </div>
                <div style='font-size:0.80rem; color:#38BDF8; margin: 4px 0 8px 0; text-transform:uppercase; letter-spacing:0.05em;'>{tier}</div>
                <div style='font-size:0.88rem; line-height:1.4; opacity:0.85;'>{aff.get('description', '')[:110]}...</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    r1, r2 = st.columns([5, 5])
    with r1:
        st.markdown(f"### {ui['char_title']}")
        
        dim_insights = [
            ("Metaphysics & Reality", user_coords[0], "Transcendence (+)" if user_coords[0] > 0 else "Physicalism (-)", "Evaluates whether reality is grounded in material laws or transcendent consciousness[cite: 5].", "Physicalism", "Transcendence"),
            ("Society & Structure", user_coords[1], "Collectivism (+)" if user_coords[1] > 0 else "Individualism (-)", "Balances communal solidarity (Ubuntu) against individual autonomy and liberty[cite: 5].", "Individualism", "Collectivism"),
            ("Culture & Evolution", user_coords[2], "Progressivism (+)" if user_coords[2] > 0 else "Traditionalism (-)", "Measures openness to technological reform vs. ancestral reverence and stability[cite: 5].", "Traditionalism", "Progressivism"),
            ("Epistemology & Truth", user_coords[3], "Empiricism (+)" if user_coords[3] > 0 else "Rationalism (-)", "Contrasts sensory, scientific observation with deductive logical axioms[cite: 5].", "Rationalism", "Empiricism")
        ]
        
        for name_dim, val_dim, leaning, explanation, pole_neg, pole_pos in dim_insights:
            pct_pos = int(((val_dim + 1.0) / 2.0) * 100)
            st.markdown(f"""
            <div class='dimension-box'>
                <div style='display:flex; justify-content:space-between; font-weight:700;'>
                    <span>{name_dim}</span>
                    <span style='color:#D4AF37;'>{val_dim:+.2f} ({leaning})</span>
                </div>
                <div class='gauge-track'>
                    <div class='gauge-fill' style='width: {pct_pos}%;'></div>
                </div>
                <div style='display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.75; text-transform:uppercase;'>
                    <span>{pole_neg} (-1.0)</span>
                    <span>{pole_pos} (+1.0)</span>
                </div>
                <div style='font-size:0.85rem; margin-top:6px; opacity:0.85; line-height:1.4;'>{explanation}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"**Profile Tags:** {' • '.join([f'`{t}`' for t in tags])}")
        st.markdown(f"**Canonical Thinkers:** {', '.join(top_match.get('thinkers', []))}")

    with r2:
        tab1, tab2 = st.tabs(["Radar Comparison", "3D Vector Space"])
        with tab1:
            st.plotly_chart(render_multi_radar_comparison(user_coords, [(top_match["name"], top_match["vector"])], st.session_state.theme), use_container_width=True, key="top_match_radar_chart")
        with tab2:
            st.plotly_chart(render_3d_scatter(user_coords, WORLDVIEWS), use_container_width=True, key="main_3d_scatter_chart")

    st.write("---")
    st.markdown(f"### {ui['comparison_title']}")
    matched_name = top_match["name"]
    st.caption(ui["comparison_sub"].format(matched_school=matched_name))
    
    available_schools = [s for s in WORLDVIEWS.keys() if s != matched_name]
    if available_schools:
        selected_comps = st.multiselect("Select traditions to compare (up to 2):", available_schools, default=[available_schools[0]], max_selections=2, key="comp_schools_multiselect")
        comp_pairs = [(s, WORLDVIEWS[s]["vector"]) for s in selected_comps]
        comp_pairs.insert(0, (matched_name, top_match["vector"]))

        c_col1, c_col2 = st.columns([6, 4])
        with c_col1:
            st.plotly_chart(render_multi_radar_comparison(user_coords, comp_pairs[1:], st.session_state.theme), use_container_width=True, key="multi_comp_radar_chart")
        with c_col2:
            st.markdown(f"**Primary Match: {matched_name}**")
            st.write(top_match.get("description", ""))
            for sc in selected_comps:
                st.markdown(f"**Compared: {sc}**")
                st.write(WORLDVIEWS[sc].get("description", ""))

    st.write("---")
    st.markdown(f"### {ui['matrix_title']}")
    st.caption(ui["matrix_sub"])

    friend_url_input = st.text_input("Friend's Shared URL:", placeholder="Paste your friend's URL here...", label_visibility="collapsed")
    
    if friend_url_input:
        try:
            parsed_query = urllib.parse.urlparse(friend_url_input).query
            params = urllib.parse.parse_qs(parsed_query)
            if "answers" in params:
                friend_answers_raw = urllib.parse.unquote(params["answers"][0])
                friend_answers = json.loads(friend_answers_raw)
                friend_coords = calculate_coordinates_direct(friend_answers, raw_questions, st.session_state.test_type)
                friend_affinities = calculate_affinities(friend_coords, WORLDVIEWS)
                friend_top = friend_affinities[0]

                dist = sum((u - f) ** 2 for u, f in zip(user_coords, friend_coords)) ** 0.5
                consensus_score = max(0.0, min(100.0, round((1.0 - (dist / 4.0)) * 100.0, 1)))

                axis_names = [
                    ("Metaphysics & Reality", abs(user_coords[0] - friend_coords[0])),
                    ("Society & Structure", abs(user_coords[1] - friend_coords[1])),
                    ("Culture & Evolution", abs(user_coords[2] - friend_coords[2])),
                    ("Epistemology & Truth", abs(user_coords[3] - friend_coords[3]))
                ]
                battleground_axis = max(axis_names, key=lambda x: x[1])[0]
                harmony_axis = min(axis_names, key=lambda x: x[1])[0]

                mat_col1, mat_col2 = st.columns([5, 5])
                with mat_col1:
                    st.markdown(f"""
                    <div class='highlight-card'>
                        <div style='font-size: 1.15rem; font-weight:700; color:#D4AF37;'>Consensus Score: {consensus_score}%</div>
                        <p style='margin: 8px 0;'><strong>Your Top Tradition:</strong> {top_match['name']}</p>
                        <p style='margin: 8px 0;'><strong>Friend's Top Tradition:</strong> {friend_top['name']}</p>
                        <p style='margin: 8px 0; color:#10B981;'><strong>🤝 Shared Common Ground:</strong> {harmony_axis}</p>
                        <p style='margin: 8px 0; color:#EF4444;'><strong>⚡ Prime Debate Battleground:</strong> {battleground_axis}</p>
                        <p style='margin: 10px 0 0 0; font-size:0.85rem; opacity:0.8; font-style:italic;'>💡 AI Debate Prompt: Given your divergence on {battleground_axis}, how do your foundational principles reconcile individual autonomy with collective welfare?</p>
                    </div>
                    """, unsafe_allow_html=True)
                with mat_col2:
                    st.plotly_chart(render_multi_radar_comparison(user_coords, [("Friend's Coordinates", friend_coords)], st.session_state.theme, "Your Coordinates"), use_container_width=True, key="friend_duel_radar")
            else:
                st.warning("Could not locate answers in the provided link. Please ensure the full URL is pasted.")
        except Exception:
            st.error("Error parsing friend's link. Please check that the URL was copied completely.")

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

    # 8. Unified Artifact Export & Share Hub
    st.write("---")
    st.markdown(f"### {ui['share_heading']}")
    st.caption(ui["share_sub"])

    custom_handle_input = st.text_input("Custom Handle / Name for Identity Card (Optional):", placeholder="e.g. Philosopher Jane", key="custom_badge_handle")

    passport_bytes = generate_hd_passport(user_coords, top_match, tags, affinities, tensions, custom_handle_input)

    share_msg = f"I took the Worldview Compass test and matched {top_match['similarity_pct']}% with {top_match['name']}! Discover your philosophical profile here:"
    encoded_share_msg = urllib.parse.quote(share_msg)

    x_url = f"https://twitter.com/intent/tweet?text={encoded_share_msg}"
    wa_url = f"https://api.whatsapp.com/send?text={encoded_share_msg}"
    li_url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://share.streamlit.io"

    x_icon = """<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>"""
    wa_icon = """<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.196 8.196 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24"/></svg>"""
    li_icon = """<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93zM6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37z"/></svg>"""

    # Uniform Layout: Social Buttons & High-Res Download Button Aligned in a Single Row
    sh1, sh2, sh3, sh4 = st.columns(4)
    with sh1:
        st.markdown(f"<a href='{x_url}' target='_blank' class='social-btn' style='width: 100%;'>{x_icon} Share on X</a>", unsafe_allow_html=True)
    with sh2:
        st.markdown(f"<a href='{wa_url}' target='_blank' class='social-btn' style='width: 100%;'>{wa_icon} Share on WhatsApp</a>", unsafe_allow_html=True)
    with sh3:
        st.markdown(f"<a href='{li_url}' target='_blank' class='social-btn' style='width: 100%;'>{li_icon} Share on LinkedIn</a>", unsafe_allow_html=True)
    with sh4:
        st.download_button(
            label="Download Identity Card (PNG) 🎫",
            data=passport_bytes,
            file_name=f"worldview_identity_card_{top_match.get('slug', 'result')}.png",
            mime="image/png",
            use_container_width=True,
            type="primary"
        )