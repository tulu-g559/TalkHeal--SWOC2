import streamlit as st
import sqlite3
import base64
from uuid import uuid4
from datetime import date
from core.utils import require_authentication
import pandas as pd
import altair as alt
import csv
from io import StringIO
from fpdf import FPDF
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import random



def get_base64_of_bin_file(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background_for_theme(selected_palette="pink"):
    from core.theme import get_current_theme

    # --- Get current theme info ---
    current_theme = st.session_state.get("current_theme", None)
    if not current_theme:
        current_theme = get_current_theme()
    
    is_dark = current_theme["name"] == "Dark"

    # --- Map light themes to background images ---
    palette_color = {
        "light": "static_files/pink.png",
        "calm blue": "static_files/blue.png",
        "mint": "static_files/mint.png",
        "lavender": "static_files/lavender.png",
        "pink": "static_files/pink.png"
    }

    # --- Select background based on theme ---
    if is_dark:
        background_image_path = "static_files/dark.png"
    else:
        background_image_path = palette_color.get(selected_palette.lower(), "static_files/pink.png")

    encoded_string = get_base64_of_bin_file(background_image_path)
    st.markdown(
        f"""
        <style>
        /* Entire app background */
        html, body, [data-testid="stApp"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Main content transparency */
        .block-container {{
            background-color: rgba(255, 255, 255, 0);
        }}

        /* Sidebar: brighter translucent background */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.6);  /* Brighter and translucent */
            color: {'black' if is_dark else 'rgba(49, 51, 63, 0.8)'} ;  /* Adjusted for light background */
        }}

        span {{
            color: {'#f0f0f0' if is_dark else 'rgba(49, 51, 63, 0.8)'} !important;
            transition: color 0.3s ease;
        }}

        /* Header bar: fully transparent */
        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}

        /* Hide left/right arrow at sidebar bottom */
        button[title="Close sidebar"],
        button[title="Open sidebar"] {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Set your background image
selected_palette = st.session_state.get("palette_name", "Pink")
set_background_for_theme(selected_palette)

import streamlit.components.v1 as components
components.html(r"""
<script>
(function() {
    var targetWindow = window.parent !== window ? window.parent : window;
    var targetDoc = targetWindow.document;
    
    if (targetWindow.__cursorTrailInit) return;
    targetWindow.__cursorTrailInit = true;
    
    var trail = [];
    var mx = 0, my = 0;
    var len = 12;
    var animationId = null;
    var lastTime = 0;
    var fps = 60;
    var frameInterval = 1000 / fps;
    
    function createTrail() {
        if (!targetDoc.body) {
            setTimeout(createTrail, 100);
            return;
        }
        
        targetDoc.querySelectorAll('.ct-heart').forEach(function(el) { el.remove(); });
        trail = [];
        
        for (var i = 0; i < len; i++) {
            var d = targetDoc.createElement('div');
            var symbol = '💕';
            var color = '#ff69b4';
            d.className = 'ct-heart';
            d.textContent = symbol;
            d.style.cssText = 'position:fixed;pointer-events:none;z-index:999999;font-size:' + (12 + i * 0.5) + 'px;color:' + color + ';text-shadow:0 0 8px ' + color + ',0 0 16px ' + color + ';opacity:' + ((len-i)/len * 0.8) + ';left:0;top:0;transform:translate(-50%,-50%) rotate(' + (i * 18) + 'deg);transition:opacity 0.2s;';
            targetDoc.body.appendChild(d);
            trail.push({el:d, x:targetWindow.innerWidth/2, y:targetWindow.innerHeight/2, rot:i*18});
        }
        
        targetWindow.addEventListener('mousemove', function(e) {
            mx = e.clientX;
            my = e.clientY;
        });
        
        function animate(currentTime) {
            if (currentTime - lastTime < frameInterval) {
                animationId = requestAnimationFrame(animate);
                return;
            }
            lastTime = currentTime;
            
            for (var i = 0; i < trail.length; i++) {
                var next = trail[i+1] || {x:mx, y:my};
                trail[i].x += (next.x - trail[i].x) * 0.25;
                trail[i].y += (next.y - trail[i].y) * 0.25;
                trail[i].rot += 1.5;
                
                var transform = 'translate(-50%,-50%) rotate(' + trail[i].rot + 'deg) scale(' + (0.6 + i/len * 0.4) + ')';
                trail[i].el.style.left = trail[i].x + 'px';
                trail[i].el.style.top = trail[i].y + 'px';
                trail[i].el.style.transform = transform;
            }
            animationId = requestAnimationFrame(animate);
        }
        animate();
    }
    
    if (targetDoc.readyState === "complete") createTrail();
    else targetWindow.addEventListener("load", createTrail);
    
    setTimeout(createTrail, 500);
})();
</script>
""", height=0, width=0)

# Centralized Authentication Check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
    
require_authentication()

def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(main_bg_path, sidebar_bg_path=None):
    main_bg = get_base64_of_bin_file(main_bg_path)
    sidebar_bg = get_base64_of_bin_file(sidebar_bg_path) if sidebar_bg_path else main_bg
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{main_bg}");
            background-size: cover;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-right: 2px solid rgba(245, 167, 208, 0.6);
            box-shadow: 4px 0 24px rgba(0,0,0,0.15);
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/png;base64,{sidebar_bg}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def analyze_sentiment(entry: str) -> str:
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(entry)['compound']
    if sentiment_score >= 0.05:
        return "Positive"
    elif sentiment_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

DB_PATH = "journals.db"

def init_journal_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id TEXT PRIMARY KEY,
            email TEXT,
            entry TEXT,
            sentiment TEXT,
            date TEXT,
            tags TEXT
        )
        """)
        conn.commit()

def save_entry(email, entry, sentiment, tags):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO journal_entries (id, email, entry, sentiment, date, tags)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid4()), email, entry, sentiment, str(date.today()), tags))
        conn.commit()

