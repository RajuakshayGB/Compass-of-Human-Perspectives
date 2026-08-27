"""
Worldview Compass — redesigned Streamlit presentation layer.

The scoring/data model remains in database.py and engine.py.  This file focuses
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
        "quick_label": "⚡ Quick Odyssey\n\n25 Questions • ~8 mins\nSamples 1 question per core dimension for an efficient diagnostic.",
        "full_label": "🏛️ Full Odyssey\n\n100 Questions • ~25 mins\nComprehensive assessment across all 100 questions for maximum precision.",
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
        "passport_btn": "Download Identity Card (PNG) 🎫"
    },
    "Hindi": {
        "title": "विचार कम्पास (Worldview Compass)",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "मानव विचार की एक निष्पक्ष और गंभीर खोज। 25 या 100 प्रश्नों के माध्यम से अपने विश्वदृष्टिकोण की वास्तुकला को जानें और प्रमुख वैश्विक परंपराओं के साथ अपनी समानता देखें।",
        "quick_label": "⚡ त्वरित यात्रा\n\n25 प्रश्न • ~8 मिनट\nत्वरित मूल्यांकन के लिए 25 मूल आयामों से 1 प्रतिनिधि प्रश्न।",
        "full_label": "🏛️ पूर्ण यात्रा\n\n100 प्रश्न • ~25 मिनट\nसमग्र विश्लेषण के लिए सभी 100 प्रश्नों का विस्तृत मूल्यांकन।",
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
        "passport_btn": "पहचान पत्र डाउनलोड करें (PNG) 🎫"
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
    w, h = 1000, 1600
    img = Image.new("RGB", (w, h), (249, 248, 245))
    draw = ImageDraw.Draw(img)

    draw.rectangle([25, 25, w - 25, h - 25], outline=(197, 160, 89), width=4)
    draw.rectangle([38, 38, w - 38, h - 38], outline=(148, 163, 184), width=1)
    
    for cx, cy in [(25, 25), (w - 25, 25), (25, h - 25), (w - 25, h - 25)]:
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=(197, 160, 89))

    draw.rounded_rectangle([70, 55, w - 70, 135], radius=10, fill=(255, 255, 255), outline=(226, 218, 203), width=1)
    draw.text((w // 2, 80), "WORLDVIEW COMPASS: COMPREHENSIVE COGNITIVE DOSSIER", fill=(133, 93, 16), anchor="mm")
    
    subtitle_text = f"VERIFIED SPECIFICATION • {custom_handle.upper()}" if custom_handle else "VERIFIED PHILOSOPHICAL IDENTITY SPECIFICATION"
    draw.text((w // 2, 110), subtitle_text, fill=(100, 116, 139), anchor="mm")

    draw.rounded_rectangle([60, 155, w - 60, 285], radius=12, fill=(255, 255, 255), outline=(197, 160, 89), width=2)
    draw.text((w // 2, 192), top_affinity["name"].upper(), fill=(15, 23, 42), anchor="mm")
    draw.text((w // 2, 230), f"MATCH AFFINITY: {top_affinity['similarity_pct']}%", fill=(2, 132, 199), anchor="mm")

    desc = top_affinity.get("description", "")
    lines = [desc[i:i+85] for i in range(0, len(desc), 85)][:2]
    for idx, l in enumerate(lines):
        draw.text((w // 2, 252 + (idx * 20)), l.strip(), fill=(51, 65, 85), anchor="mm")

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

    draw.text((w // 2, 675), "TOP HISTORICAL LINEAGE AFFINITIES", fill=(133, 93, 16), anchor="mm")
    aff_str = "  •  ".join([f"{a['name']} ({a['similarity_pct']}%)" for a in affinities[:4]])
    draw.text((w // 2, 710), aff_str, fill=(15, 23, 42), anchor="mm")

    draw.text((w // 2, 770), "PROFILE ATTRIBUTES & CANONICAL THINKERS", fill=(133, 93, 16), anchor="mm")
    draw.text((w // 2, 805), " • ".join(character_tags), fill=(15, 23, 42), anchor="mm")
    thinkers_str = ", ".join(top_affinity.get("thinkers", [])[:3])
    draw.text((w // 2, 840), f"Canonical Lineage Thinkers: {thinkers_str}", fill=(71, 85, 105), anchor="mm")

    draw.text((w // 2, 900), "DIALECTICAL COGNITIVE TENSIONS & CONSISTENCY", fill=(133, 93, 16), anchor="mm")
    t_summary = f"Primary Detected Tension: {tensions[0]['title']}" if tensions else "No major structural tensions detected. High internal consistency."
    draw.text((w // 2, 935), t_summary, fill=(180, 83, 9), anchor="mm")

    for bx in range(100, 900, 12):
        stroke = 4 if (bx % 24 == 0) else 2
        draw.line([(bx, 1420), (bx, 1470)], fill=(197, 160, 89), width=stroke)

    draw.text((w // 2, 1530), "NON-CLINICAL PHILOSOPHICAL IDENTITY SPECIFICATION • WORLDVIEW COMPASS", fill=(148, 163, 184), anchor="mm")

    buf = BytesIO()
    img.save(buf, format="PNG")
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
# Theme
# ---------------------------------------------------------------------------
def inject_theme(theme="Dark", dim_idx=0):
    dark = theme.lower() == "dark"
    tint_mode = "dark" if dark else "light"
    active_tint = DIMENSION_TINTS.get(dim_idx, {}).get(tint_mode, "transparent")

    if dark:
        p = {
            "bg": "#0A0F18",
            "surface": "rgba(19, 27, 39, .82)",
            "surface2": "#111A27",
            "text": "#F7F7F2",
            "muted": "#A8B3C2",
            "gold": "#D7B45A",
            "gold_soft": "rgba(215,180,90,.14)",
            "border": "rgba(215,180,90,.24)",
            "line": "#293548",
            "shadow": "0 18px 50px rgba(0,0,0,.28)",
            "input": "#0F1724",
        }
    else:
        p = {
            "bg": "#F6F4EE",
            "surface": "rgba(255,255,255,.90)",
            "surface2": "#FFFFFF",
            "text": "#142033",
            "muted": "#526174",
            "gold": "#76530D",
            "gold_soft": "rgba(118,83,13,.10)",
            "border": "rgba(118,83,13,.22)",
            "line": "#D8DDE5",
            "shadow": "0 14px 36px rgba(31,41,55,.09)",
            "input": "#FFFFFF",
        }

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

        :root {{
            --wc-bg: {p["bg"]};
            --wc-surface: {p["surface"]};
            --wc-surface2: {p["surface2"]};
            --wc-text: {p["text"]};
            --wc-muted: {p["muted"]};
            --wc-gold: {p["gold"]};
            --wc-gold-soft: {p["gold_soft"]};
            --wc-border: {p["border"]};
            --wc-line: {p["line"]};
            --wc-shadow: {p["shadow"]};
            --wc-input: {p["input"]};
        }}

        html, body, [data-testid="stAppViewContainer"] {{
            background: var(--wc-bg) !important;
        }}
        .stApp {{
            background:
                radial-gradient(circle at 50% -10%, {active_tint} 0%, transparent 42%),
                var(--wc-bg) !important;
            color: var(--wc-text) !important;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}
        .block-container {{
            max-width: 1180px !important;
            padding: 1.1rem 1.2rem 4rem !important;
        }}
        h1, h2, h3, h4 {{
            color: var(--wc-text) !important;
            font-family: 'Inter', sans-serif !important;
        }}
        p, li, label, [data-testid="stCaptionContainer"] {{
            color: var(--wc-muted);
        }}
        .wc-brand {{
            display:flex; align-items:center; gap:.72rem;
            font-family:'Cinzel',serif; font-weight:700; letter-spacing:.055em;
            color:var(--wc-text); font-size:1.05rem;
        }}
        .wc-brand img {{
            width:38px; height:38px; object-fit:cover; border-radius:10px;
            border:1px solid var(--wc-border);
            box-shadow:var(--wc-shadow);
        }}
        .wc-nav {{
            display:flex; align-items:center; justify-content:space-between;
            gap:1rem; padding:.15rem 0 .8rem;
        }}
        .wc-kicker {{
            color:var(--wc-gold); text-transform:uppercase; letter-spacing:.13em;
            font-size:.72rem; font-weight:800;
        }}
        .wc-hero {{
            border:1px solid var(--wc-border);
            border-radius:28px; padding:clamp(1.4rem,4vw,3.2rem);
            background:linear-gradient(135deg,var(--wc-surface),rgba(215,180,90,.035));
            box-shadow:var(--wc-shadow);
            margin:.7rem 0 1.1rem;
        }}
        .wc-hero h1 {{
            font-family:'Cinzel',serif !important; font-size:clamp(2rem,5vw,3.7rem) !important;
            line-height:1.08; letter-spacing:.025em; margin:.35rem 0 .55rem;
        }}
        .wc-hero .lead {{
            max-width:780px; font-size:1.05rem; line-height:1.7;
            margin:0 0 1.25rem;
        }}
        .wc-quote {{
            font-family:'Lora',serif; font-style:italic; color:var(--wc-muted);
        }}
        .wc-card {{
            border:1px solid var(--wc-border); border-radius:18px;
            background:var(--wc-surface); box-shadow:var(--wc-shadow);
            padding:1.05rem 1.1rem; height:100%;
        }}
        .wc-card h3 {{ margin:.1rem 0 .45rem; font-size:1.03rem; }}
        .wc-card p {{ margin:0; line-height:1.55; font-size:.91rem; }}
        .wc-mode {{
            border:1px solid var(--wc-border); border-radius:18px;
            background:var(--wc-surface); padding:1.2rem;
            box-shadow:var(--wc-shadow); min-height:190px;
        }}
        .wc-mode .icon {{ font-size:1.65rem; }}
        .wc-mode h3 {{ margin:.45rem 0 .25rem; }}
        .wc-mode p {{ font-size:.9rem; line-height:1.5; margin:0 0 .85rem; }}
        .wc-section {{
            border-top:1px solid var(--wc-line); padding-top:1.25rem; margin-top:1.25rem;
        }}
        .wc-result {{
            border:1px solid var(--wc-border); border-radius:24px;
            background:linear-gradient(145deg,var(--wc-surface),var(--wc-gold-soft));
            padding:1.5rem; box-shadow:var(--wc-shadow);
        }}
        .wc-result .match {{
            color:var(--wc-gold); font-family:'Cinzel',serif;
            font-size:clamp(1.9rem,4vw,3rem); font-weight:700; line-height:1.15;
        }}
        .wc-stat {{
            border:1px solid var(--wc-border); border-radius:14px;
            background:var(--wc-surface); padding:.8rem 1rem;
        }}
        .wc-stat .num {{ font-size:1.45rem; font-weight:800; color:var(--wc-text); }}
        .wc-stat .lbl {{ font-size:.74rem; color:var(--wc-muted); text-transform:uppercase; letter-spacing:.08em; }}
        .wc-dim {{
            border:1px solid var(--wc-border); border-radius:16px; padding:1rem;
            background:var(--wc-surface); margin:.65rem 0;
        }}
        .wc-dim-head {{ display:flex; justify-content:space-between; gap:1rem; font-weight:700; }}
        .wc-gauge {{ height:9px; background:var(--wc-line); border-radius:99px; overflow:hidden; margin:.7rem 0 .45rem; }}
        .wc-gauge > span {{ display:block; height:100%; background:var(--wc-gold); border-radius:99px; }}
        .wc-poles {{ display:flex; justify-content:space-between; gap:1rem; font-size:.72rem; color:var(--wc-muted); }}
        .wc-small {{ font-size:.82rem; color:var(--wc-muted); line-height:1.5; }}
        .wc-progress-label {{
            display:flex; justify-content:space-between; gap:1rem; align-items:center;
            margin:.35rem 0 .45rem; color:var(--wc-muted); font-size:.86rem;
        }}
        .wc-pill {{
            display:inline-flex; align-items:center; border:1px solid var(--wc-border);
            border-radius:999px; padding:.3rem .65rem; font-size:.73rem; font-weight:700;
            color:var(--wc-gold); background:var(--wc-gold-soft);
        }}
        .wc-footer {{ text-align:center; color:var(--wc-muted); font-size:.76rem; padding-top:2rem; }}
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {{
            border-radius:12px !important; border:1px solid var(--wc-border) !important;
            min-height:44px !important; transition:transform .15s ease,border-color .15s ease,box-shadow .15s ease !important;
        }}
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            transform:translateY(-1px); border-color:var(--wc-gold) !important;
            box-shadow:0 7px 20px rgba(0,0,0,.10) !important;
        }}
        div[data-testid="stRadio"] label {{
            border:1px solid var(--wc-border); border-radius:14px; padding:.72rem .85rem;
            margin:.35rem 0; background:var(--wc-surface); transition:border-color .15s ease, background .15s ease;
        }}
        div[data-testid="stRadio"] label:hover {{ border-color:var(--wc-gold); background:var(--wc-gold-soft); }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {{
            background:var(--wc-input) !important; color:var(--wc-text) !important;
        }}
        div[data-testid="stExpander"] {{
            border-color:var(--wc-border) !important;
            background:var(--wc-surface) !important;
            border-radius:14px !important;
        }}
        @media (max-width: 720px) {{
            .block-container {{ padding: .7rem .72rem 3rem !important; }}
            .wc-nav {{ align-items:flex-start; }}
            .wc-brand {{ font-size:.88rem; }}
            .wc-brand img {{ width:32px; height:32px; }}
            .wc-hero {{ border-radius:20px; padding:1.25rem; }}
            .wc-hero .lead {{ font-size:.96rem; }}
            .wc-progress-label {{ align-items:flex-start; flex-direction:column; gap:.2rem; }}
            div[data-testid="stButton"] > button,
            div[data-testid="stDownloadButton"] > button {{ min-height:48px !important; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{ animation:none !important; transition:none !important; scroll-behavior:auto !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# State / URL
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
        if params.get("theme") in ("Dark", "Light"):
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
    st.error("The question dataset could not be loaded.")
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
# Header
# ---------------------------------------------------------------------------
logo = get_base64_logo()
logo_markup = (
    f'<img src="data:image/png;base64,{logo}" alt="Worldview Compass compass logo">'
    if logo else '<span style="font-size:1.8rem" aria-hidden="true">🧭</span>'
)
st.markdown(
    f"""
    <div class="wc-nav">
      <div class="wc-brand">{logo_markup}<span>WORLDVIEW COMPASS</span></div>
      <div class="wc-kicker">Non-clinical philosophical exploration</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Controls are deliberately native Streamlit widgets for keyboard/screen-reader support.
