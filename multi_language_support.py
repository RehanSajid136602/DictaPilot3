"""
DictaPilot Multi-Language Support Module
Handles language detection, switching, and 100+ language support.

MIT License
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import platform
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


def get_language_config_path() -> Path:
    """Get platform-specific language config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "language_config.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "language_config.json"


def get_language_config_dir() -> Path:
    """Create and return language config directory"""
    config_path = get_language_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


# Language code to name mapping
LANGUAGE_CODES = {
    # Common languages
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ru": "Russian", "zh": "Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "hi": "Hindi",
    "nl": "Dutch", "pl": "Polish", "tr": "Turkish", "vi": "Vietnamese",
    "th": "Thai", "sv": "Swedish", "da": "Danish", "fi": "Finnish",
    "no": "Norwegian", "cs": "Czech", "el": "Greek", "he": "Hebrew",
    "id": "Indonesian", "ms": "Malay", "ro": "Romanian", "uk": "Ukrainian",
    # Extended languages
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "hy": "Armenian",
    "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian", "bn": "Bengali",
    "bs": "Bosnian", "bg": "Bulgarian", "my": "Burmese", "ca": "Catalan",
    "ceb": "Cebuano", "ny": "Chichewa", "co": "Corsican", "hr": "Croatian",
    "doi": "Dogri", "eo": "Esperanto", "et": "Estonian", "tl": "Filipino",
    "fy": "Frisian", "ka": "Georgian", "gu": "Gujarati", "ht": "Haitian Creole",
    "ha": "Hausa", "haw": "Hawaiian", "hu": "Hungarian", "is": "Icelandic",
    "ig": "Igbo", "ga": "Irish", "jv": "Javanese", "kn": "Kannada",
    "kk": "Kazakh", "km": "Khmer", "ku": "Kurdish", "ky": "Kyrgyz",
    "lo": "Lao", "la": "Latin", "lv": "Latvian", "lt": "Lithuanian",
    "lb": "Luxembourgish", "mk": "Macedonian", "mg": "Malagasy", "ml": "Malayalam",
    "mt": "Maltese", "mi": "Maori", "mr": "Marathi", "mn": "Mongolian",
    "ne": "Nepali", "ps": "Pashto", "fa": "Persian", "pa": "Punjabi",
    "qu": "Quechua", "sm": "Samoan", "gd": "Scottish Gaelic", "sr": "Serbian",
    "st": "Sesotho", "sn": "Shona", "sd": "Sindhi", "si": "Sinhala",
    "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "su": "Sundanese",
    "sw": "Swahili", "tg": "Tajik", "ta": "Tamil", "tt": "Tatar",
    "te": "Telugu", "ug": "Uyghur", "ur": "Urdu", "uz": "Uzbek",
    "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba",
    "zu": "Zulu"
}

# Language-specific characters for detection
LANGUAGE_CHAR_PATTERNS = {
    "ar": re.compile(r'[\u0600-\u06FF]'),
    "he": re.compile(r'[\u0590-\u05FF]'),
    "zh": re.compile(r'[\u4E00-\u9FFF]'),
    "ja": re.compile(r'[\u3040-\u309F\u30A0-\u30FF]'),
    "ko": re.compile(r'[\uAC00-\uD7AF]'),
    "ru": re.compile(r'[\u0400-\u04FF]'),
    "el": re.compile(r'[\u0370-\u03FF]'),
    "hi": re.compile(r'[\u0900-\u097F]'),
    "th": re.compile(r'[\u0E00-\u0E7F]'),
    "bn": re.compile(r'[\u0980-\u09FF]'),
    "ta": re.compile(r'[\u0B80-\u0BFF]'),
    "te": re.compile(r'[\u0C00-\u0C7F]'),
    "ml": re.compile(r'[\u0D00-\u0D7F]'),
    "gu": re.compile(r'[\u0A80-\u0AFF]'),
    "kn": re.compile(r'[\u0C80-\u0CFF]'),
    "mr": re.compile(r'[\u0900-\u097F]'),
    "pa": re.compile(r'[\u0A00-\u0A7F]'),
}

