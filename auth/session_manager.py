"""
Session management using cookies for persistent authentication across page refreshes.
Uses extra-streamlit-components for reliable cookie handling.
"""
import streamlit as st
import json
from datetime import datetime, timedelta
from auth.auth_utils import get_user_by_email
from extra_streamlit_components import CookieManager

# Cookie name for storing session data
SESSION_COOKIE_NAME = "talkheal_session"
SESSION_EXPIRY_DAYS = 7  # Session expires after 7 days

# Initialize cookie manager
@st.cache_resource
def get_cookie_manager():
    return CookieManager()

def set_session_cookie(email, user_data):
    """
    Set a cookie with user session data.
    
    Args:
        email (str): User's email
        user_data (dict): User profile data
    """
    try:
        cookie_manager = get_cookie_manager()
        
        session_data = {
            "email": email,
            "authenticated": True,
            "user_profile": user_data,
            "expires_at": (datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
        }
        
        # Convert to JSON string
        session_json = json.dumps(session_data)
        
        # Set cookie (expires in 7 days)
        cookie_manager.set(
            SESSION_COOKIE_NAME,
            session_json,
            expires_at=datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)
        )
    except Exception as e:
        # If cookie manager fails, fall back to localStorage
        _set_session_storage_fallback(email, user_data)


def get_session_cookie():
    """
    Get session data from cookie.
    
    Returns:
        dict or None: Session data if cookie exists and is valid, None otherwise
    """
    try:
        cookie_manager = get_cookie_manager()
        cookie_value = cookie_manager.get(SESSION_COOKIE_NAME)
        
        if not cookie_value:
            # Try fallback to localStorage
            return _get_session_storage_fallback()
        
        # Parse JSON data
        session_data = json.loads(cookie_value)
        
        # Check if session has expired
        expires_at_str = session_data.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                # Session expired, clear cookie
                clear_session_cookie()
                return None
        
        return session_data
    except Exception as e:
        # If there's any error, try fallback
        return _get_session_storage_fallback()


def clear_session_cookie():
    """
    Clear the session cookie.
    """
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(SESSION_COOKIE_NAME)
    except Exception:
        pass
    # Also clear localStorage fallback
    _clear_session_storage_fallback()


def restore_session_from_storage():
    """
    Restore user session from cookie if it exists.
    This should be called at the start of the app.
    
    Returns:
        bool: True if session was restored, False otherwise
    """
    # Only restore if not already authenticated
    if st.session_state.get("authenticated", False):
        return True
    
    # Check if we've already tried to restore in this session
    # This prevents infinite loops
    if st.session_state.get("session_restore_attempted", False):
        return False
    
    # Mark that we've attempted restoration
    st.session_state["session_restore_attempted"] = True
    
    # Try to get session data from cookie
    session_data = get_session_cookie()
    
    if session_data and session_data.get("authenticated"):
        email = session_data.get("email")
        user_profile = session_data.get("user_profile", {})
        
        # Handle guest users (they don't exist in database)
        if email == "guest@talkheal.app":
            # Restore guest session directly
            st.session_state.authenticated = True
            st.session_state.user_profile = user_profile
            st.session_state.user_name = user_profile.get("name", "Guest Healer")
            return True
        
        # For regular users, verify they still exist in database
        user = get_user_by_email(email)
        if user:
            # Restore session state
            st.session_state.authenticated = True
            st.session_state.user_profile = user_profile
            st.session_state.user_name = user_profile.get("name", email)
            return True
        else:
            # User doesn't exist anymore, clear cookie
            clear_session_cookie()
            return False
    
    return False


# Fallback functions using localStorage (in case cookies don't work)
def _set_session_storage_fallback(email, user_data):
    """Fallback: Set localStorage using JavaScript"""
    session_data = {
        "email": email,
        "authenticated": True,
        "user_profile": user_data,
        "expires_at": (datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
    }
    session_json = json.dumps(session_data)
    js_code = f"""
    <script>
        try {{
            localStorage.setItem("{SESSION_COOKIE_NAME}", {json.dumps(session_json)});
        }} catch(e) {{
            console.error("Error setting session storage:", e);
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


def _get_session_storage_fallback():
    """Fallback: Get localStorage using JavaScript"""
    try:
        from streamlit_js_eval import streamlit_js_eval
        storage_value = streamlit_js_eval(
            js_expressions=f'localStorage.getItem("{SESSION_COOKIE_NAME}")',
            key=f"get_session_fallback_{SESSION_COOKIE_NAME}"
        )
        
        if not storage_value or storage_value == "null" or storage_value == "None" or storage_value == "":
            return None
        
        storage_str = str(storage_value) if not isinstance(storage_value, str) else storage_value
        if isinstance(storage_value, dict):
            storage_str = storage_value.get('value', None) or storage_value.get('result', None)
            if not storage_str:
                return None
        
        session_data = json.loads(storage_str)
        
        # Check expiration
        expires_at_str = session_data.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                _clear_session_storage_fallback()
                return None
        
        return session_data
    except Exception:
        return None


def _clear_session_storage_fallback():
    """Fallback: Clear localStorage"""
    js_code = f"""
    <script>
        try {{
            localStorage.removeItem("{SESSION_COOKIE_NAME}");
        }} catch(e) {{
            console.error("Error clearing session storage:", e);
        }}
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)
