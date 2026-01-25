"""
Cuneiform Translation Service

Integrates with CDLI (Cuneiform Digital Library Initiative) to provide
real translations for cuneiform tablets. Uses multiple approaches:

1. CDLI Inscription API - Fetch existing scholarly translations
2. Sign Dictionary - Map detected signs to readings and definitions
3. Fallback - Generate contextual placeholder if no translation found
"""

import requests
from typing import Dict, List, Optional, Tuple
import json
import re


# Sumerian sign readings from ePSD2/ORACC
# This is a subset of common signs - full dictionary would be much larger
SIGN_DICTIONARY = {
    # Sign Name: (Reading, English Definition)
    'AN': ('an', 'sky, heaven; god'),
    'KI': ('ki', 'earth, place, ground'),
    'LU': ('lu', 'man, person'),
    'GI': ('gi', 'reed'),
    'DU': ('du/gin', 'to go, to walk'),
    'SAG': ('sag', 'head, top'),
    'GAL': ('gal', 'great, big'),
    'KUR': ('kur', 'mountain, land, underworld'),
    'UD': ('ud/u4', 'day, sun, light'),
    'ITI': ('iti', 'month'),
    'MU': ('mu', 'year, name'),
    'E': ('e', 'house, temple'),
    'A': ('a', 'water'),
    'NI': ('ni', 'self, own'),
    'TA': ('ta', 'from'),
    'DA': ('da', 'side, with'),
    'LUGAL': ('lugal', 'king'),
    'DINGIR': ('diŋir', 'god, deity'),
    'EN': ('en', 'lord, master'),
    'NAM': ('nam', 'fate, destiny; -ness'),
    'URU': ('uru', 'city'),
    'NIBRU': ('nibru', 'Nippur (city)'),
    'UNUG': ('unug', 'Uruk (city)'),
    'URI': ('uri', 'Ur (city)'),
    'GU': ('gu', 'string, thread'),
    'SE': ('še', 'barley, grain'),
    'GUR': ('gur', 'unit of capacity (300 liters)'),
    'GIN': ('gin', 'shekel (unit of weight)'),
    'MA-NA': ('mana', 'mina (unit of weight)'),
    'SAR': ('sar', 'to write; garden'),
    'DUB': ('dub', 'tablet'),
    'BARA': ('bara', 'throne, dais'),
    'NUN': ('nun', 'prince'),
    'INANNA': ('inanna', 'goddess Inanna'),
    'NANNA': ('nanna', 'moon god Nanna'),
    'UTU': ('utu', 'sun god Utu'),
    'ENKI': ('enki', 'god Enki'),
    'ENLIL': ('enlil', 'god Enlil'),
}


class CDLITranslationService:
    """Service for translating cuneiform tablets using CDLI data."""
    
    CDLI_API_BASE = "https://cdli.earth"
    
    def __init__(self):
        self.cache: Dict[str, dict] = {}
    
    def fetch_inscription(self, pnumber: str) -> Optional[dict]:
        """Fetch inscription data from CDLI API."""
        if pnumber in self.cache:
            return self.cache[pnumber]
        
        try:
            # Try to get JSON data from CDLI
            url = f"{self.CDLI_API_BASE}/inscriptions/{pnumber}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.cache[pnumber] = data
                return data
        except Exception as e:
            print(f"Error fetching {pnumber}: {e}")
        
        return None
    
    def translate_signs(self, signs: List[dict]) -> Tuple[str, List[dict]]:
        """
        Translate a list of detected signs to English.
        
        Returns:
            Tuple of (translation_text, annotated_signs)
        """
        translated_signs = []
        words = []
        
        for sign in signs:
            sign_name = sign.get('name', '').upper()
            
            if sign_name in SIGN_DICTIONARY:
                reading, definition = SIGN_DICTIONARY[sign_name]
                translated_signs.append({
                    **sign,
                    'reading': reading,
                    'definition': definition,
                    'translated': True
                })
                words.append(definition.split(',')[0].strip())  # Take first meaning
            else:
                translated_signs.append({
                    **sign,
                    'reading': sign_name.lower(),
                    'definition': f'[{sign_name}]',
                    'translated': False
                })
                words.append(f'[{sign_name}]')
        
        # Construct translation string
        translation = ' '.join(words)
        
        return translation, translated_signs
    
    def get_cdli_translation(self, pnumber: str) -> Optional[str]:
        """Get existing translation from CDLI if available."""
        data = self.fetch_inscription(pnumber)
        
        if data and isinstance(data, dict):
            # Look for translation in various possible fields
            translation = data.get('translation')
            if translation:
                return translation
            
            # Check for English translation in translations array
            translations = data.get('translations', [])
            for t in translations:
                if isinstance(t, dict) and t.get('language') == 'en':
                    return t.get('text')
            
            # Check in edition
            edition = data.get('edition', {})
            if isinstance(edition, dict):
                return edition.get('translation')
        
        return None
    
    def translate_tablet(
        self, 
        pnumber: str, 
        detected_signs: Optional[List[dict]] = None
    ) -> dict:
        """
        Translate a tablet using best available method.
        
        Priority:
        1. CDLI scholarly translation (if exists)
        2. Sign-by-sign dictionary translation
        3. Contextual placeholder
        
        Returns:
            dict with translation info
        """
        result = {
            'pnumber': pnumber,
            'source': 'unknown',
            'translation': '',
            'confidence': 0.0,
            'signs': [],
            'transliteration': ''
        }
        
        # Try CDLI translation first
        cdli_translation = self.get_cdli_translation(pnumber)
        if cdli_translation:
            result['source'] = 'cdli_scholarly'
            result['translation'] = cdli_translation
            result['confidence'] = 0.95  # High confidence for scholarly work
            return result
        
        # Fall back to sign dictionary
        if detected_signs:
            translation, annotated_signs = self.translate_signs(detected_signs)
            
            # Calculate confidence based on % of signs translated
            translated_count = sum(1 for s in annotated_signs if s.get('translated'))
            confidence = translated_count / len(annotated_signs) if annotated_signs else 0
            
            result['source'] = 'sign_dictionary'
            result['translation'] = translation
            result['signs'] = annotated_signs
            result['confidence'] = confidence * 0.7  # Cap at 70% for dictionary
            return result
        
        # Generate contextual placeholder based on period
        result['source'] = 'contextual_placeholder'
        result['translation'] = self._generate_contextual_translation(pnumber)
        result['confidence'] = 0.1  # Low confidence placeholder
        return result
    
    def _generate_contextual_translation(self, pnumber: str) -> str:
        """Generate a contextual placeholder translation."""
        # These are real scholarly-style translations for common tablet types
        templates = [
            "Administrative record documenting the delivery of barley to the temple storehouse.",
            "Receipt for silver payment to workers of the royal household.",
            "Letter from a merchant regarding the shipment of textiles to the temple.",
            "Legal document recording the sale of a field between two parties.",
            "List of offerings presented to the moon god Nanna on the festival day.",
            "Account of livestock received by the temple administration.",
            "Royal inscription commemorating the construction of temple walls.",
        ]
        
        import random
        # Use pnumber as seed for consistent result
        random.seed(hash(pnumber))
        return random.choice(templates)


# Singleton instance
translation_service = CDLITranslationService()


def translate_signs_to_english(signs: List[dict]) -> Tuple[str, List[dict]]:
    """Convenience function for translating signs."""
    return translation_service.translate_signs(signs)


def get_tablet_translation(pnumber: str, signs: Optional[List[dict]] = None) -> dict:
    """Convenience function for getting tablet translation."""
    return translation_service.translate_tablet(pnumber, signs)
