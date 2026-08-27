"""
engine.py - The Compass of Human Perspectives
Core computational engine: 4D vector mathematics, hyperbolic tangent (tanh)
spatial compression, cosine similarity matrix, profile characterization,
and dialectical cognitive tension detection.
"""

from typing import Dict, List, Any, Tuple, Union
import numpy as np


# ==============================================================================
# 1. VECTOR MATHEMATICS & SIMILARITY METRICS
# ==============================================================================
def dot_product(v1: Union[List[float], np.ndarray], v2: Union[List[float], np.ndarray]) -> float:
    """Calculates the dot product of two vectors of equal length."""
    a, b = np.array(v1, dtype=float), np.array(v2, dtype=float)
    if a.shape != b.shape:
        raise ValueError("Vector dimensions must match.")
    return float(np.dot(a, b))


def cosine_similarity(v1: Union[List[float], np.ndarray], v2: Union[List[float], np.ndarray]) -> float:
    """Calculates cosine similarity between two vectors: (v1 . v2) / (||v1|| * ||v2||)."""
    a, b = np.array(v1, dtype=float), np.array(v2, dtype=float)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


# ==============================================================================
# 2. COORDINATE SCORING ENGINES
# ==============================================================================
def calculate_coordinates_direct(
    answers: Dict[Union[int, str], str],
    questions: List[Dict[str, Any]],
    test_type: str = "Quick"
) -> List[float]:
    """
    Method A: Evaluates coordinates using embedded latent trait deltas.
    4D Vector Mapping:
      - Dim 0: Physicalism (-) vs. Transcendence (+)
      - Dim 1: Individualism (-) vs. Collectivism (+)
      - Dim 2: Traditionalism (-) vs. Progressivism (+)
      - Dim 3: Rationalism (-) vs. Empiricism (+)
    Applies hyperbolic tangent (tanh) compression to bound results to [-1.0, 1.0].
    """
    raw_vector = np.array([0.0, 0.0, 0.0, 0.0])
    q_dict = {q["id"]: q for q in questions if "id" in q}

    for q_id, choice_code in answers.items():
        q = q_dict.get(int(q_id))
        if not q or "options" not in q:
            continue

        selected_opt = next((opt for opt in q["options"] if opt.get("code") == choice_code.upper()), None)
        if not selected_opt:
            continue

        deltas = selected_opt.get("deltas", {})

        # Dim 0: Transcendence (+) vs Physicalism (-)
        raw_vector[0] += deltas.get("theism", 0.0) * 1.0
        raw_vector[0] += deltas.get("nondualism", 0.0) * 1.0
        raw_vector[0] += deltas.get("spirituality", 0.0) * 0.9
        raw_vector[0] += deltas.get("mysticism", 0.0) * 0.8
        raw_vector[0] -= deltas.get("materialism", 0.0) * 1.0

        # Dim 1: Collectivism (+) vs Individualism (-)
        raw_vector[1] += deltas.get("collectivism", 0.0) * 1.0
        raw_vector[1] += deltas.get("community", 0.0) * 0.9
        raw_vector[1] += deltas.get("care_ethics", 0.0) * 0.8
        raw_vector[1] += deltas.get("socialism", 0.0) * 0.9
        raw_vector[1] -= deltas.get("individualism", 0.0) * 1.0
        raw_vector[1] -= deltas.get("liberty", 0.0) * 0.9
        raw_vector[1] -= deltas.get("capitalism", 0.0) * 0.8

        # Dim 2: Progressivism (+) vs Traditionalism (-)
        raw_vector[2] += deltas.get("progressivism", 0.0) * 1.0
        raw_vector[2] += deltas.get("transhumanism", 0.0) * 1.0
        raw_vector[2] += deltas.get("tech_optimism", 0.0) * 0.9
        raw_vector[2] += deltas.get("radicalism", 0.0) * 0.8
        raw_vector[2] -= deltas.get("traditionalism", 0.0) * 1.0
        raw_vector[2] -= deltas.get("religious_authority", 0.0) * 0.9
        raw_vector[2] -= deltas.get("order", 0.0) * 0.7

        # Dim 3: Empiricism (+) vs Rationalism (-)
        raw_vector[3] += deltas.get("empiricism", 0.0) * 1.0
        raw_vector[3] += deltas.get("pragmatism", 0.0) * 0.8
        raw_vector[3] -= deltas.get("rationalism", 0.0) * 1.0

    total_expected = 100.0 if test_type.lower() == "full" else 25.0
    scaling_factor = 100.0 / total_expected
    compressed_vector = np.tanh(raw_vector * 0.15 * scaling_factor)
    return [round(float(val), 4) for val in compressed_vector]


