import sqlite3
import streamlit as st
import hashlib
from datetime import datetime, timedelta, timezone
import requests
import re
import json
import os
import google.generativeai


def get_current_time():
    """
    Returns the user's local time formatted as HH:MM AM/PM.
    Uses Streamlit's timezone offset if available.
    """
    tz_offset = st.context.timezone_offset

    if tz_offset is None:
        now = datetime.now()
    else:
        now_utc = datetime.now(timezone.utc)
        now = now_utc + timedelta(minutes=-tz_offset)

    return now.strftime("%I:%M %p").lstrip("0")


def get_current_date():
    """
    Returns the user's local date formatted as 'Month Day, Year'.
    Uses Streamlit's timezone offset if available.
    """
    tz_offset = st.context.timezone_offset
    
    if tz_offset is None:
        now = datetime.now()
    else:
        now_utc = datetime.now(timezone.utc)
        now = now_utc + timedelta(minutes=-tz_offset)
    
    return now.strftime("%B %d, %Y")


def hash_email(email):
    """
    Hash email to a short hex digest for privacy and consistent user identification.
    Args:
        email (str): The user's email address.
    Returns:
        str: Shortened SHA-256 hex digest or None if email is empty.
    """
    if not email:
        return None
    return hashlib.sha256(email.encode()).hexdigest()[:10]


def hash_password(password):
    """
    Hash password using SHA-256 for secure storage.
    Args:
        password (str): The user's password.
    Returns:
        str: Full SHA-256 hex digest.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(stored_hash, provided_password):
    """
    Verify if provided password matches stored hash.
    Args:
        stored_hash (str): The stored password hash.
        provided_password (str): The password to verify.
    Returns:
        bool: True if passwords match, False otherwise.
    """
    return stored_hash == hash_password(provided_password)


def create_new_conversation(initial_message=None):
    """
    Create a new conversation for the current user or IP.
    Optionally adds an initial user message.
    Args:
        initial_message (str, optional): The first message in the conversation.
    Returns:
        int: The new conversation ID.
    """
    user_email = st.session_state.get("user_profile", {}).get("email", None)
    ip = cached_user_ip()

    user_key = user_email if user_email else ip

    user_convos = [c for c in st.session_state.conversations if c.get("user_key") == user_key]

    new_id = len(user_convos) + 1

    new_convo = {
        "id": new_id,
        "user_key": user_key,
        "title": initial_message[:30] + "..." if initial_message and len(initial_message) > 30 else "New Conversation",
        "date": datetime.now().strftime("%B %d, %Y"),
        "messages": []
    }

    if initial_message:
        new_convo["messages"].append({
            "sender": "user",
            "message": initial_message,
            "time": get_current_time()
        })

    st.session_state.conversations.insert(0, new_convo)
    st.session_state.active_conversation = new_id
    return new_id


def get_conversation_by_id(convo_id):
    """
    Get a specific conversation by its ID.
    Args:
        convo_id (int): The conversation ID.
    Returns:
        dict or None: The conversation dict if found, None otherwise.
    """
    for convo in st.session_state.conversations:
        if convo.get("id") == convo_id:
            return convo
    return None


def delete_conversation(convo_id):
    """
    Delete a conversation by its ID.
    Args:
        convo_id (int): The conversation ID to delete.
    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    user_email = st.session_state.get("user_profile", {}).get("email", None)
    ip = cached_user_ip()
    user_key = user_email if user_email else ip
    
    initial_count = len(st.session_state.conversations)
    st.session_state.conversations = [
        c for c in st.session_state.conversations 
        if not (c.get("id") == convo_id and c.get("user_key") == user_key)
    ]
    
    if len(st.session_state.conversations) < initial_count:
        save_conversations(st.session_state.conversations)
        if st.session_state.get("active_conversation") == convo_id:
            st.session_state.active_conversation = None
        return True
    return False


def update_conversation_title(convo_id, new_title):
    """
    Update the title of a conversation.
    Args:
        convo_id (int): The conversation ID.
        new_title (str): The new title.
    Returns:
        bool: True if updated successfully, False otherwise.
    """
    convo = get_conversation_by_id(convo_id)
    if convo:
        convo["title"] = new_title
        save_conversations(st.session_state.conversations)
        return True
    return False


