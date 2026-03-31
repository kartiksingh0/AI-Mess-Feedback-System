import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from processor import (
    categorize_feedback, 
    analyze_sentiment, 
    get_macros, 
    estimate_waste, 
    get_ai_suggestion,
    NUTRITION_DATA, 
    TRANSLATIONS
)

# --- 1. PAGE CONFIG & GLOBAL STYLING ---
st.set_page_config(page_title="Omni-Mess AI", layout="wide", page_icon="🍽️")

def apply_advanced_ui(item_bg):
    bg_images = {
        "Breakfast: Poha": "https://images.unsplash.com/photo-1626132647523-66f5bf380027?q=80&w=1600",
        "Lunch: Thali": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?q=80&w=1600",
        "Dinner: Paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?q=80&w=1600",
        "South Indian: Dosa": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?q=80&w=1600",
        "Special: Biryani": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?q=80&w=1600",
        "Other/General": "https://images.unsplash.com/photo-1490812945881-3353c1ac1f73?q=80&w=1600"
    }
    selected_bg = bg_images.get(item_bg, bg_images["Other/General"])

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url("{selected_bg}");
        background-size: cover; background-position: center; background-attachment: fixed;
        color: #f8fafc; transition: 0.5s ease;
    }}
    div[data-testid="stForm"], div.stExpander {{
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px); border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px;
    }}
    h1, h2, h3 {{ color: #60a5fa !important; }}
    .stButton>button {{
        width: 100%; background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white; border-radius: 12px; border: none; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA STORAGE ---
if 'feedback_db' not in st.session_state:
    st.session_state.feedback_db = pd.DataFrame(columns=[
        "ID", "Date", "Category", "Item", "Quantity", "Protein", "Fats", "Carbs", "Calories", 
        "Waste_Est", "Taste_Rating", "Hygiene_Rating", "Comment", "Sentiment", "Status", "AI_Suggestion"
    ])

# --- 3. SIDEBAR ---
st.sidebar.markdown("# 🛡️ Control Center")
selected_lang = st.sidebar.selectbox("🌐 Select Language", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang]

page = st.sidebar.selectbox("Navigate to:", ["Student Feedback Portal", "Management Analytics", "⚙️ Menu Settings"])

temp_item = "Other/General"
if page == "Student Feedback Portal":
    temp_item = st.sidebar.selectbox("Preview Background", list(NUTRITION_DATA.keys()))

apply_advanced_ui(temp_item)

# --- 4. STUDENT FEEDBACK PORTAL ---
if page == "Student Feedback Portal":
    st.markdown(f"<h1 style='text-align: center;'>{t['title']}</h1>", unsafe_allow_html=True)

    input_mode = st.radio("Input Method:", ["Manual Selection", "AI Camera Scanner"])
    if input_mode == "AI Camera Scanner":
        st.camera_input("Verify Meal")

    with st.form("feedback_form", clear_on_submit=True):
        grams = st.slider(t['quantity'], 100, 600, 250, step=50)
        c1, c2 = st.columns(2)
        with c1: taste = st.select_slider(t['taste'], options=[1, 2, 3, 4, 5], value=3)
        with c2: hygiene = st.select_slider(t['hygiene'], options=[1, 2, 3, 4, 5], value=3)
        comment = st.text_area(t['placeholder'])
        
        if st.form_submit_button(t['submit']):
            if comment.strip():
                with st.spinner("AI Analysis in progress..."):
                    cat = categorize_feedback(comment)
                    sent = analyze_sentiment(comment)
                    macs = get_macros(temp_item, grams)
                    waste = estimate_waste(taste, grams)
                    sugg = get_ai_suggestion(cat, sent, temp_item) # AI Suggestion Logic
                    
                    new_data = {
                        "ID": len(st.session_state.feedback_db) + 1,
                        "Date": datetime.date.today(), "Category": cat, "Item": temp_item, 
                        "Quantity": grams, "Protein": macs['p'], "Fats": macs['f'], 
                        "Carbs": macs['c'], "Calories": macs['cal'], "Waste_Est": waste, 
                        "Taste_Rating": taste, "Hygiene_Rating": hygiene, "Comment": comment, 
                        "Sentiment": sent, "Status": "Pending", "AI_Suggestion": sugg
                    }
                    st.session_state.feedback_db = pd.concat([st.session_state.feedback_db, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"✅ {t['submit']} Successful!")
            else:
                st.warning("Please enter feedback.")

# --- 5. MANAGEMENT ANALYTICS ---
elif page == "Management Analytics":
    st.markdown("<h1>📊 Management Control Center</h1>", unsafe_allow_html=True)
    df = st.session_state.feedback_db

    if df.empty:
        st.info("Waiting for feedback data...")
    else:
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Reviews", len(df))
        m2.metric("Total Waste", f"{df['Waste_Est'].sum()/1000:.1f} kg")
        m3.metric("Avg Protein", f"{df['Protein'].mean():.1f}g")

        # Visuals
        st.plotly_chart(px.bar(df, x='Item', y='Waste_Est', color='Sentiment', title='Waste vs Sentiment'), use_container_width=True)

        # Actionable AI Insights
        st.subheader("🛠️ AI Action Plan")
        for idx, row in df.iterrows():
            with st.expander(f"Case #{row['ID']} - {row['Item']} ({row['Category']})"):
                st.write(f"**Student Feedback:** {row['Comment']}")
                st.info(f"💡 **AI Suggestion:** {row['AI_Suggestion']}")
                status = st.selectbox("Update Status", ["Pending", "Resolved"], key=f"s_{idx}")
                if st.button("Update Case", key=f"b_{idx}"):
                    st.session_state.feedback_db.at[idx, 'Status'] = status
                    st.rerun()

# --- 6. SETTINGS ---
else:
    st.title("⚙️ System Settings")
    st.table(pd.DataFrame(NUTRITION_DATA).T)
    csv = st.session_state.feedback_db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Report (CSV)", data=csv, file_name="mess_ai_report.csv", mime="text/csv")