"""
gui.py / app.py - The Compass of Human Perspectives
Dedicated Frontend & Presentation Layer:
Streamlit viewports, custom CSS, state sync, interactive radio cards, and 3D Plotly visualization.
"""

import streamlit as st
import plotly.graph_objects as go

# ==============================================================================
# IMPORTS FROM DATA AND LOGIC LAYERS
# ==============================================================================
from database import WORLDVIEWS, load_questions_dataset
from engine import (
    calculate_coordinates_scaled,
    calculate_affinities,
    characterize_profile,
    check_tensions
)

# ==============================================================================
# STREAMLIT CONFIGURATION & CUSTOM EDITORIAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="The Compass of Human Perspectives",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800&family=Lora:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #090D16;
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .app-title {
        font-family: 'Cinzel', serif;
        font-weight: 800;
        font-size: 2.6rem;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.1em;
        text-align: center;
        margin-top: 1.5rem;
    }
    .app-subtitle {
        font-family: 'Lora', serif;
        font-style: italic;
        color: #94A3B8;
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-container {
        border: 1px solid rgba(255, 215, 0, 0.15);
        background: radial-gradient(circle at top, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        max-width: 900px;
        margin: 2rem auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .question-card {
        background: #0F172A;
        border: 1px solid rgba(255, 215, 0, 0.1);
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .question-dim {
        font-family: 'Cinzel', serif;
        font-size: 0.9rem;
        color: #FFD700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    
    .question-text {
        font-family: 'Lora', serif;
        font-size: 1.45rem;
        font-weight: 600;
        line-height: 1.5;
        color: #FFFFFF;
        margin-bottom: 20px;
    }
    
    .profile-card {
        background: linear-gradient(145deg, #101B2B, #0A101C);
        border-radius: 16px;
        border: 1px solid rgba(255,215,0,0.2);
        padding: 40px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    
    .profile-header {
        font-family: 'Cinzel', serif;
        font-size: 1.1rem;
        color: #FFD700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    .profile-tags {
        font-family: 'Cinzel', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 25px;
        border-bottom: 1px solid rgba(255,215,0,0.1);
        padding-bottom: 15px;
    }
    
    .tension-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
    }
    
    .tension-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        color: #EF4444;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .tension-desc {
        font-size: 0.98rem;
        line-height: 1.6;
        color: #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BILINGUAL LOCALIZATION DICTIONARY
# ==============================================================================
UI_TEXT = {
    "English": {
        "title": "The Compass of Human Perspectives",
        "subtitle": "Why do you believe what you believe?",
        "tagline": "Embark on an intellectually serious, non-judgmental exploration of your core beliefs. Discover where you stand on global spectra and explore your alignments to 13 historical lineages, from Stoicism and Advaita Vedanta to Marxism and Deep Ecology.",
        "start_btn": "Begin the Odyssey →",
        "progress_label": "Question {current} of {total}",
        "prev_btn": "← Previous",
        "next_btn": "Next →",
        "reveal_btn": "Reveal My Worldview 🧭",
        "result_title": "A Worldview Has Emerged",
        "result_subtitle": "Your custom coordinates compared with historical worldviews.",
        "map_title": "📊 Vector Space Alignment",
        "char_title": "🧭 Profile Characterization",
        "affinity_title": "Your primary philosophical affinity resembles <strong>{school}</strong> with a <strong>{similarity:.1%} similarity</strong> match.",
        "thinkers_label": "Key Thinkers in this tradition:",
        "affinities_label": "🏛️ Major Historical Lineages",
        "challenge_title": "⚡ Epistemic Challenges & Cognitive Tensions",
        "challenge_desc": "Worldviews are dynamic, and logical friction is the spark of self-discovery. Based on your selections, the engine has flagged the following active cognitive tensions:",
        "no_tensions": "🟢 No major structural tensions detected! Your worldview displays high internal consistency.",
        "confidence_title": "🔍 Epistemic Confidence and Belief Strength",
        "confidence_desc": "Worldview Explorer distinguishes between how strongly you feel about your answers vs. how open you are to changing your mind when presented with empirical or logical counter-evidence.",
        "confidence_label": "My Epistemic Confidence level (how certain I am of holding objective, absolute truths):",
        "confidence_low": "Humility (I hold my beliefs provisionally, open to new evidence)",
        "confidence_high": "Absolute Certainty (My core beliefs represent non-negotiable objective truths)"
    },
    "Hindi": {
        "title": "मानव दृष्टिकोण का कम्पास (The Compass of Human Perspectives)",
        "subtitle": "आप जो मानते हैं, क्यों मानते हैं?",
        "tagline": "अपने मूल विश्वासों की एक बौद्धिक रूप से गंभीर, गैर-न्यायिक खोज शुरू करें। जानें कि आप वैश्विक दृष्टिकोणों पर कहाँ खड़े हैं और स्टोइसिज्म, अद्वैत वेदांत से लेकर मार्क्सवाद और गहन पारिस्थितिकी तक 13 ऐतिहासिक दार्शनिक परंपराओं के साथ अपनी समानता खोजें।",
        "start_btn": "यात्रा शुरू करें →",
        "progress_label": "प्रश्न {current} का {total}",
        "prev_btn": "← पिछला",
        "next_btn": "आगे →",
        "reveal_btn": "मेरा विश्वदृष्टिकोण प्रकट करें 🧭",
        "result_title": "एक नया विश्वदृष्टिकोण उदय हुआ है",
        "result_subtitle": "ऐतिहासिक विश्वदृष्टिकोणों के साथ आपके निर्देशांकों की तुलना।",
        "map_title": "📊 वेक्टर स्पेस संरेखण",
        "char_title": "🧭 प्रोफ़ाइल लक्षण वर्णन",
        "affinity_title": "आपकी प्राथमिक दार्शनिक समानता {similarity:.1%} मैच के साथ <strong>{school}</strong> से मिलती जुलती है।",
        "thinkers_label": "इस परंपरा के प्रमुख विचारक:",
        "affinities_label": "🏛️ प्रमुख ऐतिहासिक दार्शनिक परंपराएं",
        "challenge_title": "⚡ बौद्धिक चुनौतियां और संज्ञानात्मक तनाव",
        "challenge_desc": "विश्वदृष्टिकोण गतिशील होते हैं, और विचारों का घर्षण ही आत्म-खोज का स्रोत है। आपके उत्तरों के आधार पर इंजन ने निम्नलिखित संज्ञानात्मक विरोधाभासों को चिह्नित किया है:",
        "no_tensions": "🟢 कोई बड़ा विरोधाभास नहीं पाया गया! आपका विश्वदृष्टिकोण अत्यधिक सुसंगत है।",
        "confidence_title": "🔍 बौद्धिक आत्मविश्वास और विश्वास की गहराई",
        "confidence_desc": "यह प्रणाली इस बात में अंतर करती है कि आप अपने उत्तरों को कितना मजबूत मानते हैं बनाम अनुभवजन्य या तार्किक विपरीत साक्ष्य मिलने पर आप अपनी राय बदलने के लिए कितने खुले हैं।",
        "confidence_label": "मेरा बौद्धिक आत्मविश्वास स्तर (मैं पूर्ण, निरपेक्ष सत्य रखने के बारे में कितना आश्वस्त हूँ):",
        "confidence_low": "बौद्धिक विनम्रता (मैं नए साक्ष्यों के आधार पर अपने विश्वास बदलने को तैयार हूँ)",
        "confidence_high": "पूर्ण निश्चितता (मेरे मूल विश्वास गैर-परक्राम्य और निरपेक्ष सत्य का प्रतिनिधित्व करते हैं)"
    }
}

# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "language" not in st.session_state:
    st.session_state.language = "English"
if "started" not in st.session_state:
    st.session_state.started = False
if "completed" not in st.session_state:
    st.session_state.completed = False

# ==============================================================================
# UI RENDER PIPELINE
# ==============================================================================

# Header Top-Bar
header_col1, header_col2 = st.columns([8, 2])
with header_col1:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 12px; margin-top: 15px;'>
        <span style='font-size: 2.2rem;'>🧭</span>
        <span style='font-family: "Cinzel", serif; font-weight: 700; font-size: 1.6rem; color: #FFF; letter-spacing: 0.05em;'>WORLDVIEW COMPASS</span>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    selected_lang = st.selectbox(
        "Language / भाषा",
        ["English", "Hindi"],
        index=0 if st.session_state.language == "English" else 1,
        label_visibility="collapsed"
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

st.write("---")
ui = UI_TEXT[st.session_state.language]
questions = load_questions_dataset(mode="quick")

# ------------------------------------------------------------------------------
# 1. LANDING PAGE VIEW
# ------------------------------------------------------------------------------
if not st.session_state.started and not st.session_state.completed:
    st.markdown(f"""
    <div class='hero-container'>
        <h1 style='font-size: 3rem; margin-bottom: 12px; color:#FFD700; font-family:"Cinzel", serif;'>🧭 {ui['title']}</h1>
        <p class='app-subtitle'>“{ui['subtitle']}”</p>
        <p style='max-width: 800px; margin: 30px auto; font-size: 1.15rem; line-height: 1.8; color: #CBD5E1;'>
            {ui['tagline']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([3, 4, 3])
    with col_c2:
        if st.button(ui["start_btn"], use_container_width=True, type="primary"):
            st.session_state.started = True
            st.session_state.current_question_index = 0
            st.session_state.answers = {}
            st.session_state.completed = False
            st.rerun()

# ------------------------------------------------------------------------------
# 2. QUESTION SLIDESHOW VIEW
# ------------------------------------------------------------------------------
elif st.session_state.started and not st.session_state.completed:
    idx = st.session_state.current_question_index
    q = questions[idx]
    
    progress_pct = (idx + 1) / len(questions)
    st.progress(progress_pct, text=ui["progress_label"].format(current=idx + 1, total=len(questions)))
    
    st.markdown(f"""
    <div class="question-card">
        <div class="question-dim">Dimension: {q['dimension']}</div>
        <div class="question-text">
            {q['text_en']}<br>
            <span style='font-size: 1.2rem; font-style: italic; color:#94A3B8;'>{q['text_hi']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    options_dict = {}
    options_list = []
    for opt in q["options"]:
        opt_label = f"**{opt['code']}**: {opt['text_en']} / *{opt['text_hi']}*"
        options_dict[opt_label] = opt["code"]
        options_list.append(opt_label)
        
    current_answer = st.session_state.answers.get(q["id"], None)
    default_index = 0
    if current_answer:
        default_index = next((i for i, opt in enumerate(q["options"]) if opt["code"] == current_answer), 0)
        
    selected_option = st.radio(
        "Choose your alignment:",
        options_list,
        index=default_index,
        key=f"q_{q['id']}"
    )
    
    st.session_state.answers[q["id"]] = options_dict[selected_option]
    st.write("")
    
    nav1, _, nav3 = st.columns([2, 6, 2])
    with nav1:
        if idx > 0 and st.button(ui["prev_btn"], use_container_width=True):
            st.session_state.current_question_index -= 1
            st.rerun()
    with nav3:
        if idx < len(questions) - 1:
            if st.button(ui["next_btn"], use_container_width=True, type="primary"):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button(ui["reveal_btn"], use_container_width=True, type="primary"):
                st.session_state.completed = True
                st.session_state.started = False
                st.rerun()

# ------------------------------------------------------------------------------
# 3. RESULTS & 3D VISUALIZATION VIEW
# ------------------------------------------------------------------------------
elif st.session_state.completed:
    user_coords = calculate_coordinates_scaled(st.session_state.answers, questions, "Quick")
    affinities = calculate_affinities(user_coords)
    profile_tags = characterize_profile(user_coords, st.session_state.language)
    primary_match = affinities[0]
    
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.8rem; font-family:"Cinzel", serif; color:#FFD700;'>✨ {ui['result_title']}</h1>
        <p style='color:#94A3B8; font-size: 1.15rem; font-style:italic;'>{ui['result_subtitle']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_res1, col_res2 = st.columns([5, 5])
    
    with col_res1:
        tags_joined = " • ".join(profile_tags)
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-header">{ui['char_title']}</div>
            <div class="profile-tags">{tags_joined}</div>
            <div style='font-size: 1.15rem; line-height: 1.7; color:#E2E8F0; margin-bottom: 20px;'>
                {ui['affinity_title'].format(school=primary_match['name'], similarity=primary_match['similarity_pct'])}
            </div>
            <p style='color:#94A3B8; font-size:1.0rem; line-height: 1.6; margin-bottom: 20px;'>
                {primary_match['description']}
            </p>
            <div style='font-weight: 600; color:#FFD700; margin-bottom: 5px;'>{ui['thinkers_label']}</div>
            <div style='font-style: italic; color:#E2E8F0;'>{", ".join(primary_match['thinkers'])}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_res2:
        st.markdown(f"### {ui['map_title']}")
        fig = go.Figure()
        
        wv_names, wv_x, wv_y, wv_z, wv_desc = [], [], [], [], []
        for name, data in WORLDVIEWS.items():
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
            marker=dict(size=6, color='#1E40AF', opacity=0.75, line=dict(color='rgba(255,255,255,0.2)', width=1)),
            textfont=dict(color='#CBD5E1', size=9)
        ))
        
        fig.add_trace(go.Scatter3d(
            x=[user_coords[0]], y=[user_coords[1]], z=[user_coords[2]],
            mode='markers+text',
            text=["YOU"],
            textposition="top center",
            name="Your Perspective",
            marker=dict(size=12, color='#FFD700', opacity=1.0, symbol='diamond', line=dict(color='#FFFFFF', width=2)),
            textfont=dict(color='#FFFFFF', size=14, family='Cinzel')
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=40),
            scene=dict(
                xaxis=dict(title='Transcendence', backgroundcolor='#0B0F19', color='#64748B', showbackground=True),
                yaxis=dict(title='Collectivism', backgroundcolor='#0B0F19', color='#64748B', showbackground=True),
                zaxis=dict(title='Progressivism', backgroundcolor='#0B0F19', color='#64748B', showbackground=True),
            ),
            legend=dict(x=0, y=1, bgcolor='rgba(15,23,42,0.8)')
        )
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    
    # Affinities Grid
    st.markdown(f"### {ui['affinities_label']}")
    cols_affinity = st.columns(3)
    for idx_aff, affinity in enumerate(affinities[:6]):
        with cols_affinity[idx_aff % 3]:
            st.markdown(f"""
            <div style='background:rgba(15, 23, 42, 0.7); border:1px solid rgba(255,215,0,0.08); border-radius:12px; padding:20px; margin-bottom:15px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <strong style='font-size:1.1rem; color:#FFF;'>{affinity['name']}</strong>
                    <span style='color:#FFD700; font-weight:700;'>{affinity['similarity_pct']:.1%}</span>
                </div>
                <p style='color:#94A3B8; font-size:0.92rem; line-height:1.5; margin-bottom:10px;'>{affinity['description']}</p>
                <div style='font-size:0.85rem; color:#E2E8F0;'><strong style='color:#FFD700;'>Key Thinkers:</strong> {", ".join(affinity['thinkers'])}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("---")
    
    # Cognitive Tensions
    st.markdown(f"### {ui['challenge_title']}")
    tensions = check_tensions(st.session_state.answers, st.session_state.language)
    if tensions:
        st.markdown(f"<p style='color:#cbd5e1; font-size:1.02rem;'>{ui['challenge_desc']}</p>", unsafe_allow_html=True)
        for t in tensions:
            title = t["title_hi"] if st.session_state.language == "Hindi" else t["title_en"]
            desc = t["desc_hi"] if st.session_state.language == "Hindi" else t["desc_en"]
            st.markdown(f"""
            <div class="tension-box">
                <div class="tension-title">{title}</div>
                <div class="tension-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success(ui["no_tensions"])
        
    st.write("---")
    
    # Epistemic Confidence Slider
    st.markdown(f"### {ui['confidence_title']}")
    st.markdown(f"<p style='color:#cbd5e1; font-size:1.02rem;'>{ui['confidence_desc']}</p>", unsafe_allow_html=True)
    st.slider(
        ui["confidence_label"],
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )
    st.markdown(f"""
    <div style='display:flex; justify-content:space-between; font-size:0.85rem; color:#94A3B8; margin-top:-10px; margin-bottom:20px;'>
        <span>👈 {ui['confidence_low']}</span>
        <span>{ui['confidence_high']} 👉</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🏛️ Run a New Assessment", type="primary"):
        st.session_state.completed = False
        st.session_state.started = False
        st.session_state.answers = {}
        st.session_state.current_question_index = 0
        st.rerun()