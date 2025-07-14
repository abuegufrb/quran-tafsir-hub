from flask import Flask, render_template, request, jsonify
import requests
import json
import re
from difflib import SequenceMatcher

app = Flask(__name__)

# Load local verses database
try:
    with open("verses_db.json", "r", encoding="utf-8") as f:
        verses_db = json.load(f)
except FileNotFoundError:
    verses_db = []

# Surah names mapping (Arabic and English)
SURAH_NAMES = {
    1: {"ar": "الفاتحة", "en": "Al-Fatiha"},
    2: {"ar": "البقرة", "en": "Al-Baqarah"},
    3: {"ar": "آل عمران", "en": "Ali 'Imran"},
    4: {"ar": "النساء", "en": "An-Nisa"},
    5: {"ar": "المائدة", "en": "Al-Ma'idah"},
    6: {"ar": "الأنعام", "en": "Al-An'am"},
    7: {"ar": "الأعراف", "en": "Al-A'raf"},
    8: {"ar": "الأنفال", "en": "Al-Anfal"},
    9: {"ar": "التوبة", "en": "At-Tawbah"},
    10: {"ar": "يونس", "en": "Yunus"},
    11: {"ar": "هود", "en": "Hud"},
    12: {"ar": "يوسف", "en": "Yusuf"},
    13: {"ar": "الرعد", "en": "Ar-Ra'd"},
    14: {"ar": "إبراهيم", "en": "Ibrahim"},
    15: {"ar": "الحجر", "en": "Al-Hijr"},
    16: {"ar": "النحل", "en": "An-Nahl"},
    17: {"ar": "الإسراء", "en": "Al-Isra"},
    18: {"ar": "الكهف", "en": "Al-Kahf"},
    19: {"ar": "مريم", "en": "Maryam"},
    20: {"ar": "طه", "en": "Taha"},
    21: {"ar": "الأنبياء", "en": "Al-Anbya"},
    22: {"ar": "الحج", "en": "Al-Hajj"},
    23: {"ar": "المؤمنون", "en": "Al-Mu'minun"},
    24: {"ar": "النور", "en": "An-Nur"},
    25: {"ar": "الفرقان", "en": "Al-Furqan"},
    26: {"ar": "الشعراء", "en": "Ash-Shu'ara"},
    27: {"ar": "النمل", "en": "An-Naml"},
    28: {"ar": "القصص", "en": "Al-Qasas"},
    29: {"ar": "العنكبوت", "en": "Al-'Ankabut"},
    30: {"ar": "الروم", "en": "Ar-Rum"},
    31: {"ar": "لقمان", "en": "Luqman"},
    32: {"ar": "السجدة", "en": "As-Sajdah"},
    33: {"ar": "الأحزاب", "en": "Al-Ahzab"},
    34: {"ar": "سبأ", "en": "Saba"},
    35: {"ar": "فاطر", "en": "Fatir"},
    36: {"ar": "يس", "en": "Ya-Sin"},
    37: {"ar": "الصافات", "en": "As-Saffat"},
    38: {"ar": "ص", "en": "Sad"},
    39: {"ar": "الزمر", "en": "Az-Zumar"},
    40: {"ar": "غافر", "en": "Ghafir"},
    41: {"ar": "فصلت", "en": "Fussilat"},
    42: {"ar": "الشورى", "en": "Ash-Shuraa"},
    43: {"ar": "الزخرف", "en": "Az-Zukhruf"},
    44: {"ar": "الدخان", "en": "Ad-Dukhan"},
    45: {"ar": "الجاثية", "en": "Al-Jathiyah"},
    46: {"ar": "الأحقاف", "en": "Al-Ahqaf"},
    47: {"ar": "محمد", "en": "Muhammad"},
    48: {"ar": "الفتح", "en": "Al-Fath"},
    49: {"ar": "الحجرات", "en": "Al-Hujurat"},
    50: {"ar": "ق", "en": "Qaf"},
    51: {"ar": "الذاريات", "en": "Adh-Dhariyat"},
    52: {"ar": "الطور", "en": "At-Tur"},
    53: {"ar": "النجم", "en": "An-Najm"},
    54: {"ar": "القمر", "en": "Al-Qamar"},
    55: {"ar": "الرحمن", "en": "Ar-Rahman"},
    56: {"ar": "الواقعة", "en": "Al-Waqi'ah"},
    57: {"ar": "الحديد", "en": "Al-Hadid"},
    58: {"ar": "المجادلة", "en": "Al-Mujadila"},
    59: {"ar": "الحشر", "en": "Al-Hashr"},
    60: {"ar": "الممتحنة", "en": "Al-Mumtahanah"},
    61: {"ar": "الصف", "en": "As-Saff"},
    62: {"ar": "الجمعة", "en": "Al-Jumu'ah"},
    63: {"ar": "المنافقون", "en": "Al-Munafiqun"},
    64: {"ar": "التغابن", "en": "At-Taghabun"},
    65: {"ar": "الطلاق", "en": "At-Talaq"},
    66: {"ar": "التحريم", "en": "At-Tahrim"},
    67: {"ar": "الملك", "en": "Al-Mulk"},
    68: {"ar": "القلم", "en": "Al-Qalam"},
    69: {"ar": "الحاقة", "en": "Al-Haqqah"},
    70: {"ar": "المعارج", "en": "Al-Ma'arij"},
    71: {"ar": "نوح", "en": "Nuh"},
    72: {"ar": "الجن", "en": "Al-Jinn"},
    73: {"ar": "المزمل", "en": "Al-Muzzammil"},
    74: {"ar": "المدثر", "en": "Al-Muddaththir"},
    75: {"ar": "القيامة", "en": "Al-Qiyamah"},
    76: {"ar": "الإنسان", "en": "Al-Insan"},
    77: {"ar": "المرسلات", "en": "Al-Mursalat"},
    78: {"ar": "النبأ", "en": "An-Naba"},
    79: {"ar": "النازعات", "en": "An-Nazi'at"},
    80: {"ar": "عبس", "en": "Abasa"},
    81: {"ar": "التكوير", "en": "At-Takwir"},
    82: {"ar": "الانفطار", "en": "Al-Infitar"},
    83: {"ar": "المطففين", "en": "Al-Mutaffifin"},
    84: {"ar": "الانشقاق", "en": "Al-Inshiqaq"},
    85: {"ar": "البروج", "en": "Al-Buruj"},
    86: {"ar": "الطارق", "en": "At-Tariq"},
    87: {"ar": "الأعلى", "en": "Al-A'la"},
    88: {"ar": "الغاشية", "en": "Al-Ghashiyah"},
    89: {"ar": "الفجر", "en": "Al-Fajr"},
    90: {"ar": "البلد", "en": "Al-Balad"},
    91: {"ar": "الشمس", "en": "Ash-Shams"},
    92: {"ar": "الليل", "en": "Al-Layl"},
    93: {"ar": "الضحى", "en": "Ad-Duhaa"},
    94: {"ar": "الشرح", "en": "Ash-Sharh"},
    95: {"ar": "التين", "en": "At-Tin"},
    96: {"ar": "العلق", "en": "Al-'Alaq"},
    97: {"ar": "القدر", "en": "Al-Qadr"},
    98: {"ar": "البينة", "en": "Al-Bayyinah"},
    99: {"ar": "الزلزلة", "en": "Az-Zalzalah"},
    100: {"ar": "العاديات", "en": "Al-'Adiyat"},
    101: {"ar": "القارعة", "en": "Al-Qari'ah"},
    102: {"ar": "التكاثر", "en": "At-Takathur"},
    103: {"ar": "العصر", "en": "Al-'Asr"},
    104: {"ar": "الهمزة", "en": "Al-Humazah"},
    105: {"ar": "الفيل", "en": "Al-Fil"},
    106: {"ar": "قريش", "en": "Quraysh"},
    107: {"ar": "الماعون", "en": "Al-Ma'un"},
    108: {"ar": "الكوثر", "en": "Al-Kawthar"},
    109: {"ar": "الكافرون", "en": "Al-Kafirun"},
    110: {"ar": "النصر", "en": "An-Nasr"},
    111: {"ar": "المسد", "en": "Al-Masad"},
    112: {"ar": "الإخلاص", "en": "Al-Ikhlas"},
    113: {"ar": "الفلق", "en": "Al-Falaq"},
    114: {"ar": "الناس", "en": "An-Nas"}
}

