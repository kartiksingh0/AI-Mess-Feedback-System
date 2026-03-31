# processor.py
from transformers import pipeline

# --- 1. GLOBAL TRANSLATION ENGINE (31 Languages) ---
TRANSLATIONS = {
    "English": {"title": "Smart Mess Scanner", "quantity": "Quantity (Grams)", "taste": "Taste Quality", "hygiene": "Hygiene Rating", "submit": "Analyze & Submit", "placeholder": "How was the meal?", "sentiment": "AI Sentiment", "category": "Category"},
    "Hindi (हिन्दी)": {"title": "स्मार्ट मेस स्कैनर", "quantity": "मात्रा (ग्राम)", "taste": "स्वाद की गुणवत्ता", "hygiene": "स्वच्छতা रेटिंग", "submit": "विश्लेषण और जमा करें", "placeholder": "खाना कैसा था?", "sentiment": "AI भावना", "category": "श्रेणी"},
    "Bengali (বাংলা)": {"title": "স্মার্ট মেস স্ক্যানার", "quantity": "পরিমাণ (গ্রাম)", "taste": "স্বাদ", "hygiene": "পরিচ্ছন্নতা", "submit": "জমা দিন", "placeholder": "খাবার কেমন ছিল?", "sentiment": "AI অনুভূতি", "category": "বিভাগ"},
    "Telugu (తెలుగు)": {"title": "స్మార్ట్ మెస్ స్కానర్", "quantity": "పరిమాణం (గ్రాములు)", "taste": "రుచి", "hygiene": "పరిశుభ్రత", "submit": "సమర్పించు", "placeholder": "భోజనం ఎలా ఉంది?", "sentiment": "AI సెంటిమెంట్", "category": "వర్గం"},
    "Marathi (मराठी)": {"title": "स्मार्ट मेस स्कॅनर", "quantity": "प्रमाण (ग्रॅम)", "taste": "चव", "hygiene": "स्वच्छता", "submit": "सादर करा", "placeholder": "जेवण कसे होते?", "sentiment": "AI भावना", "category": "श्रेणी"},
    "Tamil (தமிழ்)": {"title": "ஸ்மார்ட் மெஸ் ஸ்கேனர்", "quantity": "அளவு (கிராம்)", "taste": "சுவை", "hygiene": "சுகாதாரம்", "submit": "சமர்ப்பிக்கவும்", "placeholder": "உணவு எப்படி இருந்தது?", "sentiment": "AI உணர்வு", "category": "வகை"},
    "Gujarati (ગુજરાતી)": {"title": "સ્માર્ટ મેસ સ્કેનર", "quantity": "જથ્થો (ગ્રામ)", "taste": "સ્વાદ", "hygiene": "સ્વચ્છતા", "submit": "સબમિટ કરો", "placeholder": "જમવાનું કેવું હતું?", "sentiment": "AI લાગણી", "category": "શ્રેણી"},
    "Kannada (ಕನ್ನಡ)": {"title": "ಸ್ಮಾರ್ಟ್ ಮೆస్ ಸ್ಕ್ಯಾನರ್", "quantity": "ಪ್ರಮಾಣ (ಗ್ರಾಂ)", "taste": "ರುಚಿ", "hygiene": "ನೈರ್ಮಲ್ಯ", "submit": "ಸಲ್ಲಿಸು", "placeholder": "ಊಟ ಹೇಗಿತ್ತು?", "sentiment": "AI ಭಾವನೆ", "category": "ವರ್ಗ"},
    "Malayalam (മലയാളം)": {"title": "സ്മാർട്ട് മെസ് സ്കാനർ", "quantity": "അളവ് (ഗ്രാം)", "taste": "രുചി", "hygiene": "ശുചിത്വം", "submit": "സമർപ്പിക്കുക", "placeholder": "ഭക്ഷണം എങ്ങനെയുണ്ടായിരുന്നു?", "sentiment": "AI വികാരം", "category": "വിഭാഗം"},
    "Punjabi (ਪੰਜਾਬੀ)": {"title": "ਸਮਾਰਟ ਮੈਸ ਸਕੈਨਰ", "quantity": "ਮਾਤਰਾ (ਗ੍ਰਾਮ)", "taste": "ਸੁਆਦ", "hygiene": "ਸਫਾਈ", "submit": "ਭੇਜੋ", "placeholder": "ਖਾਣਾ ਕਿਵੇਂ ਸੀ?", "sentiment": "AI ਭਾਵਨਾ", "category": "ਸ਼੍ਰੇਣੀ"},
    "Odia (ଓଡ଼ିଆ)": {"title": "ସ୍ମାର୍ଟ ମେସ୍ ସ୍କାନର୍", "quantity": "ପରିମାଣ (ଗ୍ରାମ)", "taste": "ସ୍ୱାଦ", "hygiene": "ସ୍ୱଚ୍ଛତା", "submit": "ଦାଖଲ କରନ୍ତୁ", "placeholder": "ଖାଦ୍ୟ କିପରି ଥିଲା?", "sentiment": "AI ମନୋଭାବ", "category": "ଶ୍ରେଣୀ"},
    "Urdu (اردو)": {"title": "اسمارٹ میس اسکینر", "quantity": "مقدار (گرام)", "taste": "ذائقہ", "hygiene": "صفائی", "submit": "جمع کرائیں", "placeholder": "کھانا کیسا تھا؟", "sentiment": "AI تاثرات", "category": "زمرہ"},
    "Spanish (Español)": {"title": "Escáner de Comedor", "quantity": "Cantidad (Gramos)", "taste": "Sabor", "hygiene": "Higiene", "submit": "Enviar", "placeholder": "¿Cómo estuvo la comida?", "sentiment": "Sentimiento AI", "category": "Categoría"},
    "French (Français)": {"title": "Scanner de Mess", "quantity": "Quantité (Grammes)", "taste": "Goût", "hygiene": "Hygiène", "submit": "Envoyer", "placeholder": "Comment était le repas?", "sentiment": "Sentiment IA", "category": "Catégorie"},
    "German (Deutsch)": {"title": "Mess-Scanner", "quantity": "Menge (Gramm)", "taste": "Geschmack", "hygiene": "Hygiene", "submit": "Absenden", "placeholder": "Wie war das Essen?", "sentiment": "KI-Stimmung", "category": "Kategorie"},
    "Chinese (中文)": {"title": "智能食堂扫描仪", "quantity": "数量 (克)", "taste": "味道", "hygiene": "卫生", "submit": "提交", "placeholder": "餐点怎么样？", "sentiment": "AI 情感", "category": "类别"},
    "Japanese (日本語)": {"title": "スマート食堂スキャナー", "quantity": "数量 (グラム)", "taste": "味", "hygiene": "衛生", "submit": "送信", "placeholder": "食事はどうでしたか？", "sentiment": "AI 感情分析", "category": "カテゴリー"},
    "Korean (한국어)": {"title": "스마트 식당 스캐너", "quantity": "수량 (그램)", "taste": "맛", "hygiene": "위생", "submit": "제출", "placeholder": "식사는 어땠나요?", "sentiment": "AI 감정", "category": "카테고리"},
    "Arabic (العربية)": {"title": "ماسح الوجبات الذكي", "quantity": "الكمية (جرام)", "taste": "الطعم", "hygiene": "النظافة", "submit": "إرسال", "placeholder": "كيف كانت الوجبة؟", "sentiment": "مشاعر الذكاء الاصطناعي", "category": "الفئة"},
    "Russian (Русский)": {"title": "Умный сканер столовой", "quantity": "Количество (граммы)", "taste": "Вкус", "hygiene": "Гигиена", "submit": "Отправить", "placeholder": "Как вам еда?", "sentiment": "AI Настроение", "category": "Категория"},
    "Portuguese (Português)": {"title": "Scanner de Refeitório", "quantity": "Quantidade (Gramas)", "taste": "Sabor", "hygiene": "Higiene", "submit": "Enviar", "placeholder": "Como estava a comida?", "sentiment": "Sentimento IA", "category": "Categoria"},
    "Italian (Italiano)": {"title": "Scanner Mensa", "quantity": "Quantità (Grammi)", "taste": "Gusto", "hygiene": "Igiene", "submit": "Invia", "placeholder": "Com'era il pasto?", "sentiment": "Sentimento IA", "category": "Categoria"},
    "Turkish (Türkçe)": {"title": "Akıllı Yemekhane Tarayıcı", "quantity": "Miktar (Gram)", "taste": "Lezzet", "hygiene": "Hijyen", "submit": "Gönder", "placeholder": "Yemek nasıldı?", "sentiment": "AI Duygu", "category": "Kategori"},
    "Vietnamese (Tiếng Việt)": {"title": "Máy quét nhà ăn thông minh", "quantity": "Số lượng (Gram)", "taste": "Hương vị", "hygiene": "Vệ sinh", "submit": "Gửi", "placeholder": "Bữa ăn thế nào?", "sentiment": "Cảm xúc AI", "category": "Danh mục"},
    "Thai (ไทย)": {"title": "เครื่องสแกนโรงอาหารอัจฉริยะ", "quantity": "ปริมาณ (กรัม)", "taste": "รสชาติ", "hygiene": "สุขอนามัย", "submit": "ส่ง", "placeholder": "อาหารเป็นอย่างไรบ้าง?", "sentiment": "ความรู้สึก AI", "category": "หมวดหมู่"},
    "Dutch (Nederlands)": {"title": "Mensa Scanner", "quantity": "Hoeveelheid (Gram)", "taste": "Smaak", "hygiene": "Hygiëne", "submit": "Verzenden", "placeholder": "Hoe was de maaltijd?", "sentiment": "AI Sentiment", "category": "Categorie"},
    "Greek (Ελληνικά)": {"title": "Έξυπνος Σαρωτής Λέσχης", "quantity": "Ποσότητα (Γραμμάρια)", "taste": "Γεύση", "hygiene": "Υγιεινή", "submit": "Υποβολή", "placeholder": "Πώς ήταν το γεύμα;", "sentiment": "AI Συναίσθημα", "category": "Κατηγορία"},
    "Indonesian (Bahasa)": {"title": "Pemindai Kantin Pintar", "quantity": "Jumlah (Gram)", "taste": "Rasa", "hygiene": "Kebersihan", "submit": "Kirim", "placeholder": "Bagaimana makanannya?", "sentiment": "Sentimen AI", "category": "Kategori"},
    "Polish (Polski)": {"title": "Inteligentny Skaner Stołówki", "quantity": "Ilość (Gramy)", "taste": "Smak", "hygiene": "Higiena", "submit": "Wyślij", "placeholder": "Jak smakował posiłek?", "sentiment": "Sentyment AI", "category": "Kategoria"},
    "Ukrainian (Українська)": {"title": "Розумний сканер їдальні", "quantity": "Кількість (грами)", "taste": "Смак", "hygiene": "Гігієна", "submit": "Надіслати", "placeholder": "Як вам страва?", "sentiment": "AI Настрій", "category": "Категорія"},
    "Hebrew (עברית)": {"title": "סורק חדר אוכל חכם", "quantity": "כמות (גרם)", "taste": "טעם", "hygiene": "היגיינה", "submit": "שלח", "placeholder": "איך הייתה הארוחה?", "sentiment": "AI סנטימנט", "category": "קטגוריה"}
}

