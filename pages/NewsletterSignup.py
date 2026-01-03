import streamlit as st
import re
from datetime import datetime
import base64

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

def newsletter_signup_form():
    """Displays the newsletter signup form and handles submission."""

    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Custom CSS styling
    st.markdown("""
        <style>
            .newsletter-container {
                background-color: var(--secondary-background-color);
                color: var(--text-color);
                padding: 2rem;
                border-radius: 10px;
                margin: 2rem auto;
                max-width: 900px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .newsletter-card {
                background-color: var(--background-color);
                border: 1px solid var(--separator-color);
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: box-shadow 0.3s;
            }
            .newsletter-card:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .tag {
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 15px;
                font-size: 0.8rem;
                margin: 0.25rem;
            }
            .stats-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 10px;
                text-align: center;
                margin: 1rem 0;
            }
            .stats-number {
                font-size: 2.5rem;
                font-weight: bold;
            }
            .share-buttons {
                display: flex;
                gap: 0.5rem;
                margin-top: 1rem;
            }
            .share-btn {
                padding: 0.5rem 1rem;
                border-radius: 5px;
                text-decoration: none;
                color: white;
                font-size: 0.9rem;
                transition: opacity 0.3s;
            }
            .share-btn:hover {
                opacity: 0.8;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='newsletter-container'>", unsafe_allow_html=True)
    
    st.header("💌 Subscribe to Our Weekly Newsletter")
    st.write("Get the latest wellness tips, mental health news, and exclusive content delivered straight to your inbox!")
    
    # Subscriber Statistics
    st.markdown("""
        <div class='stats-box'>
            <div class='stats-number'>5,234+</div>
            <div>Happy Subscribers</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form(key="newsletter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Enter your name", key="newsletter_name")
        
        with col2:
            email = st.text_input("Email Address", placeholder="Enter your email", key="newsletter_email")
        
        st.markdown("### 📬 Subscription Preferences")
        st.write("Choose the topics you're interested in:")
        
        col3, col4 = st.columns(2)
        with col3:
            mental_health = st.checkbox("Mental Health Tips", value=True, key="pref_mental")
            wellness = st.checkbox("Wellness & Lifestyle", value=True, key="pref_wellness")
            mindfulness = st.checkbox("Mindfulness Practices", value=True, key="pref_mindfulness")
        
        with col4:
            nutrition = st.checkbox("Nutrition & Diet", value=False, key="pref_nutrition")
            exercise = st.checkbox("Exercise & Fitness", value=False, key="pref_exercise")
            sleep = st.checkbox("Sleep & Rest", value=False, key="pref_sleep")
        
        st.markdown("### 📅 Frequency")
        frequency = st.radio(
            "How often would you like to receive our newsletter?",
            options=["Weekly (Recommended)", "Bi-weekly", "Monthly"],
            horizontal=True,
            key="newsletter_frequency"
        )
        
        # Privacy consent
        privacy_consent = st.checkbox(
            "I agree to receive newsletters and accept the privacy policy",
            key="privacy_consent"
        )
        
        submit = st.form_submit_button("Subscribe Now 🚀", help="Sign up for our newsletter")
        
        if submit:
            # Validate inputs
            errors = []
            
            if not name or len(name.strip()) < 2:
                errors.append("Please enter a valid name (at least 2 characters)")
            
            if not email or not re.match(EMAIL_REGEX, email):
                errors.append("Please enter a valid email address")
            
            if not privacy_consent:
                errors.append("Please accept the privacy policy to continue")
            
            # Check if at least one preference is selected
            preferences_selected = any([mental_health, wellness, mindfulness, nutrition, exercise, sleep])
            if not preferences_selected:
                errors.append("Please select at least one topic of interest")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Store subscription data in session state
                st.session_state.subscribed = True
                st.session_state.subscriber_name = name
                st.session_state.subscriber_email = email
                st.session_state.subscription_date = datetime.now().strftime("%B %d, %Y")
                st.session_state.preferences = {
                    "Mental Health Tips": mental_health,
                    "Wellness & Lifestyle": wellness,
                    "Mindfulness Practices": mindfulness,
                    "Nutrition & Diet": nutrition,
                    "Exercise & Fitness": exercise,
                    "Sleep & Rest": sleep
                }
                st.session_state.frequency = frequency
                
                st.success(f"🎉 Welcome aboard, {name}! Thank you for subscribing!")
                st.info(f"📧 A confirmation email has been sent to {email}")
                st.balloons()
                st.rerun()
    
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>We respect your privacy and will never share your email. You can unsubscribe at any time.</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def subscription_management():
    """Shows subscription management options for existing subscribers."""
    st.markdown("<div class='newsletter-container'>", unsafe_allow_html=True)
    
    st.header("✅ Subscription Active")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.success(f"Welcome back, {st.session_state.get('subscriber_name', 'Subscriber')}!")
        st.write(f"📧 Email: {st.session_state.get('subscriber_email', 'N/A')}")
        st.write(f"📅 Subscribed since: {st.session_state.get('subscription_date', 'N/A')}")
        st.write(f"🔔 Frequency: {st.session_state.get('frequency', 'Weekly')}")
        
        if st.session_state.get('preferences'):
            st.write("### Your Topics:")
            active_prefs = [topic for topic, active in st.session_state.preferences.items() if active]
            for pref in active_prefs:
                st.markdown(f"<span class='tag'>{pref}</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Actions")
        if st.button("📝 Update Preferences", use_container_width=True):
            st.session_state.update_preferences = True
            st.rerun()
        
        if st.button("🔕 Unsubscribe", use_container_width=True, type="secondary"):
            st.session_state.show_unsubscribe = True
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show unsubscribe confirmation
    if st.session_state.get('show_unsubscribe', False):
        with st.expander("⚠️ Unsubscribe Confirmation", expanded=True):
            st.warning("Are you sure you want to unsubscribe? You'll miss out on valuable content!")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("Yes, Unsubscribe"):
                    # Clear subscription data
                    st.session_state.subscribed = False
                    st.session_state.show_unsubscribe = False
                    for key in ['subscriber_name', 'subscriber_email', 'subscription_date', 'preferences', 'frequency']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.success("You've been unsubscribed. We're sorry to see you go!")
                    st.rerun()
            
            with col2:
                if st.button("No, Keep Subscription"):
                    st.session_state.show_unsubscribe = False
                    st.rerun()
    
    # Show preference update form
    if st.session_state.get('update_preferences', False):
        st.markdown("---")
        st.subheader("📝 Update Your Preferences")
        
        with st.form("update_preferences_form"):
            st.markdown("### Topics")
            col1, col2 = st.columns(2)
            
            current_prefs = st.session_state.get('preferences', {})
            
            with col1:
                mental_health = st.checkbox("Mental Health Tips", value=current_prefs.get("Mental Health Tips", True))
                wellness = st.checkbox("Wellness & Lifestyle", value=current_prefs.get("Wellness & Lifestyle", True))
                mindfulness = st.checkbox("Mindfulness Practices", value=current_prefs.get("Mindfulness Practices", True))
            
            with col2:
                nutrition = st.checkbox("Nutrition & Diet", value=current_prefs.get("Nutrition & Diet", False))
                exercise = st.checkbox("Exercise & Fitness", value=current_prefs.get("Exercise & Fitness", False))
                sleep = st.checkbox("Sleep & Rest", value=current_prefs.get("Sleep & Rest", False))
            
            st.markdown("### Frequency")
            frequency = st.radio(
                "How often would you like to receive our newsletter?",
                options=["Weekly (Recommended)", "Bi-weekly", "Monthly"],
                index=["Weekly (Recommended)", "Bi-weekly", "Monthly"].index(st.session_state.get('frequency', 'Weekly (Recommended)'))
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    st.session_state.preferences = {
                        "Mental Health Tips": mental_health,
                        "Wellness & Lifestyle": wellness,
                        "Mindfulness Practices": mindfulness,
                        "Nutrition & Diet": nutrition,
                        "Exercise & Fitness": exercise,
                        "Sleep & Rest": sleep
                    }
                    st.session_state.frequency = frequency
                    st.session_state.update_preferences = False
                    st.success("✅ Preferences updated successfully!")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.update_preferences = False
                    st.rerun()


def show():
    """Renders the Newsletter Signup page."""
    st.title("Newsletter Signup")
    
    # Initialize session state
        .newsletter-container {
            text-align: center;
            padding: 2rem 1rem;
            background: linear-gradient(135deg, #fceff9 0%, #ffffff 100%);
            border-radius: 18px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }

        .newsletter-container h1 {
            color: #d63384;
            font-family: 'Baloo 2', cursive;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .newsletter-container p {
            color: #333;
            font-size: 1.1rem;
            font-style: italic;
        }

        .newsletter-card {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s;
        }

        .newsletter-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Container for the header and form
    with st.container():
        st.markdown("""
            <div class="newsletter-container">
                <h1>💌 Subscribe to Our Weekly Newsletter</h1>
                <p>Get the latest wellness tips, mental health news, and exclusive content delivered to your inbox!</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form(key="newsletter_form", clear_on_submit=True):
            email = st.text_input("Email Address", placeholder="Enter your email")
            submit = st.form_submit_button("Subscribe")

            if submit:
                if email and re.match(EMAIL_REGEX, email):
                    st.success("✅ Thank you for subscribing! You'll receive our next newsletter soon.")
                    st.balloons()
                    st.session_state.subscribed = True
                else:
                    st.error("⚠️ Please enter a valid email address.")

        # st.markdown("<p style='text-align: center; color: #888; font-size: 0.9rem;'>We respect your privacy and will never share your email.</p>", unsafe_allow_html=True)
        st.info("🔒 We respect your privacy and will never share your email.")

def show():
    """Renders the Newsletter Signup page."""
    # st.title("📰 Newsletter Signup")

    # Session state check
    if 'subscribed' not in st.session_state:
        st.session_state.subscribed = False

    # Show appropriate content based on subscription status
    if st.session_state.subscribed:
        subscription_management()
    else:
        newsletter_signup_form()

    st.markdown("---")
    
    # Search and Filter Section
    st.subheader("📖 Past Newsletters Archive")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search newsletters", placeholder="Search by title or content...", label_visibility="collapsed")
    with col2:
        category_filter = st.selectbox("Category", ["All", "Mental Health", "Wellness", "Mindfulness", "Nutrition", "Sleep"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Most Popular"])
        st.success("🎉 You are already subscribed! Thank you for being a part of our community.")
        st.markdown("---")
        st.page_link("app.py", label="Back to Home", icon="🏠")
    else:
        newsletter_signup_form()

    st.divider()
    st.subheader("📖 Past Newsletters")

    past_newsletters = [
        {
            "title": "Mindful Mondays: The Power of Breath",
            "date": "October 6, 2025",
            "category": "Mindfulness",
            "summary": "This week, we explore the power of mindful breathing and how it can help you stay calm and centered throughout the day. We also share a simple breathing exercise that you can do anywhere, anytime.",
            "content": "Breathing is something we do unconsciously, but when we bring awareness to our breath, it becomes a powerful tool for managing stress and anxiety. In this newsletter, we dive deep into breathing techniques including box breathing, 4-7-8 breathing, and alternate nostril breathing. Each technique serves different purposes and can be used in various situations throughout your day.",
            "tags": ["Breathing", "Stress Relief", "Mindfulness"],
            "read_time": "5 min read",
            "views": 1248
        },
        {
            "title": "Wellness Wednesdays: The Importance of Sleep",
            "date": "September 29, 2025",
            "category": "Sleep",
            "summary": "In this issue, we dive into the science of sleep and why it's so crucial for your mental and physical health. We also provide some tips for getting a better night's sleep.",
            "content": "Sleep is not just rest - it's an active process where your body repairs itself, consolidates memories, and regulates hormones. We explore the sleep cycles, the importance of REM sleep, and how chronic sleep deprivation affects your mental health. You'll learn about sleep hygiene, optimal bedroom conditions, and natural ways to improve sleep quality without medication.",
            "tags": ["Sleep", "Health", "Recovery"],
            "read_time": "7 min read",
            "views": 2156
        },
        {
            "title": "Feel-Good Fridays: The Benefits of Gratitude",
            "date": "September 22, 2025",
            "category": "Mental Health",
            "summary": "This week, we focus on the power of gratitude and how it can improve your mood and overall well-being. We also share a simple gratitude journaling exercise.",
            "content": "Scientific research shows that practicing gratitude can rewire your brain for happiness. We explore the neuroscience behind gratitude, share compelling research studies, and provide practical exercises you can start today. Learn about the 3 Good Things exercise, gratitude letters, and how to build a sustainable gratitude practice that fits your lifestyle.",
            "tags": ["Gratitude", "Happiness", "Mental Health"],
            "read_time": "6 min read",
            "views": 1876
        },
        {
            "title": "Nutrition Notes: Foods That Boost Your Mood",
            "date": "September 15, 2025",
            "category": "Nutrition",
            "summary": "Discover the surprising connection between what you eat and how you feel. We explore mood-boosting foods and the gut-brain connection.",
            "content": "Your gut produces 90% of your body's serotonin! Learn about the gut-brain axis and how the foods you eat directly impact your mental health. We cover omega-3 fatty acids, probiotics, complex carbohydrates, and foods rich in B vitamins. Plus, get easy recipes for mood-boosting smoothies and snacks.",
            "tags": ["Nutrition", "Mental Health", "Recipes"],
            "read_time": "8 min read",
            "views": 1543
        },
        {
            "title": "Movement Matters: Exercise for Mental Clarity",
            "date": "September 8, 2025",
            "category": "Wellness",
            "summary": "Learn how different types of exercise affect your mental health and cognitive function. From yoga to HIIT, find what works for you.",
            "content": "Exercise isn't just for physical health - it's a powerful tool for mental wellness. We break down the mental health benefits of different exercise types: yoga for stress reduction, cardio for mood elevation, strength training for confidence, and walking for creativity. Includes a 7-day movement challenge!",
            "tags": ["Exercise", "Mental Health", "Fitness"],
            "read_time": "6 min read",
            "views": 1392
        },
        {
            "title": "Stress Less: Managing Modern Life Pressures",
            "date": "September 1, 2025",
            "category": "Mental Health",
            "summary": "Practical strategies for managing stress in our fast-paced world. Learn techniques that actually work backed by science.",
            "content": "Stress is inevitable, but chronic stress is harmful. We explore the physiology of stress, how to recognize your stress triggers, and evidence-based techniques for stress management including progressive muscle relaxation, time-blocking, and setting healthy boundaries. Real-life case studies included.",
            "tags": ["Stress", "Coping Skills", "Mental Health"],
            "read_time": "9 min read",
            "views": 2401
        }
    ]

    # Filter newsletters
    filtered_newsletters = past_newsletters
    
    if search_query:
        filtered_newsletters = [
            n for n in filtered_newsletters 
            if search_query.lower() in n['title'].lower() 
            or search_query.lower() in n['summary'].lower()
            or search_query.lower() in n['content'].lower()
        ]
    
    if category_filter != "All":
        filtered_newsletters = [n for n in filtered_newsletters if n['category'] == category_filter]
    
    # Sort newsletters
    if sort_by == "Newest First":
        filtered_newsletters.sort(key=lambda x: x['date'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_newsletters.sort(key=lambda x: x['date'])
    elif sort_by == "Most Popular":
        filtered_newsletters.sort(key=lambda x: x['views'], reverse=True)

    # Show results count
    st.markdown(f"*Showing {len(filtered_newsletters)} of {len(past_newsletters)} newsletters*")

    if not filtered_newsletters:
        st.info("No newsletters found matching your search criteria. Try different keywords!")
    else:
        cols = st.columns(2)
        for i, newsletter in enumerate(filtered_newsletters):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"""
                        <div class="newsletter-card">
                            <h4>{newsletter['title']}</h4>
                            <p><em>{newsletter['date']}</em> • {newsletter['read_time']} • 👁️ {newsletter['views']} views</p>
                    """, unsafe_allow_html=True)
                    
                    # Category badge
                    st.markdown(f"<span class='tag'>{newsletter['category']}</span>", unsafe_allow_html=True)
                    
                    # Tags
                    for tag in newsletter['tags']:
                        st.markdown(f"<span class='tag' style='background-color: #666;'>{tag}</span>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p style='margin-top: 1rem;'>{newsletter['summary']}</p>", unsafe_allow_html=True)
                    
                    # Expander for full content
                    with st.expander("📖 Read More"):
                        st.write(newsletter['content'])
                        
                        # Share buttons
                        st.markdown("### Share this newsletter")
                        share_col1, share_col2, share_col3, share_col4 = st.columns(4)
                        
                        with share_col1:
                            if st.button("🐦 Twitter", key=f"twitter_{i}", use_container_width=True):
                                st.info("Share link copied!")
                        with share_col2:
                            if st.button("📘 Facebook", key=f"facebook_{i}", use_container_width=True):
                                st.info("Share link copied!")
                        with share_col3:
                            if st.button("💼 LinkedIn", key=f"linkedin_{i}", use_container_width=True):
                                st.info("Share link copied!")
                        with share_col4:
                            if st.button("📧 Email", key=f"email_{i}", use_container_width=True):
                                st.info("Email template ready!")
                    
                    st.markdown("</div>", unsafe_allow_html=True)

    # Footer with helpful links
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #888;'>
            <h4>Need Help?</h4>
            <p>
                <a href='#' style='color: #667eea; text-decoration: none; margin: 0 1rem;'>Contact Us</a> • 
                <a href='#' style='color: #667eea; text-decoration: none; margin: 0 1rem;'>Privacy Policy</a> • 
                <a href='#' style='color: #667eea; text-decoration: none; margin: 0 1rem;'>FAQ</a>
            </p>
            <p style='font-size: 0.9rem; margin-top: 1rem;'>
                © 2025 Mental Health Newsletter. All rights reserved.
            </p>
        </div>
    """, unsafe_allow_html=True)

# To run the page
if __name__ == "__main__":
    show()