def normalize_arabic(text):
    """Normalize Arabic text by removing diacritics and standardizing characters"""
    if not text:
        return ""
    
    # Remove diacritics
    arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
    text = arabic_diacritics.sub('', text)
    
    # Normalize alef variants
    text = re.sub(r'[آأإ]', 'ا', text)
    text = re.sub(r'[ؤ]', 'و', text)
    text = re.sub(r'[ئ]', 'ي', text)
    text = re.sub(r'[ة]', 'ه', text)
    
    return text.strip()

def similarity_score(a, b):
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def parse_reference(query):
    """Parse reference like '2:5' or 'البقرة:5'"""
    # Try number:number format
    match = re.match(r'^(\d+):(\d+)$', query.strip())
    if match:
        sura, aya = int(match.group(1)), int(match.group(2))
        if 1 <= sura <= 114 and aya >= 1:
            return sura, aya
    
    # Try surah name:number format
    for sura_num, names in SURAH_NAMES.items():
        if query.lower().startswith(names["en"].lower() + ":") or query.startswith(names["ar"] + ":"):
            try:
                aya = int(query.split(":")[1])
                if aya >= 1:
                    return sura_num, aya
            except:
                pass
    
    return None, None

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    # Parse reference first
    sura, aya = parse_reference(query)
    if sura and aya:
        suggestions.append({
            'type': 'reference',
            'text': f"{SURAH_NAMES[sura]['ar']} ({sura}:{aya})",
            'value': f"{sura}:{aya}"
        })
    
    # Surah name suggestions
    query_normalized = normalize_arabic(query.lower())
    for sura_num, names in SURAH_NAMES.items():
        ar_name = normalize_arabic(names["ar"].lower())
        en_name = names["en"].lower()
        
        if (query_normalized in ar_name or 
            query.lower() in en_name or 
            similarity_score(query_normalized, ar_name) > 0.6 or
            similarity_score(query.lower(), en_name) > 0.6):
            
            suggestions.append({
                'type': 'surah',
                'text': f"{names['ar']} - {names['en']} ({sura_num})",
                'value': str(sura_num)
            })
    
    # Add verse content suggestions from local database
    for verse in verses_db:
        text = verse.get('text', '')
        tafsir = verse.get('tafsir', '')
        
        # Check if query matches part of the verse text or tafsir
        if (query.lower() in text.lower() or 
            query.lower() in tafsir.lower() or
            normalize_arabic(query.lower()) in normalize_arabic(text.lower())):
            
            # Create a preview of the verse
            preview = text[:50] + "..." if len(text) > 50 else text
            suggestions.append({
                'type': 'verse',
                'text': f"{preview} ({verse['surah']}:{verse['ayah']})",
                'value': f"{verse['surah']}:{verse['ayah']}"
            })
    
    # Remove duplicates and limit results
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        key = (suggestion['type'], suggestion['value'])
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(suggestion)
    
    return jsonify(unique_suggestions[:10])

