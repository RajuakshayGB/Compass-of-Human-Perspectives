"""
database.py - The Compass of Human Perspectives
Data access layer, worldview matrices, latent traits, knowledge graph edges, and question banks.
"""

from typing import Dict, List, Any, Optional

# ==============================================================================
# 1. 13 REFERENCE WORLDVIEW DEFINITIONS & 4D MATRICES
# ==============================================================================
# 4D Vector Schema: [D0: Physicalism/Transcendence, D1: Individualism/Collectivism, 
#                    D2: Traditionalism/Progressivism, D3: Rationalism/Empiricism]
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
        "description": "An ancient Greek and Roman philosophy teaching the development of self-control and fortitude to overcome destructive emotions and align with natural cosmic reason.",
        "description_hi": "एक प्राचीन ग्रीक और रोमन दर्शन जो विनाशकारी भावनाओं पर विजय पाने और प्राकृतिक ब्रह्मांडीय तर्क के साथ संरेखित होने के लिए आत्म-नियंत्रण और धैर्य के विकास की शिक्षा देता है।",
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
        "description": "A materialist philosophy and socio-economic analysis of class relations and historical progress through social struggle and collective ownership.",
        "description_hi": "वर्ग संघर्ष और सामूहिक स्वामित्व के माध्यम से ऐतिहासिक विकास और वर्ग संबंधों का विश्लेषण करने वाला एक भौतिकवादी दर्शन और सामाजिक-आर्थिक विश्लेषण।",
        "origin": {"region": "Trier, Germany", "lat": 49.7557, "lon": 6.6394, "start_year": 1848, "end_year": None},
        "canonical_texts": [{"title_en": "Das Kapital", "title_hi": "दास कैपिटल (Das Kapital)", "year": 1867}]
    },
    "Daoism": {
        "slug": "daoism",
        "name_hi": "दाओवाद",
        "vector": [0.4, -0.3, -0.3, -0.4],
        "thinkers": ["Laozi", "Zhuangzi"],
        "description": "A tradition of Chinese origin that emphasizes living in effortless harmony with the Dao (the natural, spontaneous flow of the cosmos).",
        "description_hi": "चीनी मूल की एक परंपरा जो दाओ (ब्रह्मांड के प्राकृतिक और सहज प्रवाह) के साथ सहज सामंजस्य में जीने पर जोर देती है।",
        "origin": {"region": "Henan, China", "lat": 34.75797, "lon": 113.66541, "start_year": -500, "end_year": None},
        "canonical_texts": [{"title_en": "Dao De Jing", "title_hi": "दाओ दे चिंग", "year": -400}]
    },
    "Early Buddhism": {
        "slug": "early-buddhism",
        "name_hi": "प्रारंभिक बौद्ध धर्म",
        "vector": [0.2, -0.1, 0.1, -0.6],
        "thinkers": ["Siddhartha Gautama (The Buddha)", "Nagarjuna"],
        "description": "A non-theistic spiritual path focused on overcoming suffering by understanding impermanence, non-attachment, and the illusion of a permanent self (Anatta).",
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
        "description_hi": "ईसा मसीह के जीवन और शिक्षाओं पर आधारित एक एकेश्वरवादी विश्वास, जो एक पारलौकिक व्यक्तिगत निर्माता और नैतिक उद्धारकर्ता का दावा करता है।",
        "origin": {"region": "Judea, Roman Empire", "lat": 31.7683, "lon": 35.2137, "start_year": 30, "end_year": None},
        "canonical_texts": [{"title_en": "Summa Theologiae", "title_hi": "सुम्मा थिओलोजिया", "year": 1274}]
    },
    "Ubuntu": {
        "slug": "ubuntu",
        "name_hi": "उबुन्टु",
        "vector": [0.2, 0.9, 0.3, -0.2],
        "thinkers": ["Desmond Tutu", "Nelson Mandela"],
        "description": "An African communalist philosophy asserting that personhood is relational, encapsulated in the phrase: 'I am because we are.'",
        "description_hi": "एक अफ्रीकी सांप्रदायिक दर्शन जो यह दावा करता है कि व्यक्तित्व संबंधपरक है, जिसे इस वाक्यांश में संपुटित किया गया है: 'मैं हूँ क्योंकि हम हैं।'",
        "origin": {"region": "Sub-Saharan Africa", "lat": -26.2041, "lon": 28.0473, "start_year": 1000, "end_year": None},
        "canonical_texts": [{"title_en": "No Future Without Forgiveness", "title_hi": "माफ़ी के बिना कोई भविष्य नहीं", "year": 1999}]
    },
    "Confucianism": {
        "slug": "confucianism",
        "name_hi": "कन्फ्यूशीवाद",
        "vector": [-0.1, 0.5, -0.9, -0.5],
        "thinkers": ["Confucius", "Mencius", "Xunzi"],
        "description": "An East Asian ethical and philosophical system emphasizing filial piety, social order, ritual propriety, and moral governance.",
        "description_hi": "एक पूर्वी एशियाई नैतिक और दार्शनिक प्रणाली जो पितृभक्ति, सामाजिक व्यवस्था, अनुष्ठानिक औचित्य और नैतिक शासन पर जोर देती है।",
        "origin": {"region": "Shandong, China", "lat": 35.5488, "lon": 116.9848, "start_year": -500, "end_year": None},
        "canonical_texts": [{"title_en": "The Analects", "title_hi": "कन्फ्यूशियस के विचार (The Analects)", "year": -479}]
    },
    "Deep Ecology": {
        "slug": "deep-ecology",
        "name_hi": "गहन पारिस्थितिकी",
        "vector": [0.3, 0.4, 0.2, 0.4],
        "thinkers": ["Arne Naess", "Aldo Leopold", "Rachel Carson"],
        "description": "An environmental philosophy advocating for the inherent moral rights of all living beings and ecosystems, rejecting human-centric exploitation.",
        "description_hi": "एक पर्यावरण दर्शन जो समस्त जैव-प्रणालियों में अंतर्निहित नैतिक मूल्य का समर्थन करता है और मानवीय शोषण को खारिज करता है।",
        "origin": {"region": "Oslo, Norway", "lat": 59.9139, "lon": 10.7522, "start_year": 1973, "end_year": None},
        "canonical_texts": [{"title_en": "The Shallow and the Deep", "title_hi": "उथली और गहरी पारिस्थितिकी", "year": 1973}]
    },
    "Transhumanism": {
        "slug": "transhumanism",
        "name_hi": "अतिमानवतावाद (ट्रांसह्यूमनिज़्म)",
        "vector": [-0.8, -0.2, 1.0, 0.9],
        "thinkers": ["Nick Bostrom", "Ray Kurzweil", "Max More"],
        "description": "An intellectual movement advocating for the enhancement of human biological, cognitive, and physical capabilities using advanced technology.",
        "description_hi": "उन्नत तकनीक का उपयोग करके मानव जैविक, संज्ञानात्मक और भौतिक क्षमताओं के संवर्धन की वकालत करने वाला आंदोलन।",
        "origin": {"region": "California, USA", "lat": 37.7749, "lon": -122.4194, "start_year": 1980, "end_year": None},
        "canonical_texts": [{"title_en": "The Transhumanist Reader", "title_hi": "द ट्रांसह्यूमनिस्ट रीडर", "year": 2013}]
    },
    "Existentialism": {
        "slug": "existentialism",
        "name_hi": "अस्तित्ववाद",
        "vector": [-0.3, -0.8, 0.6, -0.2],
        "thinkers": ["Jean-Paul Sartre", "Albert Camus", "Simone de Beauvoir", "Friedrich Nietzsche"],
        "description": "A modern movement asserting that existence precedes essence; humans are radically free and must author their own meaning and moral value.",
        "description_hi": "अस्तित्ववाद मानता है कि अस्तित्व सार से पहले आता है; मनुष्य पूरी तरह स्वतंत्र हैं और उन्हें अपने अर्थ स्वयं गढ़ने होंगे।",
        "origin": {"region": "Paris, France", "lat": 48.8566, "lon": 2.3522, "start_year": 1940, "end_year": None},
        "canonical_texts": [{"title_en": "Being and Nothingness", "title_hi": "होना और शून्यता (Being and Nothingness)", "year": 1943}]
    },
    "Classical Liberalism": {
        "slug": "classical-liberalism",
        "name_hi": "शास्त्रीय उदारवाद",
        "vector": [-0.6, -0.9, 0.4, 0.5],
        "thinkers": ["John Locke", "Adam Smith", "John Stuart Mill"],
        "description": "A political and economic philosophy championing individual liberty, private property, limited state governance, and voluntary market cooperation.",
        "description_hi": "व्यक्तिगत स्वतंत्रता, निजी संपत्ति, सीमित शासन और स्वैच्छिक बाजार सहयोग का समर्थन करने वाला दर्शन।",
        "origin": {"region": "England / Scotland", "lat": 51.5074, "lon": -0.1278, "start_year": 1689, "end_year": None},
        "canonical_texts": [{"title_en": "Second Treatise of Government", "title_hi": "शासन पर दूसरा निबंध", "year": 1689}]
    }
}