def export_conversation(convo_id, format_type="json"):
    """
    Export a conversation in specified format.
    Args:
        convo_id (int): The conversation ID.
        format_type (str): Export format - 'json', 'txt', or 'md'.
    Returns:
        str: Formatted conversation data.
    """
    convo = get_conversation_by_id(convo_id)
    if not convo:
        return None
    
    if format_type == "json":
        return json.dumps(convo, indent=2)
    
    elif format_type == "txt":
        output = f"Conversation: {convo['title']}\n"
        output += f"Date: {convo['date']}\n"
        output += "=" * 50 + "\n\n"
        for msg in convo.get("messages", []):
            sender = msg.get("sender", "unknown").upper()
            time = msg.get("time", "")
            message = msg.get("message", "")
            output += f"[{time}] {sender}: {message}\n\n"
        return output
    
    elif format_type == "md":
        output = f"# {convo['title']}\n\n"
        output += f"**Date:** {convo['date']}\n\n"
        output += "---\n\n"
        for msg in convo.get("messages", []):
            sender = msg.get("sender", "unknown").capitalize()
            time = msg.get("time", "")
            message = msg.get("message", "")
            output += f"### {sender} - {time}\n\n{message}\n\n"
        return output
    
    return None


def clean_ai_response(response_text):
    """
    Clean AI response by removing HTML tags and extra whitespace.
    Args:
        response_text (str): The raw AI response.
    Returns:
        str: Cleaned response text.
    """
    if not response_text:
        return response_text
    response_text = re.sub(r'<[^>]+>', '', response_text)
    response_text = re.sub(r'\s+', ' ', response_text).strip()
    response_text = response_text.replace('&nbsp;', ' ')
    response_text = response_text.replace('&lt;', '<')
    response_text = response_text.replace('&gt;', '>')
    response_text = response_text.replace('&amp;', '&')
    return response_text


def sanitize_input(user_input, max_length=5000):
    """
    Sanitize user input to prevent injection attacks and limit length.
    Args:
        user_input (str): Raw user input.
        max_length (int): Maximum allowed length.
    Returns:
        str: Sanitized input.
    """
    if not user_input:
        return ""
    
    # Remove potential script tags
    user_input = re.sub(r'<script[^>]*>.*?</script>', '', user_input, flags=re.IGNORECASE | re.DOTALL)
    
    # Limit length
    user_input = user_input[:max_length]
    
    # Strip leading/trailing whitespace
    user_input = user_input.strip()
    
    return user_input


def get_ai_response(user_message, model):
    """
    Generate an AI response to the user's message using the provided model.
    Handles errors and ensures a supportive, plain-text reply.
    Args:
        user_message (str): The user's message.
        model: The AI model instance.
    Returns:
        str: The AI's response.
    """
    if model is None:
        return "I'm sorry, I can't connect right now. Please check the API configuration."

    mental_health_prompt = f"""
    You are a compassionate mental health support chatbot named TalkHeal. Your role is to:
    1. Provide empathetic, supportive responses
    2. Encourage professional help when needed
    3. Never diagnose or provide medical advice
    4. Be warm, understanding, and non-judgmental
    5. Ask follow-up questions to better understand the user's situation
    6. Provide coping strategies and resources when appropriate
    7. Not assume that the user is always in overwhelming states. Sometimes he/she might also be in joyful or curious moods and ask questions not related to mental health
    
    IMPORTANT: Respond with PLAIN TEXT ONLY. Do not include any HTML tags, markdown formatting, or special characters. Just provide a natural, conversational response.
    
    User message: {user_message}
    
    Respond in a caring, supportive manner (keep response under 150 words):
    """
    try:
        response = model.generate_content(mental_health_prompt)
        cleaned_response = clean_ai_response(response.text)
        return cleaned_response
    except ValueError:
        return "I'm having trouble understanding your message. Could you please rephrase it?"
    except google.generativeai.types.BlockedPromptException:
        return "I understand you're going through something difficult. Let's focus on how you're feeling and what might help you feel better."
    except google.generativeai.types.GenerationException:
        return "I'm having trouble generating a response right now. Please try again in a moment."
    except requests.RequestException:
        return "I'm having trouble connecting to my services. Please check your internet connection and try again."
    except Exception:
        return "I'm here to listen and support you. Sometimes I have trouble connecting, but I want you to know that your feelings are valid and you're not alone. Would you like to share more about what you're experiencing?"


