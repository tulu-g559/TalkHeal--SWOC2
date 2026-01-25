import streamlit as st
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

# Add cursor trail effect with hearts only
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


def show():
    # Page title
    st.markdown("""
        <div style='background: linear-gradient(135deg, #ffe4f0 0%, #fff 100%); border-radius: 18px; box-shadow: 0 2px 18px 0 rgba(209,74,122,0.12); padding: 2.5rem; margin: 2rem auto; max-width: 900px; text-align: center;'>
            <h1 style='color: #d14a7a; font-family: "Baloo 2", cursive;'>Help Center</h1>
            <p style='font-size: 1.1rem;'>Your guide to getting the most out of TalkHeal. We're here for you!</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Add some space

    # --- Getting Started ---
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
            #### Welcome to TalkHeal!
            Here’s a quick guide to help you get started on your wellness journey:
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                **1. Explore Your Dashboard**
                <br>Your main screen shows you key features like Yoga, Journaling, and more. Click any card to begin an activity.
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                **2. Navigate with the Sidebar**
                <br>Use the sidebar on the left to switch between conversations, start new chats, or review your pinned messages.
            """, unsafe_allow_html=True)
        st.markdown("""
            **3. Chat with Your AI Companion**
            <br>Simply type your thoughts into the chat box at the bottom of the main page to start a conversation. The AI is here to listen without judgment.
        """, unsafe_allow_html=True)


    # --- Account & Privacy ---
    with st.expander("👤 Account & Privacy"):
        st.success("Your privacy is our top priority.")
        st.markdown("""
            - **Logging Out:** To log out, simply click the "Logout" button at the top right of the main page.
            - **Data Privacy:** We take your privacy very seriously. Your conversations are confidential and are not shared. For more details, please read our **[Privacy Policy](/PrivacyPolicy)**.
        """)

    # --- AI Companion ---
    with st.expander("🧠 AI Companion"):
        st.info("You can change your AI's personality to best suit your needs.")
        st.markdown("""
            - **Changing Tones:** On the main page, you'll find an expander labeled "Customize Your AI Companion." You can select from several personalities, such as "Compassionate Listener," "Motivating Coach," and more.
            - **Effective Conversations:** Be open and share what's on your mind. The more context you provide, the better the AI can support you. You can use it for advice, to vent, or even for creative brainstorming.
        """)

    # --- Wellness Tools ---
    with st.expander("🛠️ Wellness Tools"):
        st.markdown("TalkHeal offers a variety of tools to support your mental well-being. Click to explore:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link("pages/Yoga.py", label="🧘‍♀️ Yoga & Meditation")
            st.page_link("pages/Breathing_Exercise.py", label="🌬️ Breathing Exercises")
        with col2:
            st.page_link("pages/Journaling.py", label="📝 Personal Journaling")
            st.page_link("pages/selfHelpTools.py", label="🛠️ Self-Help Tools")
        with col3:
            st.page_link("pages/WellnessResourceHub.py", label="🌿 Wellness Hub")
            st.page_link("pages/Habit_Builder.py", label="🎯 Habit Builder")


    # --- "Still Need Help?" Section ---
    st.write("---")
    st.markdown("""
        <div style='background-color: #fff0f6; border-radius: 15px; padding: 2rem; margin-top: 2rem; text-align: center;'>
            <h3 style='color: #d14a7a;'>Still Need Help?</h3>
            <p>If you can't find the answer you're looking for, we're here to assist.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Contact Support**")
        st.write("For any technical issues or questions, please email us directly.")
        st.markdown("[📧 Email support@talkheal.com](mailto:support@talkheal.com)")
    with col2:
        st.info("**Provide Feedback**")
        st.write("Have a suggestion or found a bug? We'd love to hear from you!")
        st.markdown("[🐞 Report an issue on GitHub](https://github.com/eccentriccoder01/TalkHeal/issues)")

    st.markdown("</div>", unsafe_allow_html=True)


show()
