# app.py
import streamlit as st
import pandas as pd
import datetime, os
import plotly.express as px
from processor import *

st.set_page_config(page_title="Omni-Mess AI", layout="wide", page_icon="🍽️")

def apply_ui(meal_type):
    bgs = {"Breakfast": "https://images.unsplash.com/photo-1493770348161-369560ae357d?q=80&w=1600",
           "Lunch": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?q=80&w=1600",
           "Dinner": "https://images.unsplash.com/photo-1515516969-d4008cc6241a?q=80&w=1600"}
    st.markdown(f"""<style>.stApp {{ background: linear-gradient(rgba(15,23,42,0.9),rgba(15,23,42,0.9)), url("{bgs.get(meal_type)}"); background-size: cover; color: #f8fafc; }}
    div[data-testid="stForm"] {{ background: rgba(255,255,255,0.05)!important; backdrop-filter: blur(15px); border-radius: 20px; padding: 25px; border: 1px solid rgba(255,255,255,0.1); }}
    h1, h2, h3 {{ color: #60a5fa!important; }}
    .stButton>button {{ background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; border-radius: 10px; font-weight: bold; width: 100%; }}
    </style>""", unsafe_allow_html=True)

# Database Setup
DB = "mess_data.csv"
COLUMNS = ["ID","Date","Name","Roll_No","Course","Meal_Type","Item","Quantity","Protein","Calories","Waste_Est","Taste_Rating","Hygiene_Rating","Comment","Sentiment","AI_Suggestion"]

if 'db' not in st.session_state:
    st.session_state.db = pd.read_csv(DB) if os.path.exists(DB) else pd.DataFrame(columns=COLUMNS)

# Time Logic
hr = datetime.datetime.now().hour
m_now, col = ("Breakfast", "#fbbf24") if 5<=hr<11 else ("Lunch", "#10b981") if 11<=hr<16 else ("Dinner", "#3b82f6")
apply_ui(m_now)

# Sidebar
pw = st.sidebar.text_input("🔑 Admin Password", type="password")
page = st.sidebar.selectbox("Navigate", ["Student Portal", "Management Analytics"]) if pw == "kartik123" else "Student Portal"
lang = st.sidebar.selectbox("🌐 Language", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[lang]

# --- STUDENT PORTAL ---
if page == "Student Portal":
    st.markdown(f'<div style="border-left: 5px solid {col}; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
                f'<h4 style="margin:0; color:{col};">● LIVE SESSION</h4>'
                f'<h2 style="margin:0;">{m_now} | {datetime.datetime.now().strftime("%I:%M %p")}</h2></div>', unsafe_allow_html=True)

    with st.form("feedback_form", clear_on_submit=True):
        st.subheader(t['student_info'])
        c_i1, c_i2, c_i3 = st.columns(3)
        with c_i1: s_name = st.text_input(t['name'])
        with c_i2: s_roll = st.text_input(t['roll'])
        with c_i3: s_course = st.text_input(t['course'])
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: m_type = st.selectbox("Category", ["Breakfast", "Lunch", "Dinner"], index=["Breakfast", "Lunch", "Dinner"].index(m_now), disabled=True)
        with c2: food_item = st.selectbox("Dish Selection", list(MENU[m_type].keys()))
        
        grams = st.slider(t['quantity'], 100, 600, 250, step=50)
        
        st.write("### Rate Your Experience")
        c3, c4 = st.columns(2)
        star_opts = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}
        
        with c3:
            st.write(f"**{t['taste']}**")
            taste = st.radio("T", [1,2,3,4,5], format_func=lambda x: star_opts[x], horizontal=True, label_visibility="collapsed")
        with c4:
            st.write(f"**{t['hygiene']}**")
            hygiene = st.radio("H", [1,2,3,4,5], format_func=lambda x: star_opts[x], horizontal=True, label_visibility="collapsed")
        
        comment = st.text_area(t['placeholder'])
        
        if st.form_submit_button(t['submit']):
            if comment.strip() and s_name and s_roll:
                with st.spinner("AI Analysis..."):
                    cat, sent = categorize_feedback(comment), analyze_sentiment(comment)
                    macs, waste = get_macros(m_type, food_item, grams), estimate_waste(taste, grams)
                    sugg = get_ai_suggestion(cat, sent, food_item)
                    entry = {"ID": len(st.session_state.db)+1, "Date": datetime.date.today(), "Name": s_name, "Roll_No": s_roll, "Course": s_course, "Meal_Type": m_type, "Item": food_item, "Quantity": grams, "Protein": macs['p'], "Calories": macs['cal'], "Waste_Est": waste, "Taste_Rating": taste, "Hygiene_Rating": hygiene, "Comment": comment, "Sentiment": sent, "AI_Suggestion": sugg}
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([entry])], ignore_index=True)
                    st.session_state.db.to_csv(DB, index=False)
                st.balloons(); st.success(f"Done! {macs['p']}g Protein | {macs['cal']} kcal")
            else: st.warning("Please fill Name, Roll No, and Comment.")

# --- MANAGEMENT ANALYTICS ---
elif page == "Management Analytics":
    st.title("📊 Management & AI Insights")
    df = st.session_state.db
    if not df.empty:
        # 1. Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Logs", len(df))
        m2.metric("Est. Waste (kg)", f"{df['Waste_Est'].sum()/1000:.2f}")
        m3.metric("Avg Hygiene", f"{df['Hygiene_Rating'].mean():.1f}/5")
        
        # 2. Procurement
        waste_pct = (df['Waste_Est'].sum() / df['Quantity'].sum()) * 100
        advice, _ = get_procurement_advice(waste_pct)
        st.info(f"**📉 AI Procurement Advice:** {advice}")

        # 3. Detailed Feed (The Fix)
        st.subheader("📋 Student Feedback Feed")
        for idx, row in df[::-1].iterrows():
            with st.expander(f"Review #{row['ID']} - {row['Name']} ({row['Item']})"):
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.write(f"**Roll No:** {row['Roll_No']}")
                    st.write(f"**Taste:** {'⭐' * int(row['Taste_Rating'])}")
                    st.write(f"**Hygiene:** {'🧼' * int(row['Hygiene_Rating'])}")
                with col_b:
                    st.markdown(f"**Comment:** {row['Comment']}")
                    st.success(f"**AI Action Plan:** {row['AI_Suggestion']}")
        
        # 4. Chart
        st.plotly_chart(px.bar(df, x='Meal_Type', y='Waste_Est', color='Sentiment', barmode='group', template="plotly_dark"), use_container_width=True)
    else: st.info("No data recorded yet.")
