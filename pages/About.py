import streamlit as st
import base64
import json
from streamlit_lottie import st_lottie

st.set_page_config(page_title="About TalkHeal", layout="wide")

# --- Asset Loading ---
def get_base64_of_bin_file(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" # Transparent pixel

def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# --- Theming and Styling ---
def set_page_theme_and_style():
    from core.theme import get_current_theme
    current_theme = st.session_state.get("current_theme") or get_current_theme()
    is_dark = current_theme["name"] == "Dark"
    selected_palette = st.session_state.get("palette_name", "Pink")

    palette_map = {
        "light": "static_files/pink.png", "calm blue": "static_files/blue.png",
        "mint": "static_files/mint.png", "lavender": "static_files/lavender.png",
        "pink": "static_files/pink.png"
    }
    background_image_path = "static_files/dark.png" if is_dark else palette_map.get(selected_palette.lower(), "static_files/pink.png")
    encoded_string = get_base64_of_bin_file(background_image_path)

    st.markdown(f'''
        <style>
        /* --- Keyframes for Animations --- */
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

        /* --- Base and Background --- */
        html, body, [data-testid="stApp"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
        }}
        .block-container {{ background-color: transparent; }}
        [data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.6); }}
        [data-testid="stHeader"] {{ background-color: transparent; }}

        /* --- Typography --- */
        h1 {{ color: rgb(214, 51, 108) !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.2); }}
        h2, h3, h4, h5, h6, p, span, strong, div, label {{
            color: {'#f0f0f0' if is_dark else 'rgba(49, 51, 63, 0.8)'} !important;
        }}

        /* --- Custom Components --- */
        .card {{
            background-color: {'rgba(40, 40, 40, 0.7)' if is_dark else 'rgba(255, 255, 255, 0.7)'};
            border-radius: 15px; padding: 25px; text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: transform 0.2s; height: 100%;
            animation: fadeInUp 0.5s ease-out forwards; opacity: 0; /* Initial state for animation */
        }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }}
        .card-icon {{ font-size: 3rem; margin-bottom: 15px; }}
        .card-title {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 10px; }}
        
        /* Staggered animation for cards */
        .st-emotion-cache-r421ms:nth-child(1) .card {{ animation-delay: 0.1s; }}
        .st-emotion-cache-r421ms:nth-child(2) .card {{ animation-delay: 0.2s; }}
        .st-emotion-cache-r421ms:nth-child(3) .card {{ animation-delay: 0.3s; }}
        .st-emotion-cache-r421ms:nth-child(4) .card {{ animation-delay: 0.4s; }}

        .custom-disclaimer {{
            background-color: {'rgba(180, 120, 0, 0.2)' if is_dark else 'rgba(255, 165, 0, 0.15)'};
            border-left: 5px solid #FFA500; border-radius: 5px; padding: 20px; margin: 2rem 0;
        }}

        .footer {{
            text-align: center; margin-top: 40px; color: {'#aaa' if is_dark else 'rgba(49, 51, 63, 0.7)'};
        }}
        .footer a {{ text-decoration: none; color: rgb(214, 51, 108); }}
        </style>
    ''', unsafe_allow_html=True)

# --- Page Layout --- 

set_page_theme_and_style()

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

# --- Header Section ---
intro_col, lottie_col = st.columns([2, 1.5])
with intro_col:
    st.title("About TalkHeal")
    st.markdown("### Your compassionate companion for mental wellness.")
    st.markdown("TalkHeal is a safe space designed to provide a listening ear and helpful resources, available anytime, anywhere. We believe that everyone deserves to be heard and supported on their journey to mental well-being.")

with lottie_col:
    lottie_animation = load_lottiefile("assets/yoga_animation.json")
    if lottie_animation:
        st_lottie(lottie_animation, speed=1, reverse=False, loop=True, quality="high", height=300, width=300)

# --- Core Features Section ---
st.subheader("What We Offer")
features = [
    {"icon": "💬", "title": "24/7 Support", "text": "Get immediate, round-the-clock emotional support whenever you need it."},
    {"icon": "📚", "title": "Resource Guidance", "text": "Access a curated library of articles, exercises, and wellness tools."},
    {"icon": "🆘", "title": "Crisis Intervention", "text": "Find clear, actionable steps and contacts for immediate help in a crisis."},
    {"icon": "🧑‍⚕️", "title": "Professional Referrals", "text": "Receive guidance on connecting with qualified mental health professionals."}
]

feature_cols = st.columns(len(features))
for i, feature in enumerate(features):
    with feature_cols[i]:
        st.markdown(f'''
            <div class="card">
                <div class="card-icon">{feature["icon"]}</div>
                <div class="card-title">{feature["title"]}</div>
                <p>{feature["text"]}</p>
            </div>
        ''', unsafe_allow_html=True)

# --- Disclaimer Section ---
st.markdown("""
    <div class="custom-disclaimer">
        <p><b>Important:</b> TalkHeal is a supportive tool, not a substitute for professional medical advice, diagnosis, or treatment. 
        Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.</p>
    </div>
""", unsafe_allow_html=True)



# --- Footer Section ---
st.markdown('''
    <div class="footer">
        <p>Created with ❤️ by <b><a href="https://eccentriccoder01.github.io/Me" target="_blank">Eccentric Explorer</a></b></p>
        <p><i>"It's absolutely okay not to be okay :)"</i></p>
        <p>Enhanced Version - May 2025</p>
    </div>
''', unsafe_allow_html=True)