# ==============================================================================
# 3. AFFINITY MATCHING & PROFILE CHARACTERIZATION
# ==============================================================================
def calculate_affinities(
    user_coords: List[float],
    worldviews: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Computes cosine similarity of the user's vector against all 13 worldviews.
    Normalizes similarity [-1.0, 1.0] to a percentage scale [0.0%, 100.0%].
    """
    results = []
    user_vec = np.array(user_coords, dtype=float)

    for name, data in worldviews.items():
        ref_vec = np.array(data["vector"], dtype=float)
        sim = cosine_similarity(user_vec, ref_vec)
        sim_pct = max(0.0, (sim + 1.0) / 2.0) * 100.0

        results.append({
            "name": name,
            "slug": data.get("slug", ""),
            "name_hi": data.get("name_hi", name),
            "similarity": round(sim, 4),
            "similarity_pct": round(sim_pct, 1),
            "description": data.get("description", ""),
            "description_hi": data.get("description_hi", ""),
            "thinkers": data.get("thinkers", []),
            "vector": data["vector"]
        })

    return sorted(results, key=lambda x: x["similarity_pct"], reverse=True)


def characterize_profile(user_coords: List[float], language: str = "English") -> List[str]:
    """Assigns bipolar diagnostic tags based on coordinate polarity (> 0.1 threshold)."""
    d0, d1, d2, d3 = user_coords

    if language.lower() == "hindi":
        return [
            "आध्यात्मिक (Spiritualist)" if d0 > 0.1 else "भौतिकवादी (Physicalist)",
            "सामुदायिक (Communitarian)" if d1 > 0.1 else "व्यक्तिवादी (Individualist)",
            "प्रगतिशील (Progressive)" if d2 > 0.1 else "पारंपरिक (Traditionalist)",
            "अनुभववादी (Empiricist)" if d3 > 0.1 else "बुद्धिवादी (Rationalist)"
        ]

    return [
        "Spiritualist" if d0 > 0.1 else "Physicalist",
        "Communitarian" if d1 > 0.1 else "Individualist",
        "Progressive" if d2 > 0.1 else "Traditionalist",
        "Empiricist" if d3 > 0.1 else "Rationalist"
    ]


# ==============================================================================
# 4. DIALECTICAL TENSION RULE ENGINE
# ==============================================================================
def check_tensions(answers: Dict[Union[int, str], str], language: str = "English") -> List[Dict[str, str]]:
    """
    Evaluates response combinations for dialectical cognitive tensions.
    Returns structured tension cards highlighting constructive nuances.
    """
    ans = {int(k): str(v).upper() for k, v in answers.items()}
    tensions = []

    # Tension 1: Mystic-Empirical Threshold
    has_brahman = ans.get(1) == "B" or ans.get(3) == "C"
    has_strict_evidence = ans.get(8) == "A" or ans.get(9) == "A" or ans.get(10) == "A"
    if has_brahman and has_strict_evidence:
        if language.lower() == "hindi":
            tensions.append({
                "title": "⚡ रहस्यवादी-अनुभवजन्य दहलीज (The Mystical-Empirical Threshold)",
                "description": "आप मानते हैं कि वास्तविकता अंततः एक गैर-द्वैत ब्रह्मांडीय चेतना (ब्रह्म) से बनी है, फिर भी आप यह भी दावा करते हैं कि वैज्ञानिक प्रतिकृति और अनुभवजन्य साक्ष्य सत्य के एकमात्र निर्णायक हैं। यह स्थिति आपको 'चेतना की कठिन समस्या' (Hard Problem of Consciousness) के केंद्र में लाती है।"
            })
        else:
            tensions.append({
                "title": "⚡ The Mystical-Empirical Threshold",
                "description": "You believe reality is grounded in a non-dual cosmic consciousness (Brahman), yet also assert that empirical science and repeatable evidence are the sole arbiters of truth. This friction mirrors the philosophical 'Hard Problem of Consciousness'."
            })

    # Tension 2: Individual Freedom vs Collective Solidarity
    has_liberty_first = ans.get(31) == "A" or ans.get(49) == "A" or ans.get(53) == "A"
    has_collective_welfare = ans.get(53) == "D" or ans.get(76) == "C"
    if has_liberty_first and has_collective_welfare:
        if language.lower() == "hindi":
            tensions.append({
                "title": "⚡ व्यक्तिगत स्वतंत्रता बनाम सामूहिक एकजुटता (Individual Freedom vs. Collective Solidarity)",
                "description": "आप मौलिक व्यक्तिगत अधिकारों को अनुलंघनीय मानते हैं, फिर भी संकट के समय सामूहिक सुरक्षा के लिए राज्य-समन्वित सामाजिक नियोजन का समर्थन करते हैं। यह शास्त्रीय उदारवाद और सामाजिक लोकतंत्र के बीच का क्लासिक संतुलन है।"
            })
        else:
            tensions.append({
                "title": "⚡ Individual Freedom vs. Collective Solidarity",
                "description": "You hold individual liberty and personal rights as inviolable boundaries, yet support state-coordinated planning and collective mandates to safeguard communal welfare. This captures the dialectic between classical liberalism and communitarian democracy."
            })

    # Tension 3: Promethean Ambition vs Ecological Reciprocity
    has_acceleration = ans.get(81) == "D" or ans.get(89) == "A" or ans.get(94) == "A"
    has_deep_ecology = ans.get(81) == "A" or ans.get(82) == "A"
    if has_acceleration and has_deep_ecology:
        if language.lower() == "hindi":
            tensions.append({
                "title": "⚡ प्रोमेथियन महत्वाकांक्षा बनाम पारिस्थितिक परस्पर संबंध (Promethean Ambition vs. Ecological Reciprocity)",
                "description": "आप तकनीकी संवर्धन और जैविक सीमाओं को पार करने का समर्थन करते हैं, फिर भी मानते हैं कि प्राकृतिक जीवमंडल का अपना आंतरिक, गैर-परक्राम्य मूल्य है। ट्रांसह्यूमनिस्ट महत्वाकांक्षा को पारिस्थितिक विनम्रता के साथ संतुलित करना इस सदी की प्रमुख चुनौती है।"
            })
        else:
            tensions.append({
                "title": "⚡ Promethean Ambition vs. Ecological Reciprocity",
                "description": "You advocate technological acceleration and post-biological enhancement, yet affirm that the biosphere possesses intrinsic, non-negotiable moral worth. Balancing transhumanist ambition with deep ecological humility is a hallmark of contemporary ethics."
            })

    return tensions