"""
Worldview Compass — redesigned Streamlit presentation layer.

The scoring/data model remains in database.py and engine.py. This file focuses
on a cleaner, responsive and accessible experience around that existing model.
"""
import os
import sys
import json
import base64
import urllib.parse
from io import BytesIO
from html import escape

import streamlit as st
import plotly.graph_objects as go
from PIL import Image, ImageDraw

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from database import WORLDVIEWS, load_questions_dataset
from engine import (
    calculate_coordinates_direct,
    calculate_affinities,
    characterize_profile,
    check_tensions,
)

st.set_page_config(
    page_title="Worldview Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Worldview Compass — a non-clinical philosophical identity exploration."
    },
)

# ---------------------------------------------------------------------------
# Content/data
# ---------------------------------------------------------------------------
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

UI_TEXT = {
    "English": {
        "title": "Worldview Compass",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "An intellectually serious, non-judgmental exploration of your foundational assumptions. Discover your coordinates in a 4D philosophical spectrum and trace your affinities to major global traditions.",
        "quick_title": "⚡ Quick Odyssey",
        "quick_desc": "25 Questions • ~8 mins\nSamples 1 question per core dimension for an efficient diagnostic.",
        "full_title": "🏛️ Full Odyssey",
        "full_desc": "100 Questions • ~25 mins\nComprehensive assessment across all 100 questions for maximum precision.",
        "progress_label": "Question {current} of {total} ({pct}% complete • ~{time_left} mins remaining)",
        "prev_btn": "← Previous",
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
        "passport_btn": "Download Identity Card (PNG) 🎫",
        "depth_heading": "Choose your depth",
        "depth_caption": "Select an option below to begin your assessment immediately.",
        "footer_note": "Your result is a philosophical profile, not a clinical or psychological diagnosis.",
        "ans_caption": "Choose the answer that best represents your view. There is no “correct” answer.",
        "ans_auto": "Selecting an answer automatically advances to the next question.",
        "jump_label": "Jump to a question",
        "radar_space_tab": ["4D radar", "3D worldview space"],
        "traditions_compare_label": "Traditions to compare (up to 3)",
        "friend_url_label": "Friend's shared URL",
        "friend_url_placeholder": "Paste a Worldview Compass share URL",
        "badge_handle_label": "Name for identity card (optional)",
        "badge_handle_placeholder": "e.g. Philosopher Jane",
        "summary_expand_label": "📖 Explore the 25 Philosophical Dimensions & Reference Traditions",
        "core_dims_heading": "Core Assessment Dimensions",
        "ref_traditions_heading": "13 Reference Traditions"
    },
    "Hindi": {
        "title": "विचार कम्पास",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें और प्रमुख वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "quick_title": "⚡ त्वरित यात्रा",
        "quick_desc": "25 प्रश्न • ~8 मिनट\nत्वरित मूल्यांकन के लिए 25 मूल आयामों से 1 प्रतिनिधि प्रश्न।",
        "full_title": "🏛️ पूर्ण यात्रा",
        "full_desc": "100 प्रश्न • ~25 मिनट\nसमग्र विश्लेषण के लिए सभी 100 प्रश्नों का विस्तृत मूल्यांकन।",
        "progress_label": "प्रश्न {current} का {total} ({pct}% पूर्ण • ~{time_left} मिनट शेष)",
        "prev_btn": "← पिछला",
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
        "passport_btn": "पहचान पत्र डाउनलोड करें (PNG) 🎫",
        "depth_heading": "अपना मूल्यांकन चुनें",
        "depth_caption": "अपना मूल्यांकन तुरंत शुरू करने के लिए नीचे एक विकल्प चुनें।",
        "footer_note": "आपका परिणाम एक दार्शनिक प्रोफ़ाइल है, न कि कोई चिकित्सीय या मनोवैज्ञानिक निदान।",
        "ans_caption": "वह उत्तर चुनें जो आपके दृष्टिकोण को सर्वोत्तम रूप से व्यक्त करता हो। कोई भी 'सही' उत्तर नहीं है।",
        "ans_auto": "उत्तर चुनने पर स्वतः ही अगले प्रश्न पर पहुंच जाएंगे।",
        "jump_label": "किसी प्रश्न पर जाएं",
        "radar_space_tab": ["4डी रडार", "3डी विश्वदृष्टिकोण अंतरिक्ष"],
        "traditions_compare_label": "तुलना के लिए परंपराएं (अधिकतम 3)",
        "friend_url_label": "मित्र का शेयर किया गया लिंक",
        "friend_url_placeholder": "विश्वदृष्टिकोण कम्पास शेयर लिंक यहाँ पेस्ट करें",
        "badge_handle_label": "पहचान पत्र के लिए नाम (वैकल्पिक)",
        "badge_handle_placeholder": "उदा. दार्शनिक जेन",
        "summary_expand_label": "📖 25 दार्शनिक आयामों और संदर्भ परंपराओं का अन्वेषण करें",
        "core_dims_heading": "मुख्य मूल्यांकन आयाम",
        "ref_traditions_heading": "13 संदर्भ परंपराएं"
    }
}

HOMEPAGE_SECTIONS = [
    {
        "icon": "🌌",
        "title_en": "Metaphysics & Mind",
        "title_hi": "तत्वमीमांसा और मन",
        "desc_en": "Examines reality's fundamental fabric, consciousness, and free will vs determinism.",
        "desc_hi": "वास्तविकता के मूल स्वरूप, चेतना और स्वतंत्र इच्छा का अन्वेषण करता है."
    },
    {
        "icon": "⚖️",
        "title_en": "Ethics & Society",
        "title_hi": "नैतिकता और समाज",
        "desc_en": "Maps moral virtue, relational duties (Ubuntu), and systemic governance models.",
        "desc_hi": "नैतिक कर्तव्यों, सामुदायिक संबंधों और शासन प्रणालियों का विश्लेषण करता है."
    },
    {
        "icon": "🌱",
        "title_en": "Ecology & Future",
        "title_hi": "पारिस्थितिकी और भविष्य",
        "desc_en": "Surveys biocentric environmental ethics, animal sentience, and AI horizons.",
        "desc_hi": "पर्यावरण नैतिकता, पशु अधिकार और कृत्रिम बुद्धिमत्ता का विश्लेषण करता है."
    }
]

