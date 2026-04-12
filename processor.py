# processor.py
from transformers import pipeline

# --- 1. TRANSLATION ENGINE ---
TRANSLATIONS = {
    "English": {
        "title": "Omni-Mess AI Scanner", 
        "student_info": "Student Identification",
        "name": "Full Name",
        "roll": "Roll Number",
        "course": "Course / Semester",
        "quantity": "Quantity (Grams)", 
        "taste": "Food Taste Quality", 
        "hygiene": "Hygiene & Cleanliness", 
        "submit": "Analyze & Submit Feedback", 
        "placeholder": "Tell us about the food quality, hygiene, or quantity..."
    },
    "Hindi (हिन्दी)": {
        "title": "ओम्नी-मेस AI स्कैनर", 
        "student_info": "छात्र की जानकारी",
        "name": "पूरा नाम",
        "roll": "रोल नंबर",
        "course": "कोर्स / सेमेस्टर",
        "quantity": "मात्रा (ग्राम)", 
        "taste": "स्वाद की गुणवत्ता", 
        "hygiene": "स्वच्छता रेटिंग", 
        "submit": "जमा करें", 
        "placeholder": "खाना कैसा था? अपनी राय लिखें..."
    }
}

# --- 2. MENU & NUTRITION DATA ---
MENU = {
    "Breakfast": {
        "Poha & Jalebi": {"p": 3.0, "cal": 220},
        "Aloo Paratha (2pc)": {"p": 6.0, "cal": 310},
        "Idli-Sambar": {"p": 7.0, "cal": 250},
        "Tea & Biscuits": {"p": 1.0, "cal": 110}
    },
    "Lunch": {
        "Standard Thali": {"p": 15.0, "cal": 550},
        "Rajma Chawal": {"p": 12.0, "cal": 480},
        "Veg Biryani": {"p": 10.0, "cal": 420},
        "Curd Rice": {"p": 4.0, "cal": 190}
    },
    "Dinner": {
        "Paneer Butter Masala": {"p": 14.0, "cal": 380},
        "Dal Tadka & Roti": {"p": 18.0, "cal": 410},
        "Egg Curry & Rice": {"p": 20.0, "cal": 450},
        "Mixed Veg & Chapati": {"p": 8.0, "cal": 280}
    }
}

def get_macros(meal_type, item, grams):
    category = MENU.get(meal_type, MENU["Breakfast"])
    base = category.get(item, {"p": 5, "cal": 150})
    factor = grams / 100
    return {"p": round(base["p"] * factor, 1), "cal": int(base["cal"] * factor)}

def estimate_waste(rating, quantity):
    if rating <= 2: factor = 0.40
    elif rating == 3: factor = 0.15
    else: factor = 0.05
    return round(quantity * factor, 1)

def get_procurement_advice(avg_waste_pct):
    if avg_waste_pct > 20: return "CRITICAL: High waste. Reduce next procurement by 15%.", 15
    elif avg_waste_pct > 10: return "MODERATE: Reduce procurement by 8% to optimize costs.", 8
    return "OPTIMAL: Minimal waste. Maintain levels.", 0

def get_ai_suggestion(category, sentiment, item):
    suggestions = {
        "Food Quality": {"NEGATIVE": f"Review {item} prep. Adjust spice/salt levels.", "POSITIVE": f"{item} quality is optimal."},
        "Hygiene": {"NEGATIVE": "Urgent kitchen audit needed.", "POSITIVE": "Sanitization standards met."},
        "Quantity": {"NEGATIVE": f"Portion sizes for {item} are insufficient.", "POSITIVE": "Quantity is adequate."}
    }
    return suggestions.get(category, {}).get(sentiment, "Monitor daily feedback trends.")

# --- 3. AI MODELS ---
print("Loading Models...")
sentiment_task = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def analyze_sentiment(text):
    if not text.strip(): return "NEUTRAL"
    return sentiment_task(text)[0]['label']

def categorize_feedback(text):
    if not text.strip(): return "General"
    t_lower = text.lower()
    # Hybrid Keyword Overrides
    if any(w in t_lower for w in ["taste", "salt", "spicy", "bad", "tasty", "delicious", "yummy"]): return "Food Quality"
    if any(w in t_lower for w in ["clean", "dirty", "hygiene", "insect", "hair", "plate", "wash"]): return "Hygiene"
    if any(w in t_lower for w in ["quantity", "less", "portion", "enough", "fill"]): return "Quantity"
    # AI Fallback
    res = classifier(text, ["Food Quality", "Hygiene", "Quantity", "Staff Service"])
    return res['labels'][0]