def search_local_verses(query):
    """Search in local verses database with intelligent ranking"""
    results = []
    query_lower = query.lower()
    query_normalized = normalize_arabic(query_lower)
    
    for verse in verses_db:
        score = 0
        text = verse.get('text', '')
        
        # Exact reference match gets highest score
        if query == f"{verse['surah']}:{verse['ayah']}":
            score = 100
        
        # Text matches
        if query_lower in text.lower():
            score += 50
        
        # Normalized Arabic matches
        if query_normalized in normalize_arabic(text.lower()):
            score += 40
        
        # Surah name matches
        if verse['surah'] in SURAH_NAMES:
            surah_names = SURAH_NAMES[verse['surah']]
            if (query_lower in surah_names['ar'].lower() or 
                query_lower in surah_names['en'].lower() or
                normalize_arabic(query_lower) in normalize_arabic(surah_names['ar'].lower())):
                score += 35
        
        # Keyword matches (partial)
        words = query_lower.split()
        for word in words:
            if len(word) > 2:  # Skip very short words
                if word in text.lower():
                    score += 15
                if normalize_arabic(word) in normalize_arabic(text.lower()):
                    score += 12
        
        if score > 0:
            results.append({
                'sura': verse['surah'],
                'aya': verse['ayah'],
                'sura_name_ar': SURAH_NAMES[verse['surah']]['ar'],
                'sura_name_en': SURAH_NAMES[verse['surah']]['en'],
                'text': text,
                'score': score
            })
    
    return results

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 25
    
    if not query:
        return jsonify({
            'results': [],
            'total': 0,
            'page': page,
            'has_next': False,
            'has_prev': False
        })
    
    results = []
    
    # First, search in local verses database
    local_results = search_local_verses(query)
    results.extend(local_results)
    
    # Parse reference for external API search
    sura, aya = parse_reference(query)
    if sura and aya and sura > 1:  # Only search external API for surahs beyond Al-Fatiha
        try:
            api_url = f"https://api.quran.com/api/v4/verses/by_key/{sura}:{aya}?language=ar&tafsir_translations=131"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                verse = data.get('verse', {})
                
                results.append({
                    'sura': sura,
                    'aya': aya,
                    'sura_name_ar': SURAH_NAMES[sura]['ar'],
                    'sura_name_en': SURAH_NAMES[sura]['en'],
                    'text': verse.get('text_uthmani', ''),
                    'score': 100
                })
        except:
            pass
    
    # If no results from local search and reference, try external API text search
    if not results:
        # Search first few suras in external API
        for sura_num in range(2, min(15, 115)):  # Start from 2 since we have Al-Fatiha locally
            try:
                api_url = f"https://api.quran.com/api/v4/chapters/{sura_num}/verses?language=ar&tafsir_translations=131&per_page=10"
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    verses = data.get('verses', [])
                    
                    for verse in verses:
                        text = verse.get('text_uthmani', '')
                        
                        score = 0
                        if query.lower() in text.lower():
                            score += 50
                        if normalize_arabic(query.lower()) in normalize_arabic(text.lower()):
                            score += 40
                        
                        if score > 0:
                            results.append({
                                'sura': sura_num,
                                'aya': verse.get('verse_number', 1),
                                'sura_name_ar': SURAH_NAMES[sura_num]['ar'],
                                'sura_name_en': SURAH_NAMES[sura_num]['en'],
                                'text': text,
                                'score': score
                            })
            except:
                continue
    
    # Sort results by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for result in results:
        key = (result['sura'], result['aya'])
        if key not in seen:
            seen.add(key)
            unique_results.append(result)
    
    # Pagination
    total = len(unique_results)
    start = (page - 1) * per_page
    end = start + per_page
    page_results = unique_results[start:end]
    
    return jsonify({
        'results': page_results,
        'total': total,
        'page': page,
        'has_next': end < total,
        'has_prev': page > 1,
        'query': query
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/surah/<int:surah_id>')
def show_surah(surah_id):
    """Display full Surah with all verses"""
    if surah_id not in SURAH_NAMES:
        return "Surah not found", 404
    
    surah_info = SURAH_NAMES[surah_id]
    
    # Get verses from local database if available
    local_verses = [v for v in verses_db if v['surah'] == surah_id]
    
    if local_verses:
        # Use local data
        verses = local_verses
    else:
        # Fetch from external API
        try:
            api_url = f"https://api.quran.com/api/v4/chapters/{surah_id}/verses?language=ar&per_page=300"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                api_verses = data.get('verses', [])
                verses = []
                for verse in api_verses:
                    verses.append({
                        'surah': surah_id,
                        'ayah': verse.get('verse_number', 1),
                        'text': verse.get('text_uthmani', '')
                    })
            else:
                verses = []
        except:
            verses = []
    
    return render_template('surah.html', 
                         surah_info=surah_info, 
                         verses=verses, 
                         surah_id=surah_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
