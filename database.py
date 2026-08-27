"""
database.py - The Compass of Human Perspectives
Loads complete 100-question dataset from questions.json and provides worldview matrices.
"""

import os
import json
from typing import Dict, List, Any, Optional

# ==============================================================================
# 1. 13 REFERENCE WORLDVIEWS & 4D COORDINATE VECTORS
# ==============================================================================
WORLDVIEWS: Dict[str, Dict[str, Any]] = {
    "Secular Scientific Humanism": {
        "slug": "secular-scientific-humanism",
        "name_hi": "धर्मनिरपेक्ष वैज्ञानिक मानवतावाद",
        "vector": [-1.0, 0.1, 0.8, 1.0],
        "thinkers": ["Carl Sagan", "John Dewey", "Richard Dawkins"],
        "description": "A progressive philosophy based on science, reason, human agency, and ethical responsibility, completely rejecting supernatural claims.",
        "description_hi": "विज्ञान, तर्क, मानवीय एजेंसी और नैतिक जिम्मेदारी पर आधारित एक प्रगतिशील दर्शन, जो अलौकिक दावों को पूरी तरह से खारिज करता है।",
        "origin": {"region": "London, United Kingdom", "lat": 51.5074, "lon": -0.1278, "start_year": 1952, "end_year": None},
        "canonical_texts": [{"title_en": "Humanist Manifesto I", "title_hi": "मानवतावादी घोषणापत्र I", "year": 1933}]
    },
    "Stoicism": {
        "slug": "stoicism",
        "name_hi": "स्टोइसिज्म (समभाववाद)",
        "vector": [-0.3, -0.4, -0.1, -0.5],
        "thinkers": ["Marcus Aurelius", "Seneca", "Epictetus"],
        "description": "An ancient Greek and Roman philosophy teaching self-control and fortitude to overcome destructive emotions and align with natural cosmic reason.",
        "description_hi": "एक प्राचीन ग्रीक और रोमन दर्शन जो आत्म-नियंत्रण और प्राकृतिक ब्रह्मांडीय तर्क के साथ संरेखित होने की शिक्षा देता है।",
        "origin": {"region": "Athens, Greece", "lat": 37.9838, "lon": 23.7275, "start_year": -300, "end_year": 200},
        "canonical_texts": [{"title_en": "Meditations", "title_hi": "आत्म-चिंतन (Meditations)", "year": 175}]
    },
    "Advaita Vedanta": {
        "slug": "advaita-vedanta",
        "name_hi": "अद्वैत वेदांत",
        "vector": [1.0, -0.2, -0.7, -0.8],
        "thinkers": ["Adi Shankara", "Gaudapada", "Ramana Maharshi"],
        "description": "An orthodox school of Hindu philosophy asserting that the individual self (Atman) and ultimate absolute reality (Brahman) are identical and non-dual.",
        "description_hi": "हिंदू दर्शन की एक परंपरा जो मानती है कि व्यक्तिगत आत्मा (आत्मन) और पूर्ण वास्तविकता (ब्रह्म) अभिन्न और अद्वैत हैं।",
        "origin": {"region": "Sringeri, India", "lat": 13.419, "lon": 75.253, "start_year": 700, "end_year": None},
        "canonical_texts": [{"title_en": "Brahmasutra Bhashya", "title_hi": "ब्रह्मसूत्र भाष्य", "year": 800}]
    },
    "Marxism": {
        "slug": "marxism",
        "name_hi": "मार्क्सवाद",
        "vector": [-1.0, 1.0, 0.9, 0.5],
        "thinkers": ["Karl Marx", "Friedrich Engels", "Rosa Luxemburg"],
        "description": "A materialist philosophy and socio-economic analysis of class relations and historical progress through collective ownership.",
        "description_hi": "वर्ग संघर्ष और सामूहिक स्वामित्व के माध्यम से ऐतिहासिक विकास और वर्ग संबंधों का विश्लेषण करने वाला भौतिकवादी दर्शन।",
        "origin": {"region": "Trier, Germany", "lat": 49.7557, "lon": 6.6394, "start_year": 1848, "end_year": None},
        "canonical_texts": [{"title_en": "Das Kapital", "title_hi": "दास कैपिटल (Das Kapital)", "year": 1867}]
    },
    "Daoism": {
        "slug": "daoism",
        "name_hi": "दाओवाद",
        "vector": [0.4, -0.3, -0.3, -0.4],
        "thinkers": ["Laozi", "Zhuangzi"],
        "description": "A tradition of Chinese origin that emphasizes living in effortless harmony with the Dao (the natural, spontaneous flow of the cosmos).",
        "description_hi": "चीनी मूल की एक परंपरा जो दाओ (ब्रह्मांड के प्राकृतिक और सहज प्रवाह) के साथ सामंजस्य में जीने पर जोर देती है।",
        "origin": {"region": "Henan, China", "lat": 34.75797, "lon": 113.66541, "start_year": -500, "end_year": None},
        "canonical_texts": [{"title_en": "Dao De Jing", "title_hi": "दाओ दे चिंग", "year": -400}]
    },
    "Early Buddhism": {
        "slug": "early-buddhism",
        "name_hi": "प्रारंभिक बौद्ध धर्म",
        "vector": [0.2, -0.1, 0.1, -0.6],
        "thinkers": ["Siddhartha Gautama (The Buddha)", "Nagarjuna"],
        "description": "A non-theistic spiritual path focused on overcoming suffering by understanding impermanence and the illusion of a permanent self (Anatta).",
        "description_hi": "पीड़ा से मुक्ति पाने का एक अनात्मवादी मार्ग जो अनित्यता, अनासक्ति और स्थायी आत्मन के भ्रम (अनात्ता) को समझने पर बल देता है।",
        "origin": {"region": "Magadha, India", "lat": 24.6951, "lon": 84.9913, "start_year": -500, "end_year": None},
        "canonical_texts": [{"title_en": "Dhammapada", "title_hi": "धम्मपद", "year": -300}]
    },
    "Christian Theism": {
        "slug": "christian-theism",
        "name_hi": "ईसाई आस्तिकता",
        "vector": [0.9, 0.1, -0.6, -0.4],
        "thinkers": ["Thomas Aquinas", "Augustine of Hippo", "C.S. Lewis"],
        "description": "A monotheistic faith based on the life and teachings of Jesus Christ, asserting a transcendent personal Creator and moral savior.",
        "description_hi": "ईसा मसीह के जीवन और शिक्षाओं पर आधारित विश्वास, जो एक पारलौकिक व्यक्तिगत निर्माता का दावा करता है।",
        "origin": {"region": "Judea, Roman Empire", "lat": 31.7683, "lon": 35.2137, "start_year": 30, "end_year": None},
        "canonical_texts": [{"title_en": "Summa Theologiae", "title_hi": "सुम्मा थिओलोजिया", "year": 1274}]
    },
    "Ubuntu": {
        "slug": "ubuntu",
        "name_hi": "उबुन्टु",
        "vector": [0.2, 0.9, 0.3, -0.2],
        "thinkers": ["Desmond Tutu", "Nelson Mandela"],
        "description": "An African communalist philosophy asserting that personhood is relational: 'I am because we are.'",
        "description_hi": "एक अफ्रीकी सांप्रदायिक दर्शन जो मानता है कि व्यक्तित्व संबंधपरक है: 'मैं हूँ क्योंकि हम हैं।'",
        "origin": {"region": "Sub-Saharan Africa", "lat": -26.2041, "lon": 28.0473, "start_year": 1000, "end_year": None},
        "canonical_texts": [{"title_en": "No Future Without Forgiveness", "title_hi": "माफ़ी के बिना कोई भविष्य नहीं", "year": 1999}]
    },
    "Confucianism": {
        "slug": "confucianism",
        "name_hi": "कन्फ्यूशीवाद",
        "vector": [-0.1, 0.5, -0.9, -0.5],
        "thinkers": ["Confucius", "Mencius", "Xunzi"],
        "description": "An East Asian ethical system emphasizing filial piety, social order, ritual propriety, and moral governance.",
        "description_hi": "एक पूर्वी एशियाई नैतिक प्रणाली जो पितृभक्ति, सामाजिक व्यवस्था और अनुष्ठानिक औचित्य पर जोर देती है।",
        "origin": {"region": "Shandong, China", "lat": 35.5488, "lon": 116.9848, "start_year": -500, "end_year": None},
        "canonical_texts": [{"title_en": "The Analects", "title_hi": "कन्फ्यूशियस के विचार (The Analects)", "year": -479}]
    },
    "Deep Ecology": {
        "slug": "deep-ecology",
        "name_hi": "गहन पारिस्थितिकी",
        "vector": [0.3, 0.4, 0.2, 0.4],
        "thinkers": ["Arne Naess", "Aldo Leopold", "Rachel Carson"],
        "description": "An environmental philosophy advocating for the inherent moral rights of all living beings and ecosystems.",
        "description_hi": "एक पर्यावरण दर्शन जो समस्त जैव-प्रणालियों में अंतर्निहित नैतिक मूल्य का समर्थन करता है।",
        "origin": {"region": "Oslo, Norway", "lat": 59.9139, "lon": 10.7522, "start_year": 1973, "end_year": None},
        "canonical_texts": [{"title_en": "The Shallow and the Deep", "title_hi": "उथली और गहरी पारिस्थितिकी", "year": 1973}]
    },
    "Transhumanism": {
        "slug": "transhumanism",
        "name_hi": "अतिमानवतावाद (ट्रांसह्यूमनिज़्म)",
        "vector": [-0.8, -0.2, 1.0, 0.9],
        "thinkers": ["Nick Bostrom", "Ray Kurzweil", "Max More"],
        "description": "An intellectual movement advocating for the enhancement of human biological and cognitive capabilities using advanced technology.",
        "description_hi": "उन्नत तकनीक का उपयोग करके मानव जैविक और संज्ञानात्मक क्षमताओं के संवर्धन की वकालत करने वाला आंदोलन।",
        "origin": {"region": "California, USA", "lat": 37.7749, "lon": -122.4194, "start_year": 1980, "end_year": None},
        "canonical_texts": [{"title_en": "The Transhumanist Reader", "title_hi": "द ट्रांसह्यूमनिस्ट रीडर", "year": 2013}]
    },
    "Existentialism": {
        "slug": "existentialism",
        "name_hi": "अस्तित्ववाद",
        "vector": [-0.3, -0.8, 0.6, -0.2],
        "thinkers": ["Jean-Paul Sartre", "Albert Camus", "Simone de Beauvoir", "Friedrich Nietzsche"],
        "description": "A modern movement asserting that existence precedes essence; humans are radically free and must author their own meaning.",
        "description_hi": "अस्तित्ववाद मानता है कि मनुष्य पूरी तरह स्वतंत्र हैं और उन्हें अपने अर्थ स्वयं गढ़ने होंगे।",
        "origin": {"region": "Paris, France", "lat": 48.8566, "lon": 2.3522, "start_year": 1940, "end_year": None},
        "canonical_texts": [{"title_en": "Being and Nothingness", "title_hi": "होना और शून्यता (Being and Nothingness)", "year": 1943}]
    },
    "Classical Liberalism": {
        "slug": "classical-liberalism",
        "name_hi": "शास्त्रीय उदारवाद",
        "vector": [-0.6, -0.9, 0.4, 0.5],
        "thinkers": ["John Locke", "Adam Smith", "John Stuart Mill"],
        "description": "A philosophy championing individual liberty, private property, limited state governance, and voluntary market cooperation.",
        "description_hi": "व्यक्तिगत स्वतंत्रता, निजी संपत्ति, सीमित शासन और स्वैच्छिक बाजार सहयोग का समर्थन करने वाला दर्शन।",
        "origin": {"region": "England / Scotland", "lat": 51.5074, "lon": -0.1278, "start_year": 1689, "end_year": None},
        "canonical_texts": [{"title_en": "Second Treatise of Government", "title_hi": "शासन पर दूसरा निबंध", "year": 1689}]
    }
}

# ==============================================================================
# 2. JSON QUESTION DATASET LOADER
# ==============================================================================
def load_questions_dataset(mode: str = "full") -> List[Dict[str, Any]]:
    """
    Loads questions directly from questions.json:
    - 'quick': Selects 25 questions using the formula ID = 1 + (i * 4).
    - 'full': Loads all 100 questions.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "questions.json")

    if not os.path.exists(json_path):
        # Alternative fallback check for root-level execution
        json_path = "questions.json"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            all_questions = json.load(f)
    except Exception as e:
        print(f"Error loading questions.json: {e}")
        all_questions = []

    if mode.lower() == "quick":
        quick_ids = {1 + (i * 4) for i in range(25)}
        return [q for q in all_questions if q.get("id") in quick_ids]
    
    return all_questions

def get_worldview_data(slug_or_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve worldview parameters by formal name or slug."""
    if slug_or_name in WORLDVIEWS:
        return WORLDVIEWS[slug_or_name]
    for k, v in WORLDVIEWS.items():
        if v.get("slug") == slug_or_name:
            return v
    return None