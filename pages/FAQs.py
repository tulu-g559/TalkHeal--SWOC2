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

        /* Header bar: fully transparent */
        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}

        span {{
            color: {'#f0f0f0' if is_dark else 'rgba(49, 51, 63, 0.8)'} !important;
            transition: color 0.3s ease;
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


# Page title
st.markdown("""
    <div style='background-color: #ffe4ef; border-radius: 15px; padding: 2rem; margin-bottom: 2rem;'>
        <h2 style='color: #d6336c; text-align: center;'>Frequently Asked Questions (FAQs)</h2>
    </div>
""", unsafe_allow_html=True)

# FAQ container
st.markdown("""
    <div style='background-color: #fff; border-radius: 10px; box-shadow: 0 2px 8px #d6336c22; padding: 2rem; margin-bottom: 2rem;'>
""", unsafe_allow_html=True)

# Question 1
with st.expander("What is TalkHeal?"):
    st.markdown("""
        <div style='padding: 1rem;'>
            TalkHeal is your trusted companion for mental wellness, designed to empower you on your journey to emotional health. Our platform combines science-backed tools, expert resources, and a supportive community to help you thrive every day.
        </div>
    """, unsafe_allow_html=True)

# Question 2
with st.expander("What are the key features of TalkHeal?"):
    st.markdown("""
        <div style='padding: 1rem;'>
            <b>Key Features include:</b>
            <ul>
                <li><b>Mood Tracking:</b> Visualize your emotional patterns and gain insights to improve your well-being.</li>
                <li><b>Coping Tools:</b> Access quick coping cards, breathing exercises, and journaling to manage stress and anxiety.</li>
                <li><b>Wellness Resource Hub:</b> Explore articles, self-help guides, and connect with specialists for expert advice.</li>
                <li><b>Community Support:</b> Join a safe, inclusive space to share experiences and find encouragement.</li>
                <li><b>Personalized Dashboard:</b> Track your progress and celebrate your achievements.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Question 3
with st.expander("Why should I use TalkHeal?"):
    st.markdown("""
        <div style='padding: 1rem;'>
            TalkHeal is designed with you in mind:
            <ul>
                <li>It has a beautiful, user-friendly design with soothing colors and intuitive navigation.</li>
                <li>It is accessible on all devices—desktop, tablet, and mobile.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Question 4
with st.expander("Is TalkHeal free to use?"):
    st.markdown("""
        <div style='padding: 1rem;'>
            Yes, TalkHeal is free to get started. We also offer premium resources for deeper support.
        </div>
    """, unsafe_allow_html=True)

# Question 5
with st.expander("Is my data secure and private?"):
    st.markdown("""
        <div style='padding: 1rem;'>
            Absolutely. We have a privacy-first approach. Your data is always secure and confidential.
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)