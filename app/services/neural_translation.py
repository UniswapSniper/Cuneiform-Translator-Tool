"""
Neural Cuneiform Translation Service

Uses pre-trained Hugging Face models for translating cuneiform tablets
that have never been translated before.

Models:
- praeclarum/cuneiform: Sumerian/Akkadian to English
- Thalesian/AKK-60m: Multi-task cuneiform model
"""

import os
from typing import Optional, List, Dict
import requests

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN', '')

# Available models
MODELS = {
    'praeclarum': 'praeclarum/cuneiform',
    'thalesian': 'Thalesian/AKK-60m',
}


class NeuralTranslationService:
    """Neural machine translation for cuneiform using Hugging Face models."""
    
    def __init__(self, model_name: str = 'praeclarum'):
        self.model_id = MODELS.get(model_name, MODELS['praeclarum'])
        self.api_url = f"{HF_API_URL}/{self.model_id}"
        self.headers = {}
        if HF_API_TOKEN:
            self.headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
    
    def translate(self, text: str) -> Dict:
        """
        Translate cuneiform transliteration to English.
        
        Args:
            text: ATF format transliteration (e.g., "lugal an-na ki")
            
        Returns:
            Dict with translation and metadata
        """
        result = {
            'input': text,
            'translation': '',
            'model': self.model_id,
            'confidence': 0.0,
            'source': 'neural_model',
            'error': None
        }
        
        try:
            # Call Hugging Face Inference API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict):
                        result['translation'] = data[0].get('generated_text', '')
                        result['confidence'] = data[0].get('score', 0.75)
                    else:
                        result['translation'] = str(data[0])
                        result['confidence'] = 0.75
                elif isinstance(data, dict):
                    result['translation'] = data.get('generated_text', str(data))
                    result['confidence'] = 0.75
                else:
                    result['translation'] = str(data)
                    result['confidence'] = 0.5
                    
            elif response.status_code == 503:
                # Model is loading
                result['error'] = 'Model is loading, please try again in 20 seconds'
                result['translation'] = self._fallback_translation(text)
                result['source'] = 'fallback'
                result['confidence'] = 0.3
                
            else:
                result['error'] = f'API error: {response.status_code}'
                result['translation'] = self._fallback_translation(text)
                result['source'] = 'fallback'
                result['confidence'] = 0.3
                
        except requests.exceptions.Timeout:
            result['error'] = 'Translation request timed out'
            result['translation'] = self._fallback_translation(text)
            result['source'] = 'fallback'
            result['confidence'] = 0.3
            
        except Exception as e:
            result['error'] = str(e)
            result['translation'] = self._fallback_translation(text)
            result['source'] = 'fallback'
            result['confidence'] = 0.3
        
        return result
    
    def translate_signs(self, signs: List[Dict]) -> Dict:
        """
        Translate a list of detected signs.
        
        Args:
            signs: List of sign dicts with 'name' and 'reading' fields
            
        Returns:
            Translation result
        """
        # Convert signs to ATF-like format
        readings = []
        for sign in signs:
            reading = sign.get('reading') or sign.get('name', '').lower()
            readings.append(reading)
        
        # Join as transliteration string
        transliteration = ' '.join(readings)
        
        return self.translate(transliteration)
    
    def _fallback_translation(self, text: str) -> str:
        """Generate a basic translation using the sign dictionary."""
        from .translation_service import translate_signs_to_english
        
        # Parse text into signs
        words = text.strip().split()
        signs = [{'name': w.upper(), 'reading': w} for w in words]
        
        translation, _ = translate_signs_to_english(signs)
        return translation


# Try using local model if transformers is available
class LocalNeuralTranslation:
    """Local neural translation using downloaded Hugging Face model."""
    
    def __init__(self, model_name: str = 'praeclarum/cuneiform'):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_attempted = False
    
    def _load_model(self):
        """Lazy load the model."""
        if self._load_attempted:
            return self.model is not None
            
        self._load_attempted = True
        
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            
            print(f"Loading cuneiform translation model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            print("Model loaded successfully!")
            return True
            
        except ImportError:
            print("transformers library not installed. Using API fallback.")
            return False
        except Exception as e:
            print(f"Failed to load model: {e}. Using API fallback.")
            return False
    
    def translate(self, text: str) -> Dict:
        """Translate using local model."""
        if not self._load_model():
            # Fall back to API
            api_service = NeuralTranslationService()
            return api_service.translate(text)
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True)
            outputs = self.model.generate(**inputs, max_length=512)
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                'input': text,
                'translation': translation,
                'model': self.model_name,
                'confidence': 0.80,
                'source': 'local_model',
                'error': None
            }
        except Exception as e:
            return {
                'input': text,
                'translation': '',
                'model': self.model_name,
                'confidence': 0.0,
                'source': 'error',
                'error': str(e)
            }


# Singleton instances
_neural_service = None
_local_service = None


def get_neural_translation(text: str, use_local: bool = False) -> Dict:
    """Get neural translation for cuneiform text."""
    global _neural_service, _local_service
    
    if use_local:
        if _local_service is None:
            _local_service = LocalNeuralTranslation()
        return _local_service.translate(text)
    else:
        if _neural_service is None:
            _neural_service = NeuralTranslationService()
        return _neural_service.translate(text)


def translate_tablet_neural(signs: List[Dict]) -> Dict:
    """Translate a tablet using neural model."""
    global _neural_service
    
    if _neural_service is None:
        _neural_service = NeuralTranslationService()
    
    return _neural_service.translate_signs(signs)