hc1, hc2, hc3 = st.columns([1.0, 1.2, 1.2])
with hc1:
    if st.button("⌂  Home", use_container_width=True, help="Return to the home screen"):
        set_state(started=False, completed=False, current_question_index=0, answers={})
        sync_state_to_url()
        st.rerun()
with hc2:
    lang_choice = st.selectbox(
        "Language",
        ["English", "Hindi"],
        index=0 if st.session_state.language == "English" else 1,
        key="header_language",
        label_visibility="collapsed",
    )
    if lang_choice != st.session_state.language:
        st.session_state.language = lang_choice
        sync_state_to_url()
        st.rerun()
with hc3:
    theme_choice = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1,
        key="header_theme",
        label_visibility="collapsed",
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        sync_state_to_url()
        st.rerun()


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
if not st.session_state.started and not st.session_state.completed:
    st.markdown(
        f"""
        <section class="wc-hero">
          <div class="wc-kicker">A map, not a verdict</div>
          <h1>{escape(ui["title"])}</h1>
          <div class="wc-quote" style="font-size:1.18rem">“{escape(ui["subtitle"])}”</div>
          <p class="lead">{escape(ui["tagline"])}</p>
          <span class="wc-pill">25D → 4D diagnostic spectrum</span>
          <span class="wc-pill" style="margin-left:.35rem">English + हिन्दी</span>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3)
    for col, data in zip(cols, HOMEPAGE_SECTIONS):
        with col:
            title = data["title_hi"] if is_hindi else data["title_en"]
            desc = data["desc_hi"] if is_hindi else data["desc_en"]
            st.markdown(
                f"""
                <div class="wc-card">
                  <div style="font-size:1.65rem">{data["icon"]}</div>
                  <h3>{escape(title)}</h3>
                  <p>{escape(desc)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader("Choose your depth" if not is_hindi else "अपना मूल्यांकन चुनें")
    st.caption(
        "Start fast, or take the full assessment. You can move backward and revisit answers."
        if not is_hindi else
        "त्वरित मूल्यांकन शुरू करें या पूरा परीक्षण लें। आप पीछे जाकर उत्तर बदल सकते हैं।"
    )

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            """
            <div class="wc-mode">
              <div class="icon">⚡</div><h3>Quick Odyssey</h3>
              <p>25 questions • about 8 minutes<br>One representative question per core dimension.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(ui["quick_label"], key="start_quick", use_container_width=True, type="primary"):
            set_state(test_type="Quick", started=True, completed=False, current_question_index=0, answers={})
            sync_state_to_url()
            st.rerun()
    with m2:
        st.markdown(
            """
            <div class="wc-mode">
              <div class="icon">🏛️</div><h3>Full Odyssey</h3>
              <p>100 questions • about 25 minutes<br>Comprehensive coverage for maximum precision.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(ui["full_label"], key="start_full", use_container_width=True):
            set_state(test_type="Full", started=True, completed=False, current_question_index=0, answers={})
            sync_state_to_url()
            st.rerun()

    st.markdown(
        '<div class="wc-footer">Your result is a philosophical profile, not a clinical or psychological diagnosis.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# QUESTIONNAIRE
# ---------------------------------------------------------------------------
elif st.session_state.started and not st.session_state.completed:
    total = len(raw_questions)
    idx = st.session_state.current_question_index
    q = raw_questions[idx]
    qid = q["id"]
    progress = (idx + 1) / total
    pct = int(progress * 100)
    answered = len(st.session_state.answers)

    st.markdown(
        f"""
        <div class="wc-progress-label">
          <strong>Question {idx + 1} of {total}</strong>
          <span>{pct}% complete • {answered} answered</span>
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
        f'<div style="max-width:880px;margin:1rem 0 .5rem;"><h2 style="font-size:clamp(1.25rem,2.8vw,2rem);line-height:1.35">{escape(q_text)}</h2></div>',
        unsafe_allow_html=True,
    )
    st.caption("Choose the answer that best represents your view. There is no “correct” answer.")

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

    selected_label = st.radio(
        "Answer choices",
        labels,
        index=(labels.index(current_label) if current_label in labels else None),
        key=radio_key,
        label_visibility="visible",
    )

    with st.expander("Jump to a question", expanded=False):
        grid_cols = st.columns(10 if total > 25 else 5)
        for n in range(total):
            qn = n + 1
            q_id_check = raw_questions[n]["id"]
            marker = "✓ " if q_id_check in st.session_state.answers else ""
            with grid_cols[n % len(grid_cols)]:
                if st.button(
                    f"{marker}{qn}",
                    key=f"jump_{st.session_state.test_type}_{qn}",
                    use_container_width=True,
                    type="primary" if qn == idx + 1 else "secondary",
                ):
                    # Persist the current selection before jumping.
                    if selected_label:
                        st.session_state.answers[qid] = code_by_label[selected_label]
                    st.session_state.current_question_index = n
                    sync_state_to_url()
                    st.rerun()

    nav1, nav2, nav3 = st.columns([1.2, 5.6, 1.2])
    with nav1:
        if st.button("← Previous", disabled=idx == 0, use_container_width=True):
            if selected_label:
                st.session_state.answers[qid] = code_by_label[selected_label]
            st.session_state.current_question_index = max(0, idx - 1)
            sync_state_to_url()
            st.rerun()
    with nav2:
        if selected_label:
            st.caption("Selection saved when you continue. You can revisit any answered question.")
        else:
            st.warning("Select an answer to continue.", icon="⚠️")
    with nav3:
        next_label = "Finish" if idx == total - 1 else "Next →"
        if st.button(next_label, disabled=selected_label is None, use_container_width=True, type="primary"):
            st.session_state.answers[qid] = code_by_label[selected_label]
            if idx == total - 1:
                st.session_state.completed = True
            else:
                st.session_state.current_question_index = idx + 1
            sync_state_to_url()
            st.rerun()


# ---------------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------------
elif st.session_state.completed:
    answers_json = json.dumps(st.session_state.answers, sort_keys=True, separators=(",", ":"))
    questions_json = json.dumps(raw_questions, sort_keys=True, separators=(",", ":"))
    user_coords, affinities, tags, tensions = build_profile(
        answers_json, questions_json, st.session_state.test_type, st.session_state.language
    )
    top_match = affinities[0]
    title = top_match["name_hi"] if is_hindi else top_match["name"]
    desc = top_match["description_hi"] if is_hindi else top_match["description"]

    st.markdown(
        f"""
        <section class="wc-result">
          <div class="wc-kicker">Your philosophical profile</div>
          <div class="match">{escape(title)}</div>
          <div style="color:var(--wc-gold);font-weight:800;font-size:1.05rem;margin:.55rem 0">
            {top_match["similarity_pct"]}% match affinity
          </div>
          <p style="max-width:850px;line-height:1.7;margin:0">{escape(desc)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    s1, s2, s3, s4 = st.columns(4)
    stat_data = [
        (f"{top_match['similarity_pct']}%", "Top affinity"),
        (str(len(st.session_state.answers)), f"Answers • {st.session_state.test_type}"),
        (str(len(tensions)), "Dialectical tensions"),
        (str(len(affinities)), "Traditions compared"),
    ]
    for col, (num, lbl) in zip((s1,s2,s3,s4), stat_data):
        with col:
            st.markdown(f'<div class="wc-stat"><div class="num">{escape(num)}</div><div class="lbl">{escape(lbl)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["char_title"])

    dim_insights = [
        ("Metaphysics & Reality", user_coords[0], "Physicalism", "Transcendence",
         "Whether reality is primarily material or grounded in transcendence."),
        ("Society & Structure", user_coords[1], "Individualism", "Collectivism",
         "The balance between individual autonomy and communal obligation."),
        ("Culture & Evolution", user_coords[2], "Traditionalism", "Progressivism",
         "Openness to reform, technology and social change versus continuity."),
        ("Epistemology & Truth", user_coords[3], "Rationalism", "Empiricism",
         "The relative weight given to reason, observation and revision."),
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

    st.markdown("**Profile tags:** " + " · ".join(f"`{escape(t)}`" for t in tags))
    st.caption("Canonical thinkers: " + ", ".join(top_match.get("thinkers", [])))

    twin = PHILOSOPHER_QUOTES.get(top_match["name"], {
        "thinkers": [(t, 1 / max(1, len(top_match.get("thinkers", [])))) for t in top_match.get("thinkers", ["Thinker"])],
        "quote": "Truth emerges from the open dialectic of reason and experience.",
    })
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["thinker_breakdown_title"])
    tcols = st.columns(min(3, max(1, len(twin["thinkers"]))))
    for col, (thinker, weight) in zip(tcols, twin["thinkers"]):
        with col:
            st.markdown(
                f'<div class="wc-card"><div style="font-size:1.4rem">🏛️</div><h3>{escape(thinker)}</h3><div style="color:var(--wc-gold);font-weight:800">{round(top_match["similarity_pct"]*weight,1)}% lineage signal</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown(f'<div class="wc-quote" style="padding:1rem 0 0;border-left:3px solid var(--wc-gold);padding-left:1rem">{escape(twin["quote"])}</div>', unsafe_allow_html=True)

    # Visual analysis
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader("Visual map")
    tab_radar, tab_space = st.tabs(["4D radar", "3D worldview space"])

    def radar_figure(comparisons, user_label="You"):
        cats = ["Transcendence", "Collectivism", "Progressivism", "Empiricism"]
        fig = go.Figure()
        user_scaled = [((v+1)/2)*100 for v in user_coords]
        fig.add_trace(go.Scatterpolar(
            r=user_scaled+[user_scaled[0]], theta=cats+[cats[0]],
            fill="toself", name=user_label, line_color="#D7B45A",
        ))
        palette = ["#38BDF8", "#10B981", "#8B5CF6", "#F59E0B"]
        for i, (name, coords) in enumerate(comparisons):
            scaled=[((v+1)/2)*100 for v in coords]
            fig.add_trace(go.Scatterpolar(
                r=scaled+[scaled[0]], theta=cats+[cats[0]], fill="toself",
                name=name, opacity=.38, line_color=palette[i % len(palette)]
            ))
        light = st.session_state.theme == "Light"
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#142033" if light else "#E7EBF1"),
            margin=dict(l=25,r=25,t=20,b=20), height=430,
            polar=dict(
                bgcolor="rgba(255,255,255,.22)" if light else "rgba(10,15,24,.30)",
                radialaxis=dict(range=[0,100], visible=True, gridcolor="#D8DDE5" if light else "#293548"),
                angularaxis=dict(gridcolor="#D8DDE5" if light else "#293548"),
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
            name="Traditions",
        ))
        fig3.add_trace(go.Scatter3d(
            x=[user_coords[0]], y=[user_coords[1]], z=[user_coords[2]],
            mode="markers+text", text=["YOU"], textposition="top center",
            marker=dict(size=13, color="#D7B45A", symbol="diamond", line=dict(width=2,color="#FFFFFF")),
            name="You",
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0), height=480,
            scene=dict(
                xaxis_title="Transcendence", yaxis_title="Collectivism", zaxis_title="Progressivism",
                xaxis=dict(range=[-1,1]), yaxis=dict(range=[-1,1]), zaxis=dict(range=[-1,1]),
            ),
        )
        st.plotly_chart(fig3, use_container_width=True, key="result_3d", config={"displaylogo": False, "responsive": True})
        st.caption("The 3D view projects the first three coordinates; the fourth dimension is shown in the radar.")

    # Affinity ranking
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["affinities_label"])
    for i, aff in enumerate(affinities):
        nm = aff["name_hi"] if is_hindi else aff["name"]
        tier = "Primary affinity" if i == 0 else ("Strong affinity" if i < 4 else "Secondary affinity")
        st.markdown(
            f"""
            <div class="wc-card" style="margin:.45rem 0;padding:.8rem 1rem">
              <div style="display:flex;justify-content:space-between;gap:1rem;align-items:center">
                <strong>{i+1}. {escape(nm)}</strong><strong style="color:var(--wc-gold)">{aff["similarity_pct"]}%</strong>
              </div>
              <div class="wc-small" style="text-transform:uppercase;letter-spacing:.06em;margin:.2rem 0 .25rem">{tier}</div>
              <div class="wc-small">{escape((aff.get("description_hi") if is_hindi else aff.get("description",""))[:180])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Compare traditions
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["comparison_title"])
    available = [s for s in WORLDVIEWS if s != top_match["name"]]
    selected = st.multiselect(
        "Traditions to compare (up to 3)",
        available,
        default=[s for s in st.session_state.comparison_schools if s in available][:3] or available[:1],
        max_selections=3,
        key="comparison_picker",
    )
    st.session_state.comparison_schools = selected
    if selected:
        comp = [(s, WORLDVIEWS[s]["vector"]) for s in selected]
        st.plotly_chart(
            radar_figure(comp, "Your coordinates"),
            use_container_width=True,
            key="comparison_radar",
            config={"displaylogo": False, "responsive": True},
        )

    # Friend duel
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["matrix_title"])
    st.caption(ui["matrix_sub"])
    friend_url = st.text_input("Friend's shared URL", placeholder="Paste a Worldview Compass share URL", key="friend_url_input")
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
                      <div class="wc-kicker">Compatibility</div>
                      <div style="font-size:2rem;font-weight:800;color:var(--wc-gold)">{consensus}%</div>
                      <p><strong>Your top:</strong> {escape(top_match["name"])}</p>
                      <p><strong>Friend's top:</strong> {escape(friend_aff[0]["name"])}</p>
                      <p><strong>Closest common ground:</strong> {escape(harmony)}</p>
                      <p><strong>Biggest divergence:</strong> {escape(battleground)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with f2:
                st.plotly_chart(
                    radar_figure([("Friend", friend_coords)]),
                    use_container_width=True,
                    key="friend_radar",
                    config={"displaylogo": False, "responsive": True},
                )
        except (ValueError, TypeError, json.JSONDecodeError, KeyError):
            st.warning("That does not look like a valid Worldview Compass result URL. Please paste the complete link.")

    # Tensions
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["challenge_title"])
    if tensions:
        for t in tensions:
            st.warning(f"{t['title']}\n\n{t['description']}", icon="⚡")
    else:
        st.success(ui["no_tensions"], icon="✓")

    # Confidence
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["confidence_title"])
    st.caption(ui["confidence_sub"])
    st.slider(
        "Epistemic confidence",
        0, 100, st.session_state.confidence, 5,
        key="confidence",
        help="This self-report is separate from the calculated worldview match.",
    )
    st.caption(f"0 = {ui['confidence_low']}  ·  100 = {ui['confidence_high']}")

    # Share/export
    st.markdown('<div class="wc-section"></div>', unsafe_allow_html=True)
    st.subheader(ui["share_heading"])
    st.caption(ui["share_sub"])

    handle = st.text_input(
        "Name for identity card (optional)",
        placeholder="e.g. Philosopher Jane",
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
    # Use the current page's query string so shared links contain the actual profile.
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
        st.link_button("𝕏  Share on X", x_url, use_container_width=True)
    with sh2:
        st.link_button("◉  WhatsApp", wa_url, use_container_width=True)
    with sh3:
        st.link_button("in  LinkedIn", li_url, use_container_width=True)
    with sh4:
        st.download_button(
            ui["passport_btn"],
            data=passport_bytes,
            file_name=f"worldview_identity_card_{top_match.get('slug','result')}.png",
            mime="image/png",
            use_container_width=True,
            type="primary",
        )

    st.markdown('<div class="wc-footer">Worldview Compass is an exploratory philosophical instrument. Results reflect the supplied answer model and should not be treated as scientific or clinical diagnosis.</div>', unsafe_allow_html=True)