def generate_hd_passport(user_coords, top_affinity, character_tags, affinities, tensions, custom_handle=""):
    w, h = 1200, 1800
    img = Image.new("RGB", (w, h), (246, 243, 236))
    draw = ImageDraw.Draw(img)
    from PIL import ImageFont
    
    regular = next((x for x in [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ] if os.path.exists(x)), None)
    
    bold = next((x for x in [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ] if os.path.exists(x)), regular)

    def F(size, heavy=False):
        return ImageFont.truetype(bold if heavy else regular, size) if regular else ImageFont.load_default()

    gold = (166, 120, 40)
    ink = (27, 39, 54)
    muted = (92, 105, 120)
    blue = (22, 125, 175)
    line = (220, 212, 196)

    draw.rounded_rectangle([24, 24, w-24, h-24], radius=28, fill=(250, 248, 243), outline=gold, width=4)
    draw.rounded_rectangle([42, 42, w-42, h-42], radius=22, outline=(177, 185, 191), width=1)
    draw.rectangle([43, 43, w-43, 53], fill=gold)
    draw.rectangle([43, h-53, w-43, h-43], fill=gold)

    # Header - optimized font sizing for high-res readability
    draw.rounded_rectangle([75, 75, w-75, 215], radius=18, fill=(255, 253, 248), outline=line, width=1)
    draw.text((105, 95), "WORLDVIEW COMPASS", fill=gold, font=F(40, True))
    sub = f"PHILOSOPHICAL IDENTITY  •  {custom_handle.upper()}" if custom_handle else "PHILOSOPHICAL IDENTITY SPECIFICATION"
    draw.text((105, 150), sub, fill=muted, font=F(22))
    draw.text((w-105, 115), "◈", fill=gold, font=F(52, True), anchor="ra")

    # Match card - optimized typography
    draw.rounded_rectangle([75, 250, w-75, 455], radius=22, fill=(255, 255, 255), outline=gold, width=2)
    draw.text((w//2, 290), top_affinity["name"].upper(), fill=ink, font=F(42, True), anchor="ma")
    draw.text((w//2, 355), f"{top_affinity['similarity_pct']}%  MATCH AFFINITY", fill=blue, font=F(30, True), anchor="ma")
    
    desc = top_affinity.get("description", "")
    words = desc.split()
    lines = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
        if len(test) > 68:
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur:
        lines.append(cur)
    for i, line_text in enumerate(lines[:2]):
        draw.text((w//2, 400 + i * 28), line_text, fill=muted, font=F(20), anchor="ma")

    # Dimensions Section - clear spacing and scaling
    draw.text((75, 485), "04  •  DIMENSIONAL POLARITY", fill=gold, font=F(26, True))
    labels = [
        ("Metaphysics", "Physicalism", "Transcendence", user_coords[0]),
        ("Society", "Individualism", "Collectivism", user_coords[1]),
        ("Culture", "Traditionalism", "Progressivism", user_coords[2]),
        ("Epistemology", "Rationalism", "Empiricism", user_coords[3])
    ]
    for i, (name, neg, pos, val) in enumerate(labels):
        y = 535 + i * 105
        draw.text((75, y), name, fill=ink, font=F(22, True))
        draw.text((w-75, y), f"{val:+.2f}", fill=gold, font=F(22, True), anchor="ra")
        x1, x2 = 75, w-75
        yy = y + 36
        draw.rounded_rectangle([x1, yy, x2, yy+16], radius=6, fill=line)
        nx = x1 + int(((val + 1) / 2) * (x2 - x1))
        draw.rounded_rectangle([x1, yy, max(x1 + 12, nx), yy + 16], radius=6, fill=gold)
        draw.text((x1, yy + 20), neg, fill=muted, font=F(16))
        draw.text((x2, yy + 20), pos, fill=muted, font=F(16), anchor="ra")

    # Affinities
    draw.text((75, 975), "TOP LINEAGE AFFINITIES", fill=gold, font=F(26, True))
    for i, a in enumerate(affinities[:4]):
        y = 1025 + i * 65
        nm = a["name"]
        draw.text((75, y), f"{i+1:02d}  {nm}", fill=ink, font=F(20, True))
        draw.text((w-75, y), f"{a['similarity_pct']}%", fill=blue, font=F(20, True), anchor="ra")
        draw.rounded_rectangle([175, y + 30, w-75, y + 38], radius=4, fill=line)
        nx = 175 + int(((w - 250) * a['similarity_pct']) / 100)
        draw.rounded_rectangle([175, y + 30, max(180, nx), y + 38], radius=4, fill=blue)

    # Attributes / tension
    draw.text((75, 1315), "PROFILE ATTRIBUTES", fill=gold, font=F(26, True))
    attr = "  •  ".join(character_tags)
    words = attr.split()
    lines = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
        if len(test) > 72:
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur:
        lines.append(cur)
    for i, l in enumerate(lines[:2]):
        draw.text((75, 1360 + i * 32), l, fill=ink, font=F(20))
        
    thinkers = ", ".join(top_affinity.get("thinkers", [])[:3])
    draw.text((75, 1435), f"Canonical thinkers: {thinkers}", fill=muted, font=F(18))
    draw.text((75, 1495), "DIALECTICAL CONSISTENCY", fill=gold, font=F(26, True))
    summary = (tensions[0]["title"] if tensions else "No major structural tensions detected • high internal consistency")
    draw.text((75, 1540), summary[:85], fill=(153, 86, 25) if tensions else blue, font=F(19, True))

    # Footer / watermark
    draw.text((w//2, h - 75), "NON-CLINICAL • EXPLORATORY • WORLDVIEW COMPASS", fill=(130, 139, 148), font=F(16, True), anchor="mm")
    
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

# ---------------------------------------------------------------------------
# Cached helpers
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_questions_dataset(mode: str):
    return load_questions_dataset(mode=mode)


@st.cache_data(show_spinner=False)
def build_profile(answers_json: str, questions_json: str, test_type: str, language: str):
    answers = json.loads(answers_json)
    questions = json.loads(questions_json)
    coords = calculate_coordinates_direct(answers, questions, test_type)
    affinities = calculate_affinities(coords, WORLDVIEWS)
    tags = characterize_profile(coords, language)
    tensions = check_tensions(answers, language)
    return coords, affinities, tags, tensions


@st.cache_data(show_spinner=False)
def cached_passport(coords_json: str, top_json: str, tags_json: str, affinities_json: str, tensions_json: str, handle: str):
    return generate_hd_passport(
        json.loads(coords_json),
        json.loads(top_json),
        json.loads(tags_json),
        json.loads(affinities_json),
        json.loads(tensions_json),
        handle,
    )


def get_base64_logo():
    for path in (
        os.path.join(current_dir, "app_logo.png"),
        "/mnt/data/app_logo.png",
        "/workspace/app_logo.png",
        "app_logo.png",
    ):
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except OSError:
                continue
    return None


# ---------------------------------------------------------------------------
# Theme & CSS Styling (Mobile & Devanagari Responsive Overhaul)
# ---------------------------------------------------------------------------
def inject_theme(theme="Dark", dim_idx=0):
    palettes = {
        "Dark": {"bg":"#08111F","surface":"rgba(15,28,45,.86)","surface2":"#102238","text":"#F4F7FB","muted":"#AAB8C8","gold":"#D8B25C","gold_soft":"rgba(216,178,92,.13)","border":"rgba(216,178,92,.24)","line":"#263B52","shadow":"0 20px 60px rgba(0,0,0,.30)","input":"#0C1A2B","accent":"#38BDF8"},
        "Light": {"bg":"#F4F7FB","surface":"rgba(255,255,255,.94)","surface2":"#FFFFFF","text":"#102033","muted":"#566579","gold":"#76530D","gold_soft":"rgba(118,83,13,.09)","border":"rgba(118,83,13,.20)","line":"#D9E0E8","shadow":"0 16px 42px rgba(31,41,55,.09)","input":"#FFFFFF","accent":"#0284C7"},
        "Ivory": {"bg":"#F5F0E6","surface":"rgba(255,252,245,.93)","surface2":"#FFFDF8","text":"#2C2418","muted":"#716453","gold":"#A06B1C","gold_soft":"rgba(160,107,28,.10)","border":"rgba(160,107,28,.22)","line":"#DED4C3","shadow":"0 16px 42px rgba(76,56,28,.10)","input":"#FFFCF5","accent":"#B7791F"},
        "Ocean": {"bg":"#061A22","surface":"rgba(8,35,45,.88)","surface2":"#0B2935","text":"#E9FAFF","muted":"#9FC3CC","gold":"#62D5D1","gold_soft":"rgba(98,213,209,.12)","border":"rgba(98,213,209,.23)","line":"#1D4652","shadow":"0 20px 60px rgba(0,0,0,.28)","input":"#08232D","accent":"#38BDF8"},
    }
    theme = theme if theme in palettes else "Dark"
    p = palettes[theme]
    dark = theme in ("Dark", "Ocean")
    tint_mode = "dark" if dark else "light"
    active_tint = DIMENSION_TINTS.get(dim_idx, {}).get(tint_mode, "transparent")
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');
    :root {{ --wc-bg:{p['bg']}; --wc-surface:{p['surface']}; --wc-surface2:{p['surface2']}; --wc-text:{p['text']}; --wc-muted:{p['muted']}; --wc-gold:{p['gold']}; --wc-gold-soft:{p['gold_soft']}; --wc-border:{p['border']}; --wc-line:{p['line']}; --wc-shadow:{p['shadow']}; --wc-input:{p['input']}; --wc-accent:{p['accent']}; }}
    html,body,[data-testid="stAppViewContainer"] {{ background:var(--wc-bg)!important; }}
    .stApp {{ background:radial-gradient(circle at 50% -10%, {active_tint} 0%, transparent 42%),var(--wc-bg)!important; color:var(--wc-text)!important; font-family:'Inter','Noto Sans Devanagari',sans-serif!important; }}
    [data-testid="stHeader"] {{ background:transparent!important; }}
    .block-container {{ max-width:1180px!important; padding:1.1rem 1.2rem 4rem!important; }}
    h1,h2,h3,h4 {{ color:var(--wc-text)!important; font-family:'Inter','Noto Sans Devanagari',sans-serif!important; }}
    p,li,label,[data-testid="stCaptionContainer"] {{ color:var(--wc-muted); font-family:'Inter','Noto Sans Devanagari',sans-serif!important; }}
    
    .wc-brand {{ display:flex;align-items:center;gap:.72rem;font-family:'Cinzel',serif;font-weight:700;letter-spacing:.055em;color:var(--wc-text);font-size:1.05rem; }}
    .wc-brand img {{ width:38px;height:38px;object-fit:cover;border-radius:10px;border:1px solid var(--wc-border);box-shadow:var(--wc-shadow); }}
    .wc-kicker {{ color:var(--wc-gold);text-transform:uppercase;letter-spacing:.13em;font-size:.72rem;font-weight:800; }}
    .wc-hero {{ border:1px solid var(--wc-border);border-radius:28px;padding:clamp(1.4rem,4vw,3.2rem);background:linear-gradient(135deg,var(--wc-surface),var(--wc-gold-soft));box-shadow:var(--wc-shadow);margin:.7rem 0 1.1rem;animation:wcIn .45s ease both; }}
    .wc-hero h1 {{ font-family:'Cinzel',serif!important;font-size:clamp(2rem,5vw,3.7rem)!important;line-height:1.08;letter-spacing:.025em;margin:.35rem 0 .55rem; }}
    .wc-hero .lead {{ max-width:780px;font-size:1.05rem;line-height:1.7;margin:0 0 1.25rem; }}
    .wc-quote {{ font-family:'Lora',serif;font-style:italic;color:var(--wc-muted); }}
    
    .wc-card {{ border:1px solid var(--wc-border);border-radius:18px;background:linear-gradient(145deg,var(--wc-surface),rgba(255,255,255,.015));box-shadow:var(--wc-shadow);padding:1.05rem 1.1rem;height:100%;transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease; }}
    .wc-card h3 {{ margin:.1rem 0 .45rem;font-size:1.03rem; }} .wc-card p {{ margin:0;line-height:1.55;font-size:.91rem; }}
    .wc-section {{border-top:1px solid var(--wc-line);padding-top:1.25rem;margin-top:1.25rem;}}
    .wc-result {{border:1px solid var(--wc-border);border-radius:24px;background:linear-gradient(145deg,var(--wc-surface),var(--wc-gold-soft));padding:1.5rem;box-shadow:var(--wc-shadow);animation:wcIn .45s ease both;}}
    .wc-result .match {{color:var(--wc-gold);font-family:'Cinzel',serif;font-size:clamp(1.9rem,4vw,3rem);font-weight:700;line-height:1.15;}}
    
    .wc-dim {{border:1px solid var(--wc-border);border-radius:16px;padding:1rem;background:var(--wc-surface);margin:.65rem 0;}}
    .wc-dim-head {{display:flex;justify-content:space-between;gap:1rem;font-weight:700;}}
    .wc-gauge {{height:9px;background:var(--wc-line);border-radius:99px;overflow:hidden;margin:.7rem 0 .45rem;}}
    .wc-gauge>span {{display:block;height:100%;background:linear-gradient(90deg,var(--wc-accent),var(--wc-gold));border-radius:99px;}}
    .wc-poles {{display:flex;justify-content:space-between;gap:1rem;font-size:.72rem;color:var(--wc-muted);}}
    .wc-small {{font-size:.82rem;color:var(--wc-muted);line-height:1.5;}}
    .wc-pill {{display:inline-flex;align-items:center;border:1px solid var(--wc-border);border-radius:999px;padding:.3rem .65rem;font-size:.73rem;font-weight:700;color:var(--wc-gold);background:var(--wc-gold-soft);}}
    .wc-footer {{text-align:center;color:var(--wc-muted);font-size:.76rem;padding-top:2rem;}}
    
    /* Uniform Header Tiles & Streamlined Mobile Toolbar */
    div[data-testid="stButton"]>button,div[data-testid="stDownloadButton"]>button {{border-radius:14px!important;border:1px solid var(--wc-border)!important;min-height:44px!important;background:var(--wc-surface)!important;color:var(--wc-text)!important;box-shadow:var(--wc-shadow)!important;transition:all .2s ease!important;font-family:'Inter','Noto Sans Devanagari',sans-serif!important;}} 
    div[data-testid="stButton"]>button:hover,div[data-testid="stDownloadButton"]>button:hover {{transform:translateY(-2px);border-color:var(--wc-gold)!important;box-shadow:0 0 15px var(--wc-gold-soft)!important;}}
    .wc-header-tile {{border:1px solid var(--wc-border);border-radius:14px;background:var(--wc-surface);padding:.25rem;text-align:center;box-shadow:var(--wc-shadow);}}

    /* Golden twin border aesthetic for depth selection tiles */
    .wc-depth-tile {{border:3px double var(--wc-gold)!important;border-radius:20px!important;padding:1.4rem!important;background:linear-gradient(145deg,var(--wc-surface),var(--wc-gold-soft))!important;box-shadow:var(--wc-shadow)!important;transition:transform .2s ease,border-color .2s ease;}}
    .wc-depth-tile:hover {{transform:translateY(-3px);border-color:var(--wc-accent)!important;}}

    /* Full width options layout & robust Hindi text wrapping */
    div[data-testid="stRadio"] {{width:100%!important;}}
    div[data-testid="stRadio"] label {{border:1px solid var(--wc-border);border-radius:14px;padding:.85rem 1.1rem;margin:.4rem 0;background:var(--wc-surface);display:flex!important;width:100%!important;white-space:normal!important;word-break:break-word!important;overflow-wrap:break-word!important;line-height:1.6!important;transition:border-color .15s ease,background .15s ease;}} 
    div[data-testid="stRadio"] label:hover {{border-color:var(--wc-gold);background:var(--wc-gold-soft);}}

    .wc-social-btn {{display:inline-flex;align-items:center;justify-content:center;gap:.4rem;min-height:42px;padding:.55rem .7rem;border-radius:10px;text-decoration:none!important;font-weight:700;font-size:.82rem;border:1px solid var(--wc-border);}}
    .wc-x {{background:#000;color:#fff!important;}} .wc-wa {{background:#25D366;color:#fff!important;}} .wc-li {{background:#0A66C2;color:#fff!important;}}
    div[data-testid="stTextInput"] input,div[data-testid="stNumberInput"] input {{background:var(--wc-input)!important;color:var(--wc-text)!important;}}
    div[data-testid="stExpander"] {{border-color:var(--wc-border)!important;background:var(--wc-surface)!important;border-radius:14px!important;}}
    
    @keyframes wcIn {{from {{opacity:0;transform:translateY(8px)}}to {{opacity:1;transform:translateY(0)}}}}
    @media(max-width:720px) {{
        .block-container{{padding:.5rem .5rem 2.5rem!important;}}
        .wc-brand span:last-child{{font-size:.85rem;}}
        div[data-testid="stHorizontalBlock"] {{flex-wrap:wrap!important;gap:.4rem!important;}}
    }}
    </style>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# State / URL Management
# ---------------------------------------------------------------------------
def set_state(**changes):
    for key, value in changes.items():
        st.session_state[key] = value


def sync_state_to_url():
    try:
        st.query_params.update({
            "started": str(st.session_state.started).lower(),
            "completed": str(st.session_state.completed).lower(),
            "test_type": st.session_state.test_type,
            "q_idx": str(st.session_state.current_question_index),
            "lang": st.session_state.language,
            "theme": st.session_state.theme,
            "answers": json.dumps(st.session_state.answers, separators=(",", ":")),
        })
    except Exception:
        pass


def restore_state_from_url():
    try:
        params = st.query_params
        if params.get("home") == "1":
            st.session_state.started = False
            st.session_state.completed = False
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.comparison_schools = []
            st.session_state.friend_url = ""
            if params.get("lang") in ("English", "Hindi"):
                st.session_state.language = params.get("lang")
            if params.get("theme") in ("Dark", "Light", "Ivory", "Ocean"):
                st.session_state.theme = params.get("theme")
            st.query_params.clear()
            st.query_params.update({
                "started": "false",
                "completed": "false",
                "test_type": st.session_state.test_type,
                "q_idx": "0",
                "lang": st.session_state.language,
                "theme": st.session_state.theme,
                "answers": "{}",
            })
            return
        if params.get("started") is not None:
            st.session_state.started = str(params.get("started")).lower() == "true"
        if params.get("completed") is not None:
            st.session_state.completed = str(params.get("completed")).lower() == "true"
        if params.get("test_type") in ("Quick", "Full"):
            st.session_state.test_type = params.get("test_type")
        if params.get("q_idx") is not None:
            st.session_state.current_question_index = max(0, int(params.get("q_idx")))
        if params.get("lang") in ("English", "Hindi"):
            st.session_state.language = params.get("lang")
        if params.get("theme") in ("Dark", "Light", "Ivory", "Ocean"):
            st.session_state.theme = params.get("theme")
        if params.get("answers"):
            decoded = urllib.parse.unquote(params.get("answers"))
            loaded = json.loads(decoded)
            if isinstance(loaded, dict):
                st.session_state.answers = {int(k): str(v) for k, v in loaded.items()}
    except (ValueError, TypeError, json.JSONDecodeError):
        return


def init_state():
    defaults = {
        "answers": {},
        "current_question_index": 0,
        "test_type": "Quick",
        "language": "English",
        "theme": "Dark",
        "started": False,
        "completed": False,
        "url_rehydrated": False,
        "confidence": 50,
        "custom_badge_handle": "",
        "comparison_schools": [],
        "friend_url": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state.url_rehydrated:
        restore_state_from_url()
        st.session_state.url_rehydrated = True


init_state()
raw_questions = get_cached_questions_dataset(st.session_state.test_type.lower())
if not raw_questions:
    st.error("The question dataset could not be loaded." if st.session_state.language == "English" else "प्रश्न डेटासेट लोड नहीं किया जा सका।")
    st.stop()

if st.session_state.current_question_index >= len(raw_questions):
    st.session_state.current_question_index = len(raw_questions) - 1

active_dim_idx = 0
if st.session_state.started and not st.session_state.completed:
    active_dim_idx = raw_questions[st.session_state.current_question_index].get("dimIndex", 0)

inject_theme(st.session_state.theme, active_dim_idx)
ui = UI_TEXT[st.session_state.language]
is_hindi = st.session_state.language == "Hindi"


# ---------------------------------------------------------------------------
# Header — Streamlined Uniform Toolbar with House Icon & Alternate Language Toggle
# ---------------------------------------------------------------------------
logo = get_base64_logo()
c1, c2, c3, c4 = st.columns([4.6, 1.8, 1.8, 1.8], gap="small")
with c1:
    if logo:
        st.markdown(f'<div class="wc-brand"><img src="data:image/png;base64,{logo}"><span>WORLDVIEW COMPASS</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="wc-brand"><span style="font-size:1.4rem">🧭</span><span>{"विचार कम्पास" if is_hindi else "WORLDVIEW COMPASS"}</span></div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="wc-header-tile">', unsafe_allow_html=True)
    toggle_label = "🌐 English" if is_hindi else "🌐 हिन्दी"
    if st.button(toggle_label, key="lang_toggle_btn", use_container_width=True, help="Switch language / भाषा बदलें"):
        st.session_state.language = "English" if is_hindi else "Hindi"
        sync_state_to_url()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="wc-header-tile">', unsafe_allow_html=True)
    theme_order = ["Dark", "Light", "Ivory", "Ocean"]
    theme_icons = {"Dark":"🌙 Dark", "Light":"☀️ Light", "Ivory":"◐ Ivory", "Ocean":"🌊 Ocean"}
    current_theme = st.session_state.theme if st.session_state.theme in theme_order else "Dark"
    if st.button(theme_icons[current_theme], key="theme_cycle_btn", use_container_width=True, help=f"Theme: {current_theme} — click to change"):
        st.session_state.theme = theme_order[(theme_order.index(current_theme)+1)%len(theme_order)]
        sync_state_to_url()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="wc-header-tile">', unsafe_allow_html=True)
    if st.button("🏠 Home", key="home_icon_btn", use_container_width=True, help="Return to Home"):
        st.session_state.completed = False
        st.session_state.started = False
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        st.session_state.comparison_schools = []
        st.session_state.friend_url = ""
        sync_state_to_url()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="wc-section" style="padding-top:.2rem;margin-top:.2rem"></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HOME VIEW
# ---------------------------------------------------------------------------
if not st.session_state.started and not st.session_state.completed:
    st.markdown(
        f"""
        <section class="wc-hero">
          <div class="wc-kicker">{"मानचित्र, कोई अंतिम फैसला नहीं" if is_hindi else "A map, not a verdict"}</div>
          <h1>{escape(ui["title"])}</h1>
          <div class="wc-quote" style="font-size:1.1rem">“{escape(ui["subtitle"])}”</div>
          <p class="lead">{escape(ui["tagline"])}</p>
          <span class="wc-pill">{"25D → 4D नैदानिक स्पेक्ट्रम" if is_hindi else "25D → 4D diagnostic spectrum"}</span>
          <span class="wc-pill" style="margin-left:.35rem">{"हिंदी + English" if is_hindi else "English + हिन्दी"}</span>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.subheader(ui["depth_heading"])
    st.caption(ui["depth_caption"])

    m1, m2 = st.columns(2)
    with m1:
        st.markdown('<div class="wc-depth-tile">', unsafe_allow_html=True)
        if st.button(f"{ui['quick_title']}\n\n{ui['quick_desc']}", key="start_quick_tile", use_container_width=True, type="primary"):
            set_state(test_type="Quick", started=True, completed=False, current_question_index=0, answers={})
            sync_state_to_url()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="wc-depth-tile">', unsafe_allow_html=True)
        if st.button(f"{ui['full_title']}\n\n{ui['full_desc']}", key="start_full_tile", use_container_width=True):
            set_state(test_type="Full", started=True, completed=False, current_question_index=0, answers={})
            sync_state_to_url()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)

    with st.expander(ui["summary_expand_label"], expanded=False):
        col_sum1, col_sum2 = st.columns(2)
        with col_sum1:
            st.markdown(f"### 🧭 {ui['core_dims_heading']}")
            st.markdown("""
            * **Metaphysics, Reality & Mind:** Consciousness, Free Will, Determinism, and Epistemology.
            * **Ethics & Agency:** Virtue Ethics, Consequentialism, Deontology, and Care Ethics.
            * **Society & Governance:** Authority, Social Contracts, Classical Liberalism, and Egalitarianism.
            * **Ecology & Frontiers:** Deep Ecology, Animal Sentience, Artificial General Intelligence, and Longtermism.
            """)
        with col_sum2:
            st.markdown(f"### 🏛️ {ui['ref_traditions_heading']}")
            st.markdown("""
            * **Eastern Traditions:** Advaita Vedanta, Daoism, Early Buddhism, Confucianism.
            * **Western Lineages:** Stoicism, Christian Theism, Classical Liberalism, Marxism, Existentialism.
            * **Contemporary Movements:** Secular Scientific Humanism, Deep Ecology, Ubuntu, Transhumanism.
            """)

    st.markdown(
        f'<div class="wc-footer">{escape(ui["footer_note"])}</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# QUESTIONNAIRE VIEW
# ---------------------------------------------------------------------------
elif st.session_state.started and not st.session_state.completed:
    total = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]
    qid = q["id"]
    progress = (idx + 1) / total
    pct = int(progress * 100)
    answered = len(st.session_state.answers)

    progress_txt = f"प्रश्न {idx + 1} का {total}" if is_hindi else f"Question {idx + 1} of {total}"
    progress_sub = f"{pct}% पूर्ण • {answered} उत्तर दिए गए" if is_hindi else f"{pct}% complete • {answered} answered"

    st.markdown(
        f"""
        <div class="wc-progress-label" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:.3rem;">
          <strong>{escape(progress_txt)}</strong>
          <span>{escape(progress_sub)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(progress)

    dim_name = q.get("dimension_hi") if is_hindi and q.get("dimension_hi") else q.get("dimension", "")
    q_text = q.get("text_hi") if is_hindi and q.get("text_hi") else q.get("text_en", "")
    options = q.get("options", [])

    st.markdown(f'<span class="wc-pill">{escape(str(dim_name))}</span>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="width:100%;margin:1rem 0 .5rem;"><h2 style="font-size:clamp(1.1rem,2.4vw,1.7rem);line-height:1.4">{escape(q_text)}</h2></div>',
        unsafe_allow_html=True,
    )
    st.caption(ui["ans_caption"])

    labels = []
    code_by_label = {}
    for opt in options:
        txt = opt.get("text_hi") if is_hindi and opt.get("text_hi") else opt.get("text_en", "")
        label = f"{opt['code']}  —  {txt}"
        labels.append(label)
        code_by_label[label] = opt["code"]

    current_code = st.session_state.answers.get(qid)
    current_label = next((lbl for lbl, code in code_by_label.items() if code == current_code), None)
    radio_key = f"answer_radio_{st.session_state.test_type}_{qid}_{st.session_state.language}"

    def _auto_advance_answer():
        chosen = st.session_state.get(radio_key)
        if not chosen:
            return
        st.session_state.answers[qid] = code_by_label[chosen]
        if idx >= total - 1:
            st.session_state.completed = True
        else:
            st.session_state.current_question_index = idx + 1
        sync_state_to_url()

    st.radio(
        "Answer choices",
        labels,
        index=(labels.index(current_label) if current_label in labels else None),
        key=radio_key,
        label_visibility="collapsed",
        on_change=_auto_advance_answer,
    )

    st.caption(ui["ans_auto"])

    with st.expander(ui["jump_label"], expanded=False):
        num_cols = 5 if total <= 25 else 8
        grid_cols = st.columns(num_cols)
        for n in range(total):
            qn = n + 1
            q_id_check = raw_questions[n]["id"]
            marker = "✓ " if q_id_check in st.session_state.answers else ""
            with grid_cols[n % num_cols]:
                if st.button(
                    f"{marker}{qn}",
                    key=f"jump_{st.session_state.test_type}_{qn}",
                    use_container_width=True,
                    type="primary" if qn == idx + 1 else "secondary",
                ):
                    chosen_label = st.session_state.get(radio_key)
                    if chosen_label in code_by_label:
                        st.session_state.answers[qid] = code_by_label[chosen_label]
                    st.session_state.current_question_index = n
                    sync_state_to_url()
                    st.rerun()

    if idx > 0:
        if st.button(ui["prev_btn"], use_container_width=True, key=f"prev_{st.session_state.test_type}_{qid}"):
            st.session_state.current_question_index = max(0, idx - 1)
            sync_state_to_url()
            st.rerun()


# ---------------------------------------------------------------------------
# RESULTS VIEW (Anchor reset to top, Categorized sections)
# ---------------------------------------------------------------------------
elif st.session_state.completed:
    st.markdown('<span id="results-top"></span>', unsafe_allow_html=True)
    
    answers_json = json.dumps(st.session_state.answers, sort_keys=True, separators=(",", ":"))
    questions_json = json.dumps(raw_questions, sort_keys=True, separators=(",", ":"))
    user_coords, affinities, tags, tensions = build_profile(
        answers_json, questions_json, st.session_state.test_type, st.session_state.language
    )
    top_match = affinities[0]
    title = top_match["name_hi"] if is_hindi else top_match["name"]
    desc = top_match["description_hi"] if is_hindi else top_match["description"]

    profile_kicker_txt = "आपका दार्शनिक प्रोफ़ाइल" if is_hindi else "Your philosophical profile"
    match_affinity_txt = "समानता एफ़िनिटी" if is_hindi else "match affinity"

    st.markdown(
        f"""
        <section class="wc-result">
          <div class="wc-kicker">{escape(profile_kicker_txt)}</div>
          <div class="match">{escape(title)}</div>
          <div style="color:var(--wc-gold);font-weight:800;font-size:1.05rem;margin:.55rem 0">
            {top_match["similarity_pct"]}% {escape(match_affinity_txt)}
          </div>
          <p style="max-width:850px;line-height:1.7;margin:0">{escape(desc)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)

    # Category 1: Diagnostic Dimensions & Core Profile
    st.subheader("🧭 " + ("नैदानिक आयाम एवं प्रोफ़ाइल" if is_hindi else "Diagnostic Dimensions & Profile Analysis"))
    with st.expander(ui["char_title"], expanded=True):
        dim_insights = [
            ("Metaphysics & Reality" if not is_hindi else "तत्वमीमांसा और वास्तविकता", user_coords[0], "Physicalism" if not is_hindi else "भौतिकवाद", "Transcendence" if not is_hindi else "पारलौकिकता",
             "Whether reality is primarily material or grounded in transcendence." if not is_hindi else "क्या वास्तविकता मुख्य रूप से भौतिक है या पारलौकिक पर आधारित है।"),
            ("Society & Structure" if not is_hindi else "समाज और संरचना", user_coords[1], "Individualism" if not is_hindi else "व्यक्तिवाद", "Collectivism" if not is_hindi else "समूहवाद",
             "The balance between individual autonomy and communal obligation." if not is_hindi else "व्यक्तिगत स्वायत्तता और सामुदायिक दायित्व के बीच संतुलन।"),
            ("Culture & Evolution" if not is_hindi else "संस्कृति और विकास", user_coords[2], "Traditionalism" if not is_hindi else "पारंपरिकता", "Progressivism" if not is_hindi else "प्रगतिशीलता",
             "Openness to reform, technology and social change versus continuity." if not is_hindi else "सुधार, प्रौद्योगिकी और सामाजिक परिवर्तन के प्रति खुलापन।"),
            ("Epistemology & Truth" if not is_hindi else "ज्ञानमीमांसा और सत्य", user_coords[3], "Rationalism" if not is_hindi else "बुद्धिवाद", "Empiricism" if not is_hindi else "अनुभववाद",
             "The relative weight given to reason, observation and revision." if not is_hindi else "तर्क, अवलोकन और संशोधन को दिया जाने वाला सापेक्ष महत्व।"),
        ]
        dcols = st.columns(2)
        for i, (name, val, neg, pos, explanation) in enumerate(dim_insights):
            with dcols[i % 2]:
                positive = int(((val + 1) / 2) * 100)
                leaning = pos if val > 0.1 else neg
                st.markdown(
                    f"""
                    <div class="wc-dim">
                      <div class="wc-dim-head"><span>{escape(name)}</span><span style="color:var(--wc-gold)">{val:+.2f}</span></div>
                      <div class="wc-gauge"><span style="width:{positive}%"></span></div>
                      <div class="wc-poles"><span>{escape(neg)}</span><span>{escape(pos)}</span></div>
                      <div class="wc-small" style="margin-top:.55rem"><strong>{escape(leaning)}</strong> — {escape(explanation)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        tags_label = "प्रोफ़ाइल टैग:" if is_hindi else "Profile tags:"
        thinkers_label = "प्रमुख विचारक: " if is_hindi else "Canonical thinkers: "
        st.markdown(f"**{tags_label}** " + " · ".join(f"`{escape(t)}`" for t in tags))
        st.caption(thinkers_label + ", ".join(top_match.get("thinkers", [])))

    # Category 2: Historical Lineages & Philosophical Twins
    st.subheader("🏛️ " + ("ऐतिहासिक परंपराएं और दार्शनिक समानता" if is_hindi else "Historical Lineages & Philosophical Twins"))
    with st.expander(ui["affinities_label"], expanded=False):
        st.caption("Detailed ranking of how your coordinates align with major world traditions:" if not is_hindi else "प्रमुख विश्व परंपराओं के साथ आपकी स्थिति का विस्तृत मूल्यांकन:")
        for i, aff in enumerate(affinities):
            nm = aff["name_hi"] if is_hindi else aff["name"]
            tier = "Primary affinity" if i == 0 else ("Strong affinity" if i < 4 else "Secondary affinity")
            if is_hindi:
                tier = "प्राथमिक समानता" if i == 0 else ("मजबूत समानता" if i < 4 else "द्वितीयक समानता")
            st.markdown(
                f"""
                <div class="wc-card wc-affinity" style="margin:.55rem 0;padding:1rem 1.1rem">
                  <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center">
                    <div style="display:flex;align-items:center;gap:.7rem"><span class="wc-rank">{i+1}</span><strong>{escape(nm)}</strong></div>
                    <strong style="color:var(--wc-gold);font-size:1.05rem">{aff["similarity_pct"]}%</strong>
                  </div>
                  <div class="wc-scorebar"><span style="width:{aff["similarity_pct"]}%"></span></div>
                  <div class="wc-small" style="text-transform:uppercase;letter-spacing:.06em;margin:.35rem 0">{tier}</div>
                  <div class="wc-small">{escape((aff.get("description_hi") if is_hindi else aff.get("description",""))[:210])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    twin = PHILOSOPHER_QUOTES.get(top_match["name"], {
        "thinkers": [(t, 1 / max(1, len(top_match.get("thinkers", [])))) for t in top_match.get("thinkers", ["Thinker"])],
        "quote": "Truth emerges from the open dialectic of reason and experience.",
    })
    with st.expander(ui["thinker_breakdown_title"], expanded=False):
        tcols = st.columns(min(3, max(1, len(twin["thinkers"]))))
        for col, (thinker, weight) in zip(tcols, twin["thinkers"]):
            with col:
                st.markdown(
                    f'<div class="wc-card"><div style="font-size:1.4rem">🏛️</div><h3>{escape(thinker)}</h3><div style="color:var(--wc-gold);font-weight:800">{round(top_match["similarity_pct"]*weight,1)}% {"वंश सिग्नल" if is_hindi else "lineage signal"}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown(f'<div class="wc-quote" style="padding:1rem 0 0;border-left:3px solid var(--wc-gold);padding-left:1rem">{escape(twin["quote"])}</div>', unsafe_allow_html=True)

    # Category 3: Spatial Maps & Comparative Analysis
    st.subheader("🔬 " + ("स्थानिक मानचित्र और तुलनात्मक विश्लेषण" if is_hindi else "Spatial Maps & Comparative Analysis"))
    with st.expander("Visual Map & Comparative Analysis" if not is_hindi else "विजुअल मैप और तुलनात्मक विश्लेषण", expanded=False):
        tab_radar, tab_space = st.tabs(ui["radar_space_tab"])

        def radar_figure(comparisons, user_label="You"):
            cats = ["Transcendence", "Collectivism", "Progressivism", "Empiricism"]
            fig = go.Figure()
            user_scaled = [((v+1)/2)*100 for v in user_coords]
            fig.add_trace(go.Scatterpolar(
                r=user_scaled+[user_scaled[0]], theta=cats+[cats[0]],
                fill="toself", name=user_label if not is_hindi else "आप", line_color={"Dark":"#D8B25C","Light":"#76530D","Ivory":"#A06B1C","Ocean":"#62D5D1"}.get(st.session_state.theme,"#D8B25C"),
            ))
            palette = ["#38BDF8", "#10B981", "#8B5CF6", "#F59E0B"]
            for i, (name, coords) in enumerate(comparisons):
                scaled=[((v+1)/2)*100 for v in coords]
                fig.add_trace(go.Scatterpolar(
                    r=scaled+[scaled[0]], theta=cats+[cats[0]], fill="toself",
                    name=name, opacity=.38, line_color=palette[i % len(palette)]
                ))
            chart_pal = {"Dark":("#E7EBF1","#293548"),"Light":("#142033","#D8DDE5"),"Ivory":("#2C2418","#DED4C3"),"Ocean":("#E9FAFF","#1D4652")}
            text_c, grid_c = chart_pal.get(st.session_state.theme, chart_pal["Dark"])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color=text_c),
                margin=dict(l=25,r=25,t=20,b=20), height=430,
                polar=dict(
                    bgcolor="rgba(255,255,255,.18)" if st.session_state.theme in ("Light","Ivory") else "rgba(10,15,24,.30)",
                    radialaxis=dict(range=[0,100], visible=True, gridcolor=grid_c),
                    angularaxis=dict(gridcolor=grid_c),
                ),
                legend=dict(orientation="h", y=-.08),
            )
            return fig

        with tab_radar:
            st.plotly_chart(
                radar_figure([(top_match["name"], top_match["vector"])]),
                use_container_width=True,
                key="result_radar",
                config={"displaylogo": False, "responsive": True},
            )
        with tab_space:
            names = list(WORLDVIEWS.keys())
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter3d(
                x=[WORLDVIEWS[n]["vector"][0] for n in names],
                y=[WORLDVIEWS[n]["vector"][1] for n in names],
                z=[WORLDVIEWS[n]["vector"][2] for n in names],
                mode="markers+text", text=names, textposition="top center",
                marker=dict(size=6, color="#38BDF8", opacity=.78),
                hovertemplate="%{text}<extra></extra>",
                name="Traditions" if not is_hindi else "परंपराएं",
            ))
            fig3.add_trace(go.Scatter3d(
                x=[user_coords[0]], y=[user_coords[1]], z=[user_coords[2]],
                mode="markers+text", text=["YOU" if not is_hindi else "आप"], textposition="top center",
                marker=dict(size=13, color="#D7B45A", symbol="diamond", line=dict(width=2,color="#FFFFFF")),
                name="You" if not is_hindi else "आप",
            ))
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0), height=480,
                scene=dict(
                    xaxis_title="Transcendence", yaxis_title="Collectivism", zaxis_title="Progressivism",
                    xaxis=dict(range=[-1,1]), yaxis=dict(range=[-1,1]), zaxis=dict(range=[-1,1]),
                ),
            )
            st.plotly_chart(fig3, use_container_width=True, key="result_3d", config={"displaylogo": False, "responsive": True})
            st.caption("The 3D view projects the first three coordinates; the fourth dimension is shown in the radar." if not is_hindi else "3D दृश्य पहले तीन निर्देशांकों को प्रदर्शित करता है; चौथा आयाम रडार में दिखाया गया है।")

        st.markdown(f"**{ui['comparison_title']}**")
        available = [s for s in WORLDVIEWS if s != top_match["name"]]
        selected = st.multiselect(
            ui["traditions_compare_label"],
            available,
            default=[s for s in st.session_state.comparison_schools if s in available][:3] or available[:1],
            max_selections=3,
            key="comparison_picker",
        )
        st.session_state.comparison_schools = selected
        if selected:
            comp = [(s, WORLDVIEWS[s]["vector"]) for s in selected]
            st.plotly_chart(
                radar_figure(comp, "Your coordinates" if not is_hindi else "आपके निर्देशांक"),
                use_container_width=True,
                key="comparison_radar",
                config={"displaylogo": False, "responsive": True},
            )

    # Category 4: Compatibility, Tensions & Conviction Calibration
    st.subheader("⚔️ " + ("संगतता, तनाव और बौद्धिक आत्मविश्वास" if is_hindi else "Compatibility, Tensions & Conviction"))
    with st.expander(ui["matrix_title"] + " & Tensions", expanded=False):
        st.caption(ui["matrix_sub"])
        friend_url = st.text_input(ui["friend_url_label"], placeholder=ui["friend_url_placeholder"], key="friend_url_input")
        if friend_url:
            try:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(friend_url).query)
                raw = query.get("answers", [None])[0]
                if raw is None:
                    raise ValueError("No answers parameter")
                friend_answers = json.loads(urllib.parse.unquote(raw))
                friend_answers = {int(k): str(v) for k,v in friend_answers.items()}
                friend_coords = calculate_coordinates_direct(friend_answers, raw_questions, st.session_state.test_type)
                friend_aff = calculate_affinities(friend_coords, WORLDVIEWS)
                dist = sum((u-f)**2 for u,f in zip(user_coords, friend_coords)) ** .5
                consensus = max(0.0, min(100.0, round((1-(dist/4))*100,1)))
                axes = [
                    ("Metaphysics & Reality", abs(user_coords[0]-friend_coords[0])),
                    ("Society & Structure", abs(user_coords[1]-friend_coords[1])),
                    ("Culture & Evolution", abs(user_coords[2]-friend_coords[2])),
                    ("Epistemology & Truth", abs(user_coords[3]-friend_coords[3])),
                ]
                harmony = min(axes,key=lambda x:x[1])[0]
                battleground = max(axes,key=lambda x:x[1])[0]
                f1, f2 = st.columns(2)
                with f1:
                    st.markdown(
                        f"""
                        <div class="wc-card">
                          <div class="wc-kicker">{"अनुकूलता" if is_hindi else "Compatibility"}</div>
                          <div style="font-size:2rem;font-weight:800;color:var(--wc-gold)">{consensus}%</div>
                          <p><strong>{"आपका शीर्ष:" if is_hindi else "Your top:"}</strong> {escape(top_match["name"])}</p>
                          <p><strong>{"मित्र का शीर्ष:" if is_hindi else "Friend's top:"}</strong> {escape(friend_aff[0]["name"])}</p>
                          <p><strong>{"समानता का बिंदु:" if is_hindi else "Closest common ground:"}</strong> {escape(harmony)}</p>
                          <p><strong>{"सबसे बड़ा भेद:" if is_hindi else "Biggest divergence:"}</strong> {escape(battleground)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with f2:
                    st.plotly_chart(
                        radar_figure([("Friend" if not is_hindi else "मित्र", friend_coords)], "Friend" if not is_hindi else "मित्र"),
                        use_container_width=True,
                        key="friend_radar",
                        config={"displaylogo": False, "responsive": True},
                    )
            except (ValueError, TypeError, json.JSONDecodeError, KeyError):
                st.warning("That does not look like a valid Worldview Compass result URL. Please paste the complete link." if not is_hindi else "यह वैध विश्वदृष्टिकोण कम्पास परिणाम लिंक नहीं प्रतीत होता। कृपया पूरा लिंक पेस्ट करें।")

        st.markdown(f"**{ui['challenge_title']}**")
        if tensions:
            for t in tensions:
                st.warning(f"{t['title']}\n\n{t['description']}", icon="⚡")
        else:
            st.success(ui["no_tensions"])

        st.markdown("---")
        st.caption(ui["confidence_sub"])
        st.slider(
            "Epistemic confidence" if not is_hindi else "बौद्धिक आत्मविश्वास",
            0, 100, st.session_state.confidence, 5,
            key="confidence",
            help="This self-report is separate from the calculated worldview match.",
        )
        st.caption(f"0 = {ui['confidence_low']}  ·  100 = {ui['confidence_high']}")

    # Category 5: Share Profile & Identity Artifacts
    st.subheader("📢 " + ("प्रोफ़ाइल और पहचान पत्र साझा करें" if is_hindi else "Share Profile & Identity Artifacts"))
    with st.expander(ui["share_heading"], expanded=False):
        st.caption(ui["share_sub"])
        handle = st.text_input(
            ui["badge_handle_label"],
            placeholder=ui["badge_handle_placeholder"],
            key="custom_badge_handle",
        )
        passport_bytes = cached_passport(
            json.dumps(user_coords),
            json.dumps(top_match, sort_keys=True),
            json.dumps(tags),
            json.dumps(affinities, sort_keys=True),
            json.dumps(tensions, sort_keys=True),
            handle.strip(),
        )

        share_msg = (
            f"I took the Worldview Compass test and matched {top_match['similarity_pct']}% "
            f"with {top_match['name']}! Discover your philosophical profile."
        )
        try:
            share_url = st.context.url
        except Exception:
            share_url = ""
        encoded_msg = urllib.parse.quote(f"{share_msg} {share_url}".strip())
        share_target = urllib.parse.quote(share_url or "Worldview Compass")
        x_url = f"https://twitter.com/intent/tweet?text={encoded_msg}"
        wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
        li_url = f"https://www.linkedin.com/sharing/share-offsite/?url={share_target}"

        sh1, sh2, sh3, sh4 = st.columns(4)
        with sh1:
            st.markdown(f"<a class='wc-social-btn wc-x' style='width:100%' href='{escape(x_url)}' target='_blank' rel='noopener noreferrer'>𝕏&nbsp; X</a>", unsafe_allow_html=True)
        with sh2:
            st.markdown(f"<a class='wc-social-btn wc-wa' style='width:100%' href='{escape(wa_url)}' target='_blank' rel='noopener noreferrer'>◉&nbsp; WhatsApp</a>", unsafe_allow_html=True)
        with sh3:
            st.markdown(f"<a class='wc-social-btn wc-li' style='width:100%' href='{escape(li_url)}' target='_blank' rel='noopener noreferrer'>in&nbsp; LinkedIn</a>", unsafe_allow_html=True)
        with sh4:
            st.download_button("🎫 " + ("डाउनलोड" if is_hindi else "Download"), data=passport_bytes, file_name=f"worldview_identity_card_{top_match.get('slug','result')}.png", mime="image/png", use_container_width=True, type="secondary")

    st.markdown(f'<div class="wc-footer">{"विश्वदृष्टिकोण कम्पास एक दार्शनिक अन्वेषण उपकरण है। परिणाम आपूर्ति किए गए उत्तर मॉडल को दर्शाते हैं और इन्हें वैज्ञानिक या चिकित्सीय निदान नहीं माना जाना चाहिए।" if is_hindi else "Worldview Compass is an exploratory philosophical instrument. Results reflect the supplied answer model and should not be treated as scientific or clinical diagnosis."}</div>', unsafe_allow_html=True)