def get_conversation_summary(convo_id, model=None):
    """
    Generate a brief summary of a conversation using AI.
    Args:
        convo_id (int): The conversation ID.
        model: The AI model instance (optional).
    Returns:
        str: A brief summary or the first message.
    """
    convo = get_conversation_by_id(convo_id)
    if not convo or not convo.get("messages"):
        return "Empty conversation"
    
    messages = convo.get("messages", [])
    if len(messages) <= 2:
        first_msg = messages[0].get("message", "")
        return first_msg[:50] + "..." if len(first_msg) > 50 else first_msg
    
    if model:
        try:
            message_text = "\n".join([f"{m['sender']}: {m['message']}" for m in messages[:5]])
            prompt = f"Summarize this conversation in 5-7 words:\n{message_text}"
            response = model.generate_content(prompt)
            return clean_ai_response(response.text)[:50]
        except:
            pass
    
    # Fallback to first message
    first_msg = messages[0].get("message", "")
    return first_msg[:50] + "..." if len(first_msg) > 50 else first_msg


def cached_user_ip():
    """
    Get the user's IP address, caching it in session state for 1 hour.
    Returns:
        str: The user's IP address or a fallback session ID.
    """
    if hasattr(st.session_state, 'cached_ip') and hasattr(st.session_state, 'ip_cache_time'):
        cache_age = datetime.now() - st.session_state.ip_cache_time
        if cache_age < timedelta(hours=1):
            return st.session_state.cached_ip
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        ip = response.text.strip()
        st.session_state.cached_ip = ip
        st.session_state.ip_cache_time = datetime.now()
        return ip
    except (requests.RequestException, requests.Timeout, Exception):
        fallback_id = f"session_{hash(str(st.session_state)) % 100000}"
        if not hasattr(st.session_state, 'cached_ip'):
            st.session_state.cached_ip = fallback_id
            st.session_state.ip_cache_time = datetime.now()
        return st.session_state.cached_ip


def get_user_ip():
    """
    Get the user's public IP address (no caching).
    Returns:
        str: The user's IP address or 'unknown_ip'.
    """
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "unknown_ip"


def get_memory_file():
    """
    Get the filename for storing conversation history, based on user email or IP.
    Returns:
        str: The path to the memory file.
    """
    user_email = st.session_state.get("user_profile", {}).get("email")
    if user_email:
        safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
        filename = f"data/conversations_{safe_email}.json"
    else:
        ip = cached_user_ip()
        filename = f"data/conversations_{ip}.json"
    os.makedirs("data", exist_ok=True)
    return filename


def save_conversations(conversations):
    """
    Save the list of conversations to the user's memory file.
    Args:
        conversations (list): List of conversation dicts.
    """
    memory_file = get_memory_file()
    with open(memory_file, 'w', encoding="utf-8") as f:
        json.dump(conversations, f, indent=4)


def load_conversations():
    """
    Load the user's conversation history from file.
    Returns:
        list: List of conversation dicts, or empty list if none exist.
    """
    memory_file = get_memory_file()
    if not os.path.exists(memory_file):
        return []
    with open(memory_file, 'r', encoding="utf-8") as f:
        return json.load(f)