def fetch_entries(email, sentiment_filter=None, start_date=None, end_date=None, tag_filter=None, search_query=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, entry, sentiment, date, tags FROM journal_entries
            WHERE email = ?
        """
        params = [email]
        if sentiment_filter and sentiment_filter != "All":
            query += " AND sentiment = ?"
            params.append(sentiment_filter)
        if start_date and end_date:
            query += " AND date BETWEEN ? AND ?"
            params.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
        if tag_filter:
            for tag in tag_filter:
                query += f" AND tags LIKE '%{tag}%'"
        if search_query:
            query += f" AND (entry LIKE '%{search_query}%' OR tags LIKE '%{search_query}%')"

        query += " ORDER BY date ASC"
        rows = cursor.execute(query, params).fetchall()
    return rows

def update_entry(entry_id, new_text, new_tags):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        new_sentiment = analyze_sentiment(new_text)
        cursor.execute("UPDATE journal_entries SET entry = ?, sentiment = ?, tags = ? WHERE id = ?", (new_text, new_sentiment, new_tags, entry_id))
        conn.commit()

def delete_entry(entry_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
        conn.commit()

def create_mood_trend_chart(entries):
    if not entries:
        return None

    df = pd.DataFrame(entries, columns=['id', 'entry', 'sentiment', 'date', 'tags'])
    df['date'] = pd.to_datetime(df['date'])
    
    sentiment_mapping = {"Positive": 1, "Neutral": 0, "Negative": -1}
    df['sentiment_score'] = df['sentiment'].map(sentiment_mapping)

    chart = alt.Chart(df).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('sentiment_score:Q', title='Mood Score'),
        tooltip=['date', 'sentiment', 'tags']
    ).properties(
        title="Mood Trend Over Time"
    ).interactive()

    return chart

def get_csv_export(entries):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Sentiment', 'Entry', 'Tags'])
    for _, entry, sentiment, entry_date, tags in entries:
        writer.writerow([entry_date, sentiment, entry, tags])
    return output.getvalue()

def get_pdf_export(entries):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for _, entry, sentiment, entry_date, tags in entries:
        pdf.cell(200, 10, txt=f"Date: {entry_date}", ln=True)
        pdf.cell(200, 10, txt=f"Sentiment: {sentiment}", ln=True)
        pdf.cell(200, 10, txt=f"Tags: {tags}", ln=True)
        pdf.multi_cell(0, 10, txt=entry)
        pdf.ln(10)
    return pdf.output(dest='S').encode('latin-1')

def journaling_app():
    set_background_for_theme(selected_palette)
    st.markdown(
        """
        <style>
        /* CSS styles for the app */
        textarea.stTextArea > div > textarea { color: white !important; background-color: #222222 !important; }
        button[aria-expanded] { color: white !important; }
        .streamlit-expanderContent p, .streamlit-expanderContent div { color: white !important; }
        .stTextArea, .css-1d391kg, .stMarkdown, .css-1v0mbdj { color: white !important; }
        textarea::placeholder { color: #ccc !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📝 My Journal")
    st.markdown("Write about your day, thoughts, or anything you'd like to reflect on.")
    email = st.session_state.user_profile.get("email")

    # Journaling Prompts Feature
    journal_prompts = [
        "What are you grateful for today?",
        "What's one thing you want to remember from today?",
        "Describe a challenge you faced today and how you handled it.",
        "What's on your mind right now?",
        "Write about something that made you smile today.",
        "What is one thing you can do to make tomorrow better?",
        "Describe a recent dream you had.",
        "What are your goals for the upcoming week?",
        "Write about a person who has had a positive impact on your life.",
        "What is a skill you would like to learn and why?"
    ]

    if 'current_prompt' not in st.session_state:
        st.session_state.current_prompt = "How are you feeling today?"

    if st.button("Get a Journaling Prompt"):
        st.session_state.current_prompt = random.choice(journal_prompts)
        st.rerun()

    with st.form("journal_form"):
        journal_text = st.text_area(st.session_state.current_prompt, height=200)
        tags = st.text_input("Tags (comma-separated)")
        submitted = st.form_submit_button("Submit Entry")

    if submitted and journal_text.strip():
        sentiment = analyze_sentiment(journal_text)
        save_entry(email, journal_text, sentiment, tags)
        st.success(f"Entry saved! Sentiment: **{sentiment}**")
        st.rerun() 

    st.markdown("---")
    st.subheader("Mood Dashboard")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("End Date", value=date.today())

    all_entries = fetch_entries(email, start_date=start_date, end_date=end_date)
    all_tags = list(set(",".join([entry[4] for entry in all_entries if entry[4]]).split(',')))

    tag_filter = st.multiselect("Filter by Tags", all_tags)
    search_query = st.text_input("Search Entries")

    entries = fetch_entries(email, start_date=start_date, end_date=end_date, tag_filter=tag_filter, search_query=search_query)

    chart = create_mood_trend_chart(entries)
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Not enough data to display mood trend. Write some journal entries first!")


    st.markdown("---")
    st.subheader("📖 Your Journal Entries")

    filter_sentiment = st.selectbox("Filter by Sentiment", ["All", "Positive", "Neutral", "Negative"])
    
    filtered_entries = entries
    if filter_sentiment != "All":
        filtered_entries = [entry for entry in entries if entry[2] == filter_sentiment]

    if not filtered_entries:
        st.info("No entries found for selected filters.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            csv_data = get_csv_export(filtered_entries)
            st.download_button(
                label="Export as CSV",
                data=csv_data,
                file_name="journal_entries.csv",
                mime="text/csv",
            )
        with col2:
            pdf_data = get_pdf_export(filtered_entries)
            st.download_button(
                label="Export as PDF",
                data=pdf_data,
                file_name="journal_entries.pdf",
                mime="application/pdf",
            )

        for entry_id, entry, sentiment, entry_date, tags in reversed(filtered_entries):
            with st.expander(f"{entry_date} - Mood: {sentiment} - Tags: {tags}"):
                st.write(entry)
                
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Edit", key=f"edit_{entry_id}"):
                        st.session_state.edit_id = entry_id
                with col2:
                    if st.button("Delete", key=f"delete_{entry_id}"):
                        delete_entry(entry_id)
                        st.rerun()

                if st.session_state.get("edit_id") == entry_id:
                    with st.form(key=f"edit_form_{entry_id}"):
                        new_text = st.text_area("Edit your entry", value=entry, height=200)
                        new_tags = st.text_input("Tags (comma-separated)", value=tags)
                        if st.form_submit_button("Save"):
                            update_entry(entry_id, new_text, new_tags)
                            st.session_state.edit_id = None
                            st.rerun()

init_journal_db()
journaling_app()