# ==============================================================================
# 2. PHILOSOPHICAL KNOWLEDGE GRAPH EDGES
# ==============================================================================
WORLDVIEW_EDGES = [
    {"from": "stoicism", "to": "advaita-vedanta", "type": "antagonist", "weight": 0.4, "notes": "Western materialistic self-fortification vs non-dual transcendent union."},
    {"from": "marxism", "to": "stoicism", "type": "antagonist", "weight": 0.3, "notes": "Marxist material-collective structures conflict with Stoic emotional resignation."},
    {"from": "classical-liberalism", "to": "marxism", "type": "antagonist", "weight": 0.8, "notes": "Capitalist market freedom and private property vs socialist collective ownership."},
    {"from": "confucianism", "to": "daoism", "type": "antagonist", "weight": 0.6, "notes": "Rigid social duty and ritual decorum vs effortless spontaneity and natural flow."},
    {"from": "secular-scientific-humanism", "to": "transhumanism", "type": "predecessor", "weight": 0.8, "notes": "Secular humanism provides the baseline values that transhumanism expands through technology."},
    {"from": "stoicism", "to": "existentialism", "type": "predecessor", "weight": 0.5, "notes": "Inner character, moral duty, and accepting mortality shaped existential responsibility."},
    {"from": "early-buddhism", "to": "advaita-vedanta", "type": "predecessor", "weight": 0.7, "notes": "Concepts of non-self and impermanence influenced early non-dual Vedanta."},
    {"from": "ubuntu", "to": "deep-ecology", "type": "synthesis", "weight": 0.6, "notes": "Communal kinship synthesized with biocentric ecological reciprocity."}
]

