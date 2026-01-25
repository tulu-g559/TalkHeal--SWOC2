import streamlit as st
import base64
import random
import datetime

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

        h2, h3, span {{
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
    """Renders a more visually appealing Community page using tabs and icons."""

    st.markdown("""
    <style>
    /* General container style */
    .main-container {
        padding: 1rem;
    }
    /* Forum style */
    .community-forum {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #ffe4f0 0%, #fff 100%);
        border-radius: 18px;
        margin-bottom: 2rem;
    }
    .community-forum h1 {
        color: rgb(214, 51, 108);
        font-family: 'Baloo 2', cursive;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .community-forum p {
        color: #333;
        font-size: 1.2rem;
        font-style: italic;
    }
    /* Custom list style with icons */
    .icon-list-item {
        display: flex;
        align-items: center;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding: 0.75rem;
        background-color: #f8f9fa;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #31333F; /* Set text color for dark mode visibility */
    }
    .icon-list-item span {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
          
    </style>
    """, unsafe_allow_html=True)

    

    with st.container():
        # --- Header Section --- 
        st.markdown("""
        <div class="community-forum">
            <h1>🌐Community Forum</h1>
            <p>Welcome! Connect, share, and support each other in a safe, AI-moderated environment.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    show()

# --- Helper Functions ---

# List of fun anonymous names
ANONYMOUS_NAMES = [
    "Creative Cat", "Brave Bear", "Wise Wolf", "Gentle Giraffe", "Happy Hippo",
    "Curious Crow", "Daring Dolphin", "Kind Koala", "Lucky Llama", "Patient Panda"
]

# Simple profanity filter (for demonstration)
BANNED_WORDS = ["badword1", "badword2", "example_profanity"]

def initialize_state():
    """Initializes session state variables."""
    if 'posts' not in st.session_state:
        st.session_state.posts = []
    if 'user_name' not in st.session_state:
        st.session_state.user_name = random.choice(ANONYMOUS_NAMES)

def format_time_ago(dt):
    """Formats a datetime object into a 'time ago' string."""
    now = datetime.datetime.now(datetime.timezone.utc)
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)} minute(s) ago"
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)} hour(s) ago"
    days = hours / 24
    return f"{int(days)} day(s) ago"

def contains_profanity(message):
    """Checks if a message contains any banned words."""
    return any(word in message.lower() for word in BANNED_WORDS)

# --- UI Rendering ---

def show_post_form():
    """Displays the form for creating a new post."""
    with st.form("new_post_form", clear_on_submit=True):
        st.subheader(f"Post as: {st.session_state.user_name}")
        message = st.text_area("Share your thoughts or ask for support:", height=150, max_chars=1000)
        submitted = st.form_submit_button("Post Anonymously")
        
        if submitted:
            if not message.strip():
                st.warning("Please enter a message before posting.")
            elif contains_profanity(message):
                st.error("Your message contains inappropriate language and was blocked by our AI moderator.")
            else:
                new_post = {
                    "id": len(st.session_state.posts) + 1,
                    "author": st.session_state.user_name,
                    "message": message,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc),
                    "replies": []
                }
                st.session_state.posts.insert(0, new_post) # Add to the beginning of the list
                st.success("Your message has been posted anonymously!")
                st.rerun()

def show_posts():
    """Displays all the posts and their replies."""
    if not st.session_state.posts:
        st.info("No posts yet. Be the first to share your story!")
        return

    for post in st.session_state.posts:
        with st.container(border=True):
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**{post['author']}** · *{format_time_ago(post['timestamp'])}*")
                st.markdown(post['message'])
            
            # Display replies
            for reply in post['replies']:
                with st.chat_message("user", avatar="💬"):
                     st.markdown(f"**{reply['author']}** · *{format_time_ago(reply['timestamp'])}*")
                     st.markdown(reply['message'])

            # Reply form
            with st.expander("Add a reply..."):
                reply_message = st.text_area("Your reply", key=f"reply_{post['id']}")
                if st.button("Submit Reply", key=f"submit_reply_{post['id']}"):
                    if reply_message.strip():
                        new_reply = {
                            "author": st.session_state.user_name,
                            "message": reply_message,
                            "timestamp": datetime.datetime.now(datetime.timezone.utc)
                        }
                        post['replies'].append(new_reply)
                        st.rerun()

# --- Main Page --- 

initialize_state()

with st.expander("📘 Forum Guidelines"):
    st.markdown("""
    - **Be Kind & Respectful:** Treat everyone with respect. No personal attacks.
    - **Stay Anonymous:** Do not share personal identifying information.
    - **Offer Support:** Provide constructive and supportive feedback.
    - **Safety First:** Do not post content that is graphic or promotes self-harm. Our AI moderator is here to help.
    """)

st.markdown("--- ")

# --- Layout: Two Columns ---
col1, col2 = st.columns([2, 1]) # 2/3 for posts, 1/3 for form

with col1:
    st.header("Recent Posts")
    show_posts()

with col2:
    st.header("Create a Post")
    show_post_form()

st.markdown("---")
st.info("This is a prototype. Posts are cleared when you close the browser tab.")