# --- 2. NUTRITION ENGINE DATA (Per 100g) ---
NUTRITION_DATA = {
    "Breakfast: Poha": {"p": 2.5, "f": 8.0, "c": 25.0, "cal": 180},
    "Lunch: Thali": {"p": 15.0, "f": 12.0, "c": 60.0, "cal": 450},
    "Dinner: Paneer": {"p": 14.0, "f": 18.0, "c": 12.0, "cal": 280},
    "South Indian: Dosa": {"p": 4.0, "f": 10.0, "c": 40.0, "cal": 300},
    "Special: Biryani": {"p": 12.0, "f": 15.0, "c": 45.0, "cal": 400},
    "Other/General": {"p": 5.0, "f": 5.0, "c": 20.0, "cal": 150}
}

def get_macros(item, grams):
    base = NUTRITION_DATA.get(item, NUTRITION_DATA["Other/General"])
    factor = grams / 100
    return {
        "p": round(base["p"] * factor, 1),
        "f": round(base["f"] * factor, 1),
        "c": round(base["c"] * factor, 1),
        "cal": int(base["cal"] * factor)
    }

# --- 3. ANALYTICS: WASTE ESTIMATION ---
def estimate_waste(taste_rating, quantity):
    if taste_rating <= 2: factor = 0.45
    elif taste_rating == 3: factor = 0.15
    else: factor = 0.05
    return round(quantity * factor, 1)