# ==============================================================================
# 3. 51 DIAGNOSTIC LATENT TRAITS REGISTRY
# ==============================================================================
LATENT_TRAITS = [
    "afterlife", "ahimsa", "animal_ethics", "anti_authoritarian", "authority",
    "biocentrism", "capitalism", "care_ethics", "collectivism", "community",
    "consequentialism", "cosmopolitanism", "deontology", "determinism",
    "empiricism", "environmentalism", "equality", "existentialism", "humanism",
    "idealism", "impermanence", "individualism", "liberty", "materialism",
    "mysticism", "nationalism", "nature_harmony", "no_self", "nondualism",
    "order", "pluralism", "pragmatism", "progressivism", "radicalism",
    "rationalism", "reincarnation", "religious_authority", "secularism",
    "self_discipline", "skepticism", "social_justice", "socialism", "soul_self",
    "spirituality", "tech_optimism", "theism", "traditionalism", "transhumanism",
    "universalism", "utilitarianism", "virtue"
]

# ==============================================================================
# 4. QUESTION DATASET & FAST-TRACK INDEXING ACCESSORS
# ==============================================================================
# Sample of structured bilingual dataset (expandable up to the full 100 questions)
QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1, "dimIndex": 0, "dimension": "Metaphysics & Reality", "track": "Track B",
        "text_en": "What ultimately constitutes the fundamental fabric of reality?",
        "text_hi": "वास्तविकता का मूल तत्व अंततः किस रूप में मौजूद है?",
        "options": [
            {"code": "A", "text_en": "Only physical matter, energy, and natural physical laws.", "text_hi": "केवल भौतिक पदार्थ, ऊर्जा और प्राकृतिक भौतिक नियम।", "deltas": {"materialism": 1.0, "spirituality": -1.0}, "weights": {"secular_humanism": 0.9, "marxism": 0.8}},
            {"code": "B", "text_en": "An uncreated, non-dual cosmic consciousness (Brahman / Absolute).", "text_hi": "अनादि, अद्वैत ब्रह्मांडीय चेतना (ब्रह्म या परम तत्व)।", "deltas": {"nondualism": 1.0, "spirituality": 1.0}, "weights": {"advaita_vedanta": 1.0}},
            {"code": "C", "text_en": "A purposeful physical universe created and sustained by God.", "text_hi": "ईश्वर द्वारा निर्मित और संचालित एक सोद्देश्य ब्रह्मांड।", "deltas": {"theism": 1.0, "spirituality": 0.8}, "weights": {"christian_theism": 1.0}},
            {"code": "D", "text_en": "An interconnected dynamic flow with no permanent substance (Dao / Flux).", "text_hi": "परस्पर जुड़ा हुआ, गतिशील प्रवाह जिसका कोई स्थायी सार नहीं (दाओ)।", "deltas": {"impermanence": 0.9, "nature_harmony": 0.9}, "weights": {"daoism": 1.0, "early_buddhism": 0.8}},
            {"code": "E", "text_en": "An empirical web of relations; metaphysical assertions are untestable.", "text_hi": "संबंधों का अनुभवजन्य जाल; तत्वमीमांसा के दावे अप्रमाणित हैं।", "deltas": {"empiricism": 0.9, "skepticism": 0.8}, "weights": {"secular_humanism": 0.8}}
        ]
    },
    {
        "id": 5, "dimIndex": 1, "dimension": "Consciousness & Mind", "track": "Track B",
        "text_en": "What is the true nature of human consciousness and subjective experience?",
        "text_hi": "मानव चेतना और व्यक्तिपरक अनुभव का वास्तविक स्वरूप क्या है?",
        "options": [
            {"code": "A", "text_en": "A neurological computation emergent from physical brain architecture.", "text_hi": "मस्तिष्क के जैविक न्यूरोलॉजिकल तंत्र का भौतिक परिणाम।", "deltas": {"materialism": 1.0, "rationalism": 0.8}, "weights": {"secular_humanism": 0.9}},
            {"code": "B", "text_en": "An uncreated ground of awareness that cannot be reduced to physical matter.", "text_hi": "ब्रह्मांड का एक मौलिक गुण जिसे केवल भौतिक पदार्थ में नहीं समेटा जा सकता।", "deltas": {"idealism": 0.9, "spirituality": 0.8}, "weights": {"advaita_vedanta": 0.9}},
            {"code": "C", "text_en": "A dynamic stream of fleeting mental events with no permanent underlying ego.", "text_hi": "क्षणिक मानसिक घटनाओं का अनवरत प्रवाह, जिसमें कोई स्थायी 'अहम' नहीं है।", "deltas": {"no_self": 1.0, "impermanence": 0.9}, "weights": {"early_buddhism": 1.0}},
            {"code": "D", "text_en": "An immortal soul endowed by the divine with moral responsibility.", "text_hi": "ईश्वर प्रदत्त एक अमर आत्मा जिसमें नैतिक उत्तरदायित्व निहित है।", "deltas": {"theism": 0.9, "soul_self": 1.0}, "weights": {"christian_theism": 0.9}},
            {"code": "E", "text_en": "An evolving information pattern capable of synthetic substrate transfer.", "text_hi": "एक विकासशील संज्ञान प्रणाली जिसे डिजिटल रूप से संवर्धित किया जा सकता है।", "deltas": {"tech_optimism": 0.9, "transhumanism": 1.0}, "weights": {"transhumanism": 1.0}}
        ]
    },
    {
        "id": 9, "dimIndex": 2, "dimension": "Epistemology & Knowledge", "track": "Track A",
        "text_en": "How do human beings reliably acquire genuine truth and knowledge?",
        "text_hi": "मनुष्य को सत्य और वास्तविक ज्ञान की प्राप्ति सबसे प्रामाणिक रूप से कैसे होती है?",
        "options": [
            {"code": "A", "text_en": "Through systematic empirical observation, repeatable tests, and scientific falsification.", "text_hi": "अनुभवजन्य अवलोकन, दोहराए जा सकने वाले प्रयोगों और वैज्ञानिक पद्धति से।", "deltas": {"empiricism": 1.0, "rationalism": 0.8}, "weights": {"secular_humanism": 1.0}},
            {"code": "B", "text_en": "By combining rigorous rational logic with direct contemplative discernment.", "text_hi": "तर्कसंगत विवेक और प्रत्यक्ष अंतर्मुखी साधना के समन्वय द्वारा।", "deltas": {"rationalism": 0.8, "mysticism": 0.7}, "weights": {"advaita_vedanta": 0.8, "stoicism": 0.7}},
            {"code": "C", "text_en": "Pragmatic verification: ideas are true if they resolve real human challenges.", "text_hi": "व्यावहारिक पुष्टि: सत्य वही है जो जीवन की वास्तविक समस्याओं का समाधान करे।", "deltas": {"pragmatism": 1.0, "secularism": 0.6}, "weights": {"secular_humanism": 0.7}},
            {"code": "D", "text_en": "Through sacred revelation transmitted across holy scriptures and lineages.", "text_hi": "धर्मग्रंथों और पवित्र परंपराओं में प्रकट ईश्वरीय ज्ञान के माध्यम से।", "deltas": {"religious_authority": 1.0, "traditionalism": 0.8}, "weights": {"confucianism": 0.6, "christian_theism": 0.7}},
            {"code": "E", "text_en": "Through multifaceted viewpoints; no single system grasps totality (Anekānta).", "text_hi": "अनेक दृष्टिकोणों (अनेकांतवाद) से; कोई एक दृष्टिकोण पूर्ण सत्य नहीं समेट सकता।", "deltas": {"pluralism": 1.0, "skepticism": 0.7}, "weights": {"daoism": 0.8}}
        ]
    },
    {
        "id": 97, "dimIndex": 24, "dimension": "Pluralism & Openness", "track": "Track A",
        "text_en": "How should society navigate deeply conflicting philosophical worldviews?",
        "text_hi": "परस्पर विरोधी और भिन्न सांस्कृतिक विचारों व मान्यताओं का सामना कैसे करना चाहिए?",
        "options": [
            {"code": "A", "text_en": "Universal rational scrutiny: all beliefs must be evaluated by evidence and human rights.", "text_hi": "सार्वभौमिक तर्क: विचारों को साक्ष्य, तर्क और मानवाधिकारों की कसौटी पर परखा जाए।", "deltas": {"rationalism": 0.9, "humanism": 0.9}, "weights": {"secular_humanism": 1.0}},
            {"code": "B", "text_en": "Deep epistemic humility: reality is multifaceted (Anekāntavāda) and exceeds single doctrines.", "text_hi": "गहरी वैचारिक विनम्रता: सत्य बहुआयामी है और किसी एक मत की बपौती नहीं।", "deltas": {"pluralism": 1.0, "skepticism": 0.8}, "weights": {"daoism": 0.9, "early_buddhism": 0.8}},
            {"code": "C", "text_en": "Radical toleration: non-coercive peaceful coexistence without imposing ideological orthodoxy.", "text_hi": "पूर्ण सहिष्णुता: दूसरों पर अपने विचार थोपे बिना शांतिपूर्ण सह-अस्तित्व।", "deltas": {"liberty": 1.0, "anti_authoritarian": 0.8}, "weights": {"classical_liberalism": 0.9}}
        ]
    }
]

# ==============================================================================
# 5. DATA ACCESSOR FUNCTIONS
# ==============================================================================
def get_worldview_data(slug_or_name: str) -> Optional[Dict[str, Any]]:
    """Retrieve worldview parameters by formal name or slug."""
    if slug_or_name in WORLDVIEWS:
        return WORLDVIEWS[slug_or_name]
    for k, v in WORLDVIEWS.items():
        if v.get("slug") == slug_or_name:
            return v
    return None

def load_questions_dataset(mode: str = "full") -> List[Dict[str, Any]]:
    """
    Returns the questionnaire set:
    - 'full': Returns all available questions across dimensions.
    - 'quick': Returns 1 question per dimension using the formula ID = 1 + (i * 4).
    """
    if mode == "quick":
        quick_ids = {1 + (i * 4) for i in range(25)}
        return [q for q in QUESTIONS if q["id"] in quick_ids]
    return QUESTIONS