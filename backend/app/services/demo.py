from datetime import date, datetime, timedelta, timezone
from uuid import uuid4  # noqa: F401  -- kept for future use

NOW = datetime.now(timezone.utc).replace(second=0, microsecond=0)
TODAY: date = NOW.date()


def weather():
    days = []
    for i, rain in enumerate([85, 75, 55, 35, 25, 20, 15]):
        d = (TODAY + timedelta(days=i)).isoformat()
        days.append({
            "date": d,
            "temp_min_c": 22 + i % 2,
            "temp_max_c": 31 + i % 3,
            "rain_probability": rain,
            "rainfall_mm": 8.5 if rain >= 70 else (3.0 if rain >= 50 else 0.5),
            "condition": "Rain likely" if rain >= 70 else ("Cloudy" if rain >= 40 else "Partly cloudy"),
        })
    return {
        "location": "Kanpur Nagar, Uttar Pradesh",
        "observed_at": NOW,
        "source": "Demo weather provider",
        "stale": False,
        "current_temp_c": 27.0,
        "rain_probability": 85,
        "humidity": 78,
        "wind_kph": 12.0,
        "forecast": days,
        "impact": "Rain is likely today; avoid unnecessary irrigation and monitor drainage.",
    }


def soil():
    return {
        "recorded_at": NOW - timedelta(minutes=18),
        "moisture": 72.0,
        "ph": 6.8,
        "nitrogen": 120.0,
        "phosphorus": 45.0,
        "potassium": 160.0,
        "temperature_c": 23.0,
        "freshness": "recent",
        "moisture_status": "High",
    }


def risk():
    return {
        "overall_score": 0.68,
        "disease_score": 0.42,
        "pest_score": 0.31,
        "weather_score": 0.79,
        "confidence": "medium-high",
        "factors": [
            {"factor": "High rain probability", "effect": "increases field moisture and weather-related risk", "score": 0.79},
            {"factor": "Soil moisture 72%", "effect": "irrigation demand is low today", "score": 0.72},
            {"factor": "Wheat vegetative stage", "effect": "monitor crop after wet conditions", "score": 0.45},
        ],
        "disclaimer": "Risk scores are decision-support signals, not disease or pest diagnoses.",
    }


def recommendations():
    valid = NOW + timedelta(hours=24)
    return [
        {
            "id": "demo-no-irrigation",
            "title": "Avoid irrigation today",
            "priority": "high",
            "why": "Rain probability is 85% and soil moisture is already 72%.",
            "evidence": ["Rain probability: 85%", "Soil moisture: 72%", "Wheat: vegetative stage"],
            "valid_until": valid,
            "state": "active",
        },
        {
            "id": "demo-monitor",
            "title": "Monitor wheat after rainfall",
            "priority": "medium",
            "why": "Wet conditions can increase crop stress and disease pressure.",
            "evidence": ["Weather risk: 0.79", "Rain likely today"],
            "valid_until": valid + timedelta(hours=24),
            "state": "active",
        },
    ]


def market():
    vals = [2420, 2440, 2410, 2460, 2485, 2470, 2495]
    history = []
    for i, v in enumerate(vals):
        history.append({
            "date": (TODAY - timedelta(days=6 - i)).isoformat(),
            "price": v,
            "unit": "₹/quintal",
            "source": "Demo mandi dataset",
        })
    return {
        "commodity": "Wheat",
        "market": "Kanpur Mandi",
        "unit": "₹/quintal",
        "history": history,
        "forecast_low": 2470,
        "forecast_high": 2550,
        "trend": "slightly rising",
        "signal": "Watch / compare offers",
        "confidence": "medium",
        "disclaimer": "Forecast is an estimate based on the demo dataset; it is not a guaranteed selling price.",
    }


def advisor(message: str, language: str):
    hi = language.lower().startswith("hi")
    if hi:
        answer = (
            "आज सिंचाई न करना बेहतर है। मौसम में 85% बारिश की संभावना और मिट्टी की नमी 72% है। "
            "बारिश के बाद गेहूं की फसल की निगरानी करें। यह सलाह उपलब्ध खेत डेटा पर आधारित निर्णय-सहायता है।"
        )
    else:
        answer = (
            "Avoid irrigation today. Rain probability is 85% and soil moisture is 72%. "
            "Monitor the wheat crop after rainfall. This is decision support based on the available farm data."
        )
    if any(k in message.lower() for k in ["pesticide", "कीटनाशक", "medicine", "दवा", "disease", "रोग"]):
        answer += (
            " For pesticide choice or disease diagnosis, use a qualified local agriculture expert "
            "and the approved label; this assistant does not diagnose or prescribe."
        )
    return {
        "answer": answer,
        "sources": [
            {"title": "KrishiMitra crop-risk rules", "source_id": "km-rule-wheat-rain-soil-001"},
            {"title": "Approved wheat advisory knowledge", "source_id": "km-knowledge-wheat-001"},
        ],
        "safety_note": "Estimates and recommendations should be verified against local conditions and official agricultural guidance.",
    }