# --- 4. AI SUGGESTION ENGINE ---
def get_ai_suggestion(category, sentiment, item):
    suggestions = {
        "Food Quality": {
            "NEGATIVE": f"Standardize the recipe for {item}. Check spice levels and cooking time.",
            "POSITIVE": f"Maintain the current prep method for {item}; it is highly appreciated."
        },
        "Hygiene": {
            "NEGATIVE": "CRITICAL: Schedule an immediate deep clean and audit staff glove usage.",
            "POSITIVE": "Hygiene standards are met. Continue weekly sanitization audits."
        },
        "Quantity": {
            "NEGATIVE": f"Review serving portions for {item}. Students feel it is insufficient.",
            "POSITIVE": "Portion sizes are currently optimal for student needs."
        },
        "Staff Service": {
            "NEGATIVE": "Conduct soft-skills training for the counter staff on shift.",
            "POSITIVE": "Acknowledge the mess staff for their excellent service."
        }
    }
    return suggestions.get(category, {}).get(sentiment, "Continue monitoring feedback for trends.")

# --- 5. AI BRAINS: SENTIMENT & CATEGORIZATION ---
print("Initializing Global AI Models...")
sentiment_task = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def analyze_sentiment(text):
    if not text.strip(): return "NEUTRAL"
    result = sentiment_task(text)[0]
    return result['label']

def categorize_feedback(text):
    if not text.strip(): return "General"
    candidate_labels = ["Food Quality", "Hygiene", "Quantity", "Staff Service"]
    result = classifier(text, candidate_labels)
    return result['labels'][0]