def backup_conversations():
    """
    Create a backup of current conversations with timestamp.
    Returns:
        str: Path to backup file, or None if backup failed.
    """
    try:
        memory_file = get_memory_file()
        if not os.path.exists(memory_file):
            return None
        
        backup_dir = "data/backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_email = st.session_state.get("user_profile", {}).get("email")
        if user_email:
            safe_email = user_email.replace("@", "_at_").replace(".", "_dot_")
            backup_file = f"{backup_dir}/backup_{safe_email}_{timestamp}.json"
        else:
            ip = cached_user_ip()
            backup_file = f"{backup_dir}/backup_{ip}_{timestamp}.json"
        
        with open(memory_file, 'r', encoding="utf-8") as src:
            data = json.load(src)
        
        with open(backup_file, 'w', encoding="utf-8") as dst:
            json.dump(data, dst, indent=4)
        
        return backup_file
    except Exception as e:
        print(f"[backup_conversations] Failed to backup: {e}")
        return None


def save_feedback(convo_id, message, feedback, comment=None):
    """
    Save user feedback for a specific message in a conversation.
    Args:
        convo_id (int): Conversation ID.
        message (str): The message being rated.
        feedback (str): The feedback value.
        comment (str, optional): Optional user comment.
    """
    user_email = st.session_state.get("user_profile", {}).get("email")
    hashed_email = hash_email(user_email) if user_email else "unknown"

    print(f"""
    [save_feedback]
    User: {hashed_email}
    Convo ID: {convo_id}
    Message: {message}
    Feedback: {feedback}
    Comment: {comment if comment else "No comment"}
    """)

    try:
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()

            c.execute('''
                SELECT id FROM feedback WHERE user_email = ? AND convo_id = ? AND message = ?
            ''', (hashed_email, convo_id, message))
            row = c.fetchone()

            if row:
                c.execute('''
                    UPDATE feedback
                    SET feedback = ?, comment = ?, timestamp = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (feedback, comment, row[0]))
                print(f"[save_feedback] Updated existing feedback (id={row[0]})")
            else:
                c.execute('''
                    INSERT INTO feedback (user_email, convo_id, message, feedback, comment)
                    VALUES (?, ?, ?, ?, ?)
                ''', (hashed_email, convo_id, message, feedback, comment))
                print("[save_feedback] Inserted new feedback")

            conn.commit()

    except Exception as e:
        print(f"[save_feedback] Exception while saving feedback: {e}")


def get_feedback(convo_id, message):
    """
    Retrieve feedback for a specific message in a conversation.
    Args:
        convo_id (int): Conversation ID.
        message (str): The message to look up.
    Returns:
        str or None: The feedback value, or None if not found.
    """
    user_email = st.session_state.get("user_profile", {}).get("email")
    if not user_email:
        print("[get_feedback] No user email found in session. Cannot retrieve feedback.")
        return None

    hashed_email = hash_email(user_email)

    try:
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()
            c.execute('''
                SELECT feedback FROM feedback WHERE user_email = ? AND convo_id = ? AND message = ?
            ''', (hashed_email, convo_id, message))
            row = c.fetchone()
            if row:
                return row[0]
            else:
                return None
    except Exception as e:
        print(f"[get_feedback] Exception while fetching feedback: {e}")
        return None


def get_feedback_per_message(convo_id=None):
    """
    Retrieve all feedback entries, optionally filtered by conversation ID.
    Args:
        convo_id (int, optional): Conversation ID to filter by.
    Returns:
        list: List of feedback dicts.
    """
    with sqlite3.connect("feedback.db") as conn:
        c = conn.cursor()

        if convo_id is None:
            c.execute('''
                SELECT user_email, convo_id, message, feedback, comment, timestamp
                FROM feedback
                ORDER BY timestamp DESC
            ''')
        else:
            c.execute('''
                SELECT user_email, convo_id, message, feedback, comment, timestamp
                FROM feedback
                WHERE convo_id = ?
                ORDER BY timestamp DESC
            ''', (convo_id,))

        rows = c.fetchall()

    return [
        {
            "user_email": r[0],
            "convo_id": r[1],
            "message": r[2],
            "feedback": r[3],
            "comment": r[4],
            "timestamp": r[5],
        }
        for r in rows
    ]


def get_feedback_statistics():
    """
    Get statistics about feedback (positive/negative counts).
    Returns:
        dict: Statistics including total, positive, negative counts and percentage.
    """
    try:
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()
            
            c.execute("SELECT COUNT(*) FROM feedback WHERE feedback = 'positive'")
            positive = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM feedback WHERE feedback = 'negative'")
            negative = c.fetchone()[0]
            
            total = positive + negative
            positive_pct = (positive / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "positive": positive,
                "negative": negative,
                "positive_percentage": round(positive_pct, 1)
            }
    except Exception as e:
        print(f"[get_feedback_statistics] Error: {e}")
        return {"total": 0, "positive": 0, "negative": 0, "positive_percentage": 0}


def is_authenticated():
    """
    Check if the user is authenticated in the current session.
    Returns:
        bool: True if authenticated, False otherwise.
    """
    return st.session_state.get("authenticated", False)


def set_authenticated_user(user):
    """
    Set the authenticated user in session state.
    Args:
        user (dict): User profile data.
    """
    st.session_state["authenticated"] = True
    st.session_state["user_profile"] = {
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "join_date": user.get("join_date", datetime.now().strftime("%B %Y"))
    }


def require_authentication():
    """
    Require the user to be authenticated, otherwise stop execution and show a warning.
    """
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("⚠️ Please login from the main page to access this section.")
        st.stop()


def logout_user():
    """
    Log out the user by clearing authentication-related session state keys.
    """
    keys_to_remove = ["authenticated", "user_email", "user_name", "profile_picture", "join_date", "font_size", "user_profile"]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def initialize_session_state():
    """
    Initialize all required session state variables with default values.
    Call this at the start of your app.
    """
    defaults = {
        "authenticated": False,
        "conversations": [],
        "active_conversation": None,
        "user_profile": {},
        "font_size": "medium",
        "theme": "light"
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def validate_email(email):
    """
    Validate email format using regex.
    Args:
        email (str): Email address to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """
    Validate password strength.
    Args:
        password (str): Password to validate.
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"


def format_message_time(timestamp_str):
    """
    Format a timestamp string to a more readable format.
    Args:
        timestamp_str (str): Timestamp string.
    Returns:
        str: Formatted time string.
    """
    try:
        dt = datetime.fromisoformat(timestamp_str)
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            return dt.strftime("%I:%M %p")
        elif diff.days == 1:
            return f"Yesterday {dt.strftime('%I:%M %p')}"
        elif diff.days < 7:
            return dt.strftime("%A %I:%M %p")
        else:
            return dt.strftime("%b %d, %Y %I:%M %p")
    except:
        return timestamp_str


def search_conversations(query, conversations=None):
    """
    Search through conversations for matching messages.
    Args:
        query (str): Search query.
        conversations (list, optional): List of conversations to search.
    Returns:
        list: List of matching conversation IDs and message snippets.
    """
    if conversations is None:
        conversations = st.session_state.get("conversations", [])
    
    query_lower = query.lower()
    results = []
    
    for convo in conversations:
        matches = []
        for msg in convo.get("messages", []):
            if query_lower in msg.get("message", "").lower():
                matches.append({
                    "message": msg.get("message", "")[:100] + "...",
                    "time": msg.get("time", "")
                })
        
        if matches or query_lower in convo.get("title", "").lower():
            results.append({
                "convo_id": convo.get("id"),
                "title": convo.get("title"),
                "date": convo.get("date"),
                "matches": matches
            })
    
    return results


def get_user_statistics():
    """
    Get statistics about user's conversations.
    Returns:
        dict: Statistics including total conversations, messages, etc.
    """
    conversations = st.session_state.get("conversations", [])
    
    total_conversations = len(conversations)
    total_messages = sum(len(c.get("messages", [])) for c in conversations)
    
    user_messages = sum(
        1 for c in conversations 
        for m in c.get("messages", []) 
        if m.get("sender") == "user"
    )
    
    ai_messages = total_messages - user_messages
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "user_messages": user_messages,
        "ai_messages": ai_messages,
        "avg_messages_per_conversation": round(total_messages / total_conversations, 1) if total_conversations > 0 else 0
    }


def create_responsive_columns(num_columns, min_width="120px", mobile_stack_breakpoint=480):
    """
    Create responsive columns that stack vertically on mobile devices.
    Args:
        num_columns (int): Number of columns for desktop layout.
        min_width (str): Minimum width for each column before stacking.
        mobile_stack_breakpoint (int): Screen width (px) below which to stack.
    Returns:
        list: List of Streamlit column objects.
    """
    if mobile_stack_breakpoint > 768:
        return st.columns([1] * num_columns)
    else:
        return st.columns(num_columns)


def render_responsive_buttons(buttons_data, columns_per_row=None, mobile_stack=True):
    """
    Render buttons in a responsive layout that stacks on mobile.
    Args:
        buttons_data (list): List of dictionaries with button data.
        columns_per_row (int, optional): Number of buttons per row on desktop.
        mobile_stack (bool): Whether to stack buttons on mobile.
    Returns:
        None (renders buttons directly to Streamlit)
    """
    if not buttons_data:
        return
        
    if columns_per_row is None:
        columns_per_row = min(len(buttons_data), 4)
    
    st.markdown(f"""
    <style>
    @media (max-width: 768px) {{
        .responsive-button-container {{
            display: flex;
            flex-direction: {'column' if mobile_stack else 'row'};
            gap: 0.5rem;
            flex-wrap: wrap;
        }}
        .responsive-button-container .stButton {{
            flex: 1 1 auto;
            min-width: 120px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    for i in range(0, len(buttons_data), columns_per_row):
        row_buttons = buttons_data[i:i + columns_per_row]
        cols = st.columns(len(row_buttons))
        
        for j, button_data in enumerate(row_buttons):
            with cols[j]:
                button_type = button_data.get('type', 'primary')
                help_text = button_data.get('help', '')
                use_container_width = button_data.get('use_container_width', True)
                
                if st.button(
                    button_data['text'],
                    key=button_data['key'],
                    type=button_type,
                    help=help_text,
                    use_container_width=use_container_width
                ):
                    if button_data.get('action'):
                        button_data['action']()


def get_mobile_friendly_columns(desktop_ratios, mobile_threshold=768):
    """
    Convert desktop column ratios to mobile-friendly layout.
    Args:
        desktop_ratios (list): List of column width ratios for desktop.
        mobile_threshold (int): Screen width threshold for mobile layout.
    Returns:
        list: Mobile-optimized column ratios.
    """
    if len(desktop_ratios) > 4:
        return [1] * min(2, len(desktop_ratios))
    elif len(desktop_ratios) > 2:
        return [1] * len(desktop_ratios)
    else:
        return desktop_ratios


def apply_custom_css():
    """
    Apply custom CSS for improved UI/UX across the app.
    Includes mobile-responsive styles.
    """
    st.markdown("""
    <style>
    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .stButton button {
            font-size: 14px;
            padding: 0.5rem 1rem;
        }
        .stTextInput input {
            font-size: 16px;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        h2 {
            font-size: 1.4rem !important;
        }
        h3 {
            font-size: 1.2rem !important;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)


def format_file_size(size_bytes):
    """
    Format file size in bytes to human-readable format.
    Args:
        size_bytes (int): File size in bytes.
    Returns:
        str: Formatted file size (e.g., "1.5 MB").
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def detect_crisis_keywords(message):
    """
    Detect crisis-related keywords in user messages.
    Args:
        message (str): User's message.
    Returns:
        tuple: (bool, list) - (crisis_detected, matched_keywords)
    """
    crisis_keywords = [
        'suicide', 'kill myself', 'end my life', 'want to die',
        'hurt myself', 'self harm', 'no reason to live', 'better off dead',
        'overdose', 'jump off', 'end it all', 'can\'t go on'
    ]
    
    message_lower = message.lower()
    matched = [kw for kw in crisis_keywords if kw in message_lower]
    
    return len(matched) > 0, matched


def get_crisis_resources():
    """
    Get crisis helpline and resource information.
    Returns:
        dict: Crisis resources by country/region.
    """
    return {
        "India": {
            "hotlines": [
                {"name": "AASRA", "number": "91-9820466926", "available": "24/7"},
                {"name": "Vandrevala Foundation", "number": "1860-2662-345", "available": "24/7"},
                {"name": "iCall", "number": "91-9152987821", "available": "Mon-Sat, 8am-10pm"}
            ],
            "website": "https://www.tiss.edu/view/3/projects/icall/"
        },
        "USA": {
            "hotlines": [
                {"name": "National Suicide Prevention Lifeline", "number": "988", "available": "24/7"},
                {"name": "Crisis Text Line", "number": "Text HOME to 741741", "available": "24/7"}
            ],
            "website": "https://988lifeline.org/"
        },
        "UK": {
            "hotlines": [
                {"name": "Samaritans", "number": "116 123", "available": "24/7"},
                {"name": "Crisis Text Line UK", "number": "Text SHOUT to 85258", "available": "24/7"}
            ],
            "website": "https://www.samaritans.org/"
        },
        "International": {
            "hotlines": [
                {"name": "Befrienders Worldwide", "number": "Visit website for local numbers", "available": "Varies by location"}
            ],
            "website": "https://befrienders.org/"
        }
    }


def log_user_activity(activity_type, details=None):
    """
    Log user activity for analytics and debugging.
    Args:
        activity_type (str): Type of activity (e.g., 'login', 'new_conversation', 'feedback').
        details (dict, optional): Additional details about the activity.
    """
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        user_email = st.session_state.get("user_profile", {}).get("email", "anonymous")
        hashed_email = hash_email(user_email) if user_email != "anonymous" else "anonymous"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": hashed_email,
            "activity": activity_type,
            "details": details or {}
        }
        
        log_file = f"{log_dir}/activity_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily log file
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"[log_user_activity] Error logging activity: {e}")


def rate_limit_check(user_key, max_requests=50, time_window_minutes=60):
    """
    Check if user has exceeded rate limit for API calls.
    Args:
        user_key (str): User identifier (email or IP).
        max_requests (int): Maximum number of requests allowed.
        time_window_minutes (int): Time window in minutes.
    Returns:
        tuple: (bool, int) - (is_allowed, requests_remaining)
    """
    if 'rate_limit_data' not in st.session_state:
        st.session_state.rate_limit_data = {}
    
    now = datetime.now()
    
    if user_key not in st.session_state.rate_limit_data:
        st.session_state.rate_limit_data[user_key] = {
            'requests': [],
            'reset_time': now + timedelta(minutes=time_window_minutes)
        }
    
    user_data = st.session_state.rate_limit_data[user_key]
    
    # Reset if time window expired
    if now > user_data['reset_time']:
        user_data['requests'] = []
        user_data['reset_time'] = now + timedelta(minutes=time_window_minutes)
    
    # Filter requests within time window
    cutoff_time = now - timedelta(minutes=time_window_minutes)
    user_data['requests'] = [
        req_time for req_time in user_data['requests'] 
        if req_time > cutoff_time
    ]
    
    # Check limit
    if len(user_data['requests']) >= max_requests:
        return False, 0
    
    # Add current request
    user_data['requests'].append(now)
    requests_remaining = max_requests - len(user_data['requests'])
    
    return True, requests_remaining


def generate_session_id():
    """
    Generate a unique session ID for tracking.
    Returns:
        str: Unique session ID.
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = hashlib.sha256(
            f"{datetime.now().isoformat()}{hash(str(st.session_state))}".encode()
        ).hexdigest()[:16]
    return st.session_state.session_id


def calculate_response_time(start_time):
    """
    Calculate response time from start time.
    Args:
        start_time (datetime): Start time of the operation.
    Returns:
        float: Response time in seconds.
    """
    return (datetime.now() - start_time).total_seconds()


def format_duration(seconds):
    """
    Format duration in seconds to human-readable format.
    Args:
        seconds (float): Duration in seconds.
    Returns:
        str: Formatted duration.
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_sentiment_emoji(sentiment):
    """
    Get emoji representation for sentiment.
    Args:
        sentiment (str): Sentiment string ('positive', 'negative', 'neutral').
    Returns:
        str: Emoji character.
    """
    sentiment_map = {
        'positive': '😊',
        'negative': '😔',
        'neutral': '😐',
        'very_positive': '😄',
        'very_negative': '😢'
    }
    return sentiment_map.get(sentiment, '😐')


def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to specified length with suffix.
    Args:
        text (str): Text to truncate.
        max_length (int): Maximum length.
        suffix (str): Suffix to add if truncated.
    Returns:
        str: Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].strip() + suffix


def get_welcome_message():
    """
    Get a contextual welcome message based on time of day.
    Returns:
        str: Welcome message.
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 22:
        greeting = "Good evening"
    else:
        greeting = "Hello"
    
    user_name = st.session_state.get("user_profile", {}).get("name", "")
    
    if user_name:
        return f"{greeting}, {user_name}! How can I support you today?"
    return f"{greeting}! How can I support you today?"


def clean_database():
    """
    Clean up old entries from feedback database (older than 90 days).
    Returns:
        int: Number of entries deleted.
    """
    try:
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=90)).isoformat()
            
            c.execute("SELECT COUNT(*) FROM feedback WHERE timestamp < ?", (cutoff_date,))
            count = c.fetchone()[0]
            
            c.execute("DELETE FROM feedback WHERE timestamp < ?", (cutoff_date,))
            conn.commit()
            
            return count
    except Exception as e:
        print(f"[clean_database] Error: {e}")
        return 0


def export_user_data():
    """
    Export all user data (conversations, feedback) for GDPR compliance.
    Returns:
        dict: User data package.
    """
    user_email = st.session_state.get("user_profile", {}).get("email")
    if not user_email:
        return None
    
    data_package = {
        "export_date": datetime.now().isoformat(),
        "user_email": user_email,
        "conversations": [],
        "feedback": []
    }
    
    # Get conversations
    user_key = user_email
    data_package["conversations"] = [
        c for c in st.session_state.get("conversations", [])
        if c.get("user_key") == user_key
    ]
    
    # Get feedback
    hashed_email = hash_email(user_email)
    try:
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM feedback WHERE user_email = ?", (hashed_email,))
            rows = c.fetchall()
            
            data_package["feedback"] = [
                {
                    "convo_id": r[2],
                    "message": r[3],
                    "feedback": r[4],
                    "comment": r[5],
                    "timestamp": r[6]
                }
                for r in rows
            ]
    except Exception as e:
        print(f"[export_user_data] Error: {e}")
    
    return data_package


def delete_user_data():
    """
    Delete all user data (conversations, feedback) for GDPR compliance.
    Returns:
        bool: True if successful, False otherwise.
    """
    user_email = st.session_state.get("user_profile", {}).get("email")
    if not user_email:
        return False
    
    try:
        # Delete conversations file
        memory_file = get_memory_file()
        if os.path.exists(memory_file):
            os.remove(memory_file)
        
        # Delete feedback
        hashed_email = hash_email(user_email)
        with sqlite3.connect("feedback.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM feedback WHERE user_email = ?", (hashed_email,))
            conn.commit()
        
        # Clear session state
        st.session_state.conversations = []
        st.session_state.active_conversation = None
        
        return True
    except Exception as e:
        print(f"[delete_user_data] Error: {e}")
        return False


def get_conversation_count_by_date(days=30):
    """
    Get conversation count grouped by date for the last N days.
    Args:
        days (int): Number of days to look back.
    Returns:
        dict: Date -> count mapping.
    """
    conversations = st.session_state.get("conversations", [])
    date_counts = {}
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%B %d, %Y")
        date_counts[date] = 0
    
    for convo in conversations:
        convo_date = convo.get("date", "")
        if convo_date in date_counts:
            date_counts[convo_date] += 1
    
    return date_counts


def check_api_health(api_key=None):
    """
    Check if the AI API is healthy and responsive.
    Args:
        api_key (str, optional): API key to test.
    Returns:
        tuple: (bool, str) - (is_healthy, status_message)
    """
    if not api_key:
        return False, "No API key provided"
    
    try:
        google.generativeai.configure(api_key=api_key)
        model = google.generativeai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        return True, "API is healthy"
    except Exception as e:
        return False, f"API error: {str(e)[:100]}"