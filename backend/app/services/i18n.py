from typing import Dict, Optional

# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "fire": "Fire",
        "flood": "Flood",
        "earthquake": "Earthquake",
        "storm": "Storm",
        "tornado": "Tornado",
        "unknown": "Unknown",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "location_not_specified": "Location not specified",
        "confirmed_incident": "Confirmed Incident",
        "witnesses": "witnesses",
        "danger_zone": "Danger Zone",
        "avoid_this_area": "Avoid this area"
    },
    "es": {
        "fire": "Incendio",
        "flood": "Inundación",
        "earthquake": "Terremoto",
        "storm": "Tormenta",
        "tornado": "Tornado",
        "unknown": "Desconocido",
        "low": "Bajo",
        "medium": "Medio",
        "high": "Alto",
        "location_not_specified": "Ubicación no especificada",
        "confirmed_incident": "Incidente Confirmado",
        "witnesses": "testigos",
        "danger_zone": "Zona de Peligro",
        "avoid_this_area": "Evite esta área"
    },
    "fr": {
        "fire": "Feu",
        "flood": "Inondation",
        "earthquake": "Tremblement de terre",
        "storm": "Tempête",
        "tornado": "Tornade",
        "unknown": "Inconnu",
        "low": "Faible",
        "medium": "Moyen",
        "high": "Élevé",
        "location_not_specified": "Emplacement non spécifié",
        "confirmed_incident": "Incident Confirmé",
        "witnesses": "témoins",
        "danger_zone": "Zone de Danger",
        "avoid_this_area": "Évitez cette zone"
    }
}


def translate(key: str, language: str = "en") -> str:
    """
    Translate a key to the specified language
    
    Args:
        key: Translation key
        language: Language code (en, es, fr)
        
    Returns:
        Translated string or key if translation not found
    """
    if language not in TRANSLATIONS:
        language = "en"
    
    return TRANSLATIONS.get(language, {}).get(key, key)


def translate_hazard_type(hazard_type: Optional[str], language: str = "en") -> str:
    """Translate hazard type"""
    if not hazard_type:
        return translate("unknown", language)
    return translate(hazard_type.lower(), language) or hazard_type


def translate_severity(severity: Optional[str], language: str = "en") -> str:
    """Translate severity"""
    if not severity:
        return translate("unknown", language)
    return translate(severity.lower(), language) or severity