# Common words for language detection
LANGUAGE_INDICATORS = {
    "en": {"the", "is", "are", "was", "were", "have", "has", "been", "being", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", "from", "as", "into", "through", "during", "before", "after", "above", "below", "between", "under", "again", "further", "then", "once"},
    "es": {"el", "la", "los", "las", "un", "una", "unos", "unas", "es", "son", "está", "están", "fue", "fueron", "ser", "estar", "ha", "han", "haber", "hace", "hacen", "hizo", "hicieron", "poder", "querer", "saber", "decir", "ver", "dar", "saber", "tener", "venir", "ir", "llegar", "pasar", "existir", "parecer", "conocer", "pensar", "entender", "querer", "sentir", "trabajar", "tomar", "hablar", "escribir", "leer", "comer", "beber", "vivir", "sentir"},
    "fr": {"le", "la", "les", "un", "une", "des", "est", "sont", "été", "être", "avoir", "fait", "faire", "pouvoir", "vouloir", "dire", "voir", "savoir", "prendre", "venir", "arriver", "paraître", "devenir", "entendre", "donner", "poser", "tenir", "croire", "regarder", "comprendre", "parler", "écrire", "lire", "manger", "boire", "vivre", "sentir", "servir", "porter", "jouer"},
    "de": {"der", "die", "das", "ein", "eine", "einer", "einem", "einen", "ist", "sind", "war", "waren", "sein", "haben", "hat", "hatte", "hatten", "werden", "wird", "wurde", "wurden", "können", "kann", "konnte", "wollen", "will", "wollte", "müssen", "muss", "musste", "sollen", "soll", "sollte", "dürfen", "darf", "durfte", "sagen", "wissen", "wird", "werden", "geben", "gibt", "ging", "gehen", "kommen", "kamen", "sehen", "sieht", "nahm", "nehmen"},
    "it": {"il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "è", "sono", "era", "erano", "essere", "avere", "ha", "aveva", "fare", "fa", "fare", "potere", "può", "poteva", "volere", "vuole", "voleva", "dire", "dice", "disse", "vedere", "vede", "vide", "sapere", "sa", "sapeva", "venire", "viene", "venne", "andare", "va", "andò", "stare", "sta", "stette", "dare", "dà", "diede", "parlare", "parla", "parlò", "scrivere", "scrive", "scrisse", "leggere", "legge", "lesse", "mangiare", "mangia", "mangiò", "bere", "beve", "bevve"},
    "pt": {"o", "a", "os", "as", "um", "uma", "uns", "umas", "é", "são", "foi", "foram", "ser", "estar", "ter", "há", "havia", "fazer", "faz", "fez", "poder", "pode", "podia", "querer", "quer", "queria", "dizer", "diz", "disse", "ver", "vê", "viu", "saber", "sabe", "sabia", "vir", "vem", "veio", "ir", "vai", "foi", "chegar", "chega", "chegou", "parecer", "parece", "pareceu"},
    "ru": {"и", "в", "не", "на", "я", "быть", "он", "с", "это", "а", "что", "по", "из", "к", "весь", "она", "как", "у", "мы", "за", "вы", "от", "до", "для", "при", "или", "то", "же", "только", "его", "но", "да", "ее", "ли", "если", "هم", "было", "был", "была"},
    "zh": {"的", "一", "是", "不", "了", "在", "人", "有", "我", "他", "这", "个", "们", "中", "来", "上", "大", "为", "和", "地", "到", "以", "说", "时", "要", "就", "出", "会", "可", "也", "你", "对", "生", "能", "而", "子", "那", "得", "于", "着", "下", "自", "之", "年", "再", "只", "想", "来", "后", "然", "作", "方", "成", "者", "日", "都", "三", "小", "军", "二", "无", "同", "么", "经", "法"},
    "ja": {"の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある", "いる", "も", "する", "から", "な", "こと", "として", "い", "や", "れる", "なっ", "ない", "この", "ため", "その", "あっ", "よう", "また", "もの", "という", "あり", "まで", "られ", "なる", "へ", "か", "だ", "これ", "によって", "により", "おり", "より", "による", "ず", "なり", "られる", "において", "ば", "なかっ", "なく", "しかし", "について", "せ", "だっ", "できる", "それ", "う", "ので", "なお", "のみ", "でき", "き", "つ", "における", "および", "いう", "さらに", "でも", "ら", "たり", "その他", "に関する", "たち", "ます", "ん", "です"},
    "ko": {"이", "의", "가", "을", "를", "에", "에서", "와", "과", "도", "는", "은", "로", "으로", "하다", "되다", "있다", "없다", "않다", "같다", "보다", "알다", "받다", "주다", "가다", "오다", "만들다", "말하다", "보다", "알다", "쓰다", "읽다", "가졌다", "주었다", "되었다", "싶다", " 못하는", "이다", "있다"}
}


class LanguageCode(Enum):
    """Supported language codes"""
    EN = "en"
    ES = "fr"
    DE = "de"
    IT = "it"
    PT = "pt"
    FR = "fr"
    ZH = "zh"
    JA = "ja"
    KO = "ko"
    RU = "ru"
    AR = "ar"
    HI = "hi"


@dataclass
class LanguagePreference:
    """Language preference for application"""
    app_type: str
    language: str
    auto_detect: bool = True


class LanguageDetector:
    """Detects language from text"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
    
    def detect(self, text: str) -> Tuple[str, float]:
        """Detect language from text"""
        if not text or len(text.strip()) < 3:
            return "en", 0.0
        
        # First try character-based detection
        lang, confidence = self._detect_by_chars(text)
        if confidence > 0.9:
            return lang, confidence
        
        # Then try word-based detection
        lang2, confidence2 = self._detect_by_words(text)
        
        # Combine results
        if confidence2 > confidence:
            return lang2, confidence2
        
        return lang, max(confidence, confidence2 * 0.8)
    
    def _detect_by_chars(self, text: str) -> Tuple[str, float]:
        """Detect by character patterns"""
        best_lang = "en"
        best_score = 0.0
        
        for lang, pattern in LANGUAGE_CHAR_PATTERNS.items():
            matches = len(pattern.findall(text))
            score = matches / max(len(text), 1)
            
            if score > best_score:
                best_score = score
                best_lang = lang
        
        return best_lang, best_score * 10  # Scale up
    
    def _detect_by_words(self, text: str) -> Tuple[str, float]:
        """Detect by common words"""
        words = set(text.lower().split())
        
        best_lang = "en"
        best_score = 0.0
        
        for lang, indicators in LANGUAGE_INDICATORS.items():
            matches = len(words & indicators)
            score = matches / max(len(indicators), 1)
            
            if score > best_score:
                best_score = score
                best_lang = lang
        
        return best_lang, best_score
    
    def detect_with_alternatives(self, text: str, top_n: int = 3) -> List[Tuple[str, float]]:
        """Detect language with multiple alternatives"""
        if not text or len(text.strip()) < 3:
            return [("en", 0.5)]
        
        scores: Dict[str, float] = {}
        
        # Character-based scoring
        for lang, pattern in LANGUAGE_CHAR_PATTERNS.items():
            matches = len(pattern.findall(text))
            scores[lang] = scores.get(lang, 0) + matches * 2
        
        # Word-based scoring
        words = set(text.lower().split())
        for lang, indicators in LANGUAGE_INDICATORS.items():
            matches = len(words & indicators)
            scores[lang] = scores.get(lang, 0) + matches
        
        # Sort by score
        sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_langs[:top_n]


class LanguageManager:
    """Manages multi-language support and preferences"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.current_language = "en"
        self.preferences: Dict[str, LanguagePreference] = {}
        self.language_history: List[Tuple[str, float]] = []
        self.auto_detect = True
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        config_path = get_language_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.current_language = data.get('current_language', 'en')
                    self.auto_detect = data.get('auto_detect', True)
                    
                    prefs = data.get('preferences', {})
                    for app_type, pref_data in prefs.items():
                        self.preferences[app_type] = LanguagePreference(**pref_data)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save configuration"""
        get_language_config_dir()
        config_path = get_language_config_path()
        
        data = {
            'current_language': self.current_language,
            'auto_detect': self.auto_detect,
            'preferences': {
                app_type: {
                    'app_type': pref.app_type,
                    'language': pref.language,
                    'auto_detect': pref.auto_detect
                }
                for app_type, pref in self.preferences.items()
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language from text"""
        lang, confidence = self.detector.detect(text)
        
        # Update history
        self.language_history.append((lang, confidence))
        if len(self.language_history) > 100:
            self.language_history.pop(0)
        
        return lang, confidence
    
    def set_language(self, language: str):
        """Set current language"""
        if language in LANGUAGE_CODES:
            self.current_language = language
            self._save_config()
    
    def set_auto_detect(self, enabled: bool):
        """Enable/disable auto-detection"""
        self.auto_detect = enabled
        self._save_config()
    
    def set_app_preference(self, app_type: str, language: str, auto_detect: bool = True):
        """Set language preference for specific app type"""
        self.preferences[app_type] = LanguagePreference(
            app_type=app_type,
            language=language,
            auto_detect=auto_detect
        )
        self._save_config()
    
    def get_preferred_language(self, app_type: str = "default") -> str:
        """Get preferred language for app"""
        if app_type in self.preferences:
            pref = self.preferences[app_type]
            if pref.auto_detect and self.auto_detect:
                return self.current_language
            return pref.language
        
        return self.current_language
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        return LANGUAGE_CODES.get(code, code.upper())
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages"""
        return [
            {"code": code, "name": name}
            for code, name in sorted(LANGUAGE_CODES.items(), key=lambda x: x[1])
        ]
    
    def get_detection_history(self) -> List[Dict[str, Any]]:
        """Get language detection history"""
        return [
            {"language": lang, "confidence": conf}
            for lang, conf in self.language_history[-20:]
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get language usage statistics"""
        if not self.language_history:
            return {
                "current": self.current_language,
                "auto_detect": self.auto_detect,
                "total_detections": 0
            }
        
        # Count languages
        lang_counts: Dict[str, int] = {}
        total_confidence = 0.0
        
        for lang, conf in self.language_history:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            total_confidence += conf
        
        return {
            "current": self.current_language,
            "auto_detect": self.auto_detect,
            "total_detections": len(self.language_history),
            "avg_confidence": round(total_confidence / len(self.language_history), 2),
            "language_distribution": {
                self.get_language_name(k): v 
                for k, v in lang_counts.items()
            }
        }


# Global instance
_language_manager_instance: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """Get or create the global language manager instance"""
    global _language_manager_instance
    if _language_manager_instance is None:
        _language_manager_instance = LanguageManager()
    return _language_manager_instance
