"""
OAuth utility functions for TalkHeal
Handles OAuth authentication flow and user data processing
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import secrets
import hashlib
from auth.oauth_config import oauth_config
from auth.auth_utils import init_db, register_user, authenticate_user, get_user_by_email

def generate_state() -> str:
    """Generate a secure random state for OAuth flow"""
    return secrets.token_urlsafe(32)

def store_oauth_state(state: str, provider: str) -> None:
    """Store OAuth state in session state"""
    if "oauth_states" not in st.session_state:
        st.session_state.oauth_states = {}
    st.session_state.oauth_states[state] = {
        "provider": provider,
        "timestamp": datetime.now().isoformat()
    }

def verify_oauth_state(state: str) -> Optional[str]:
    """Verify OAuth state and return provider"""
    if "oauth_states" not in st.session_state:
        return None
    
    if state not in st.session_state.oauth_states:
        return None
    
    # Clean up old states (older than 10 minutes)
    current_time = datetime.now()
    for stored_state, data in list(st.session_state.oauth_states.items()):
        state_time = datetime.fromisoformat(data["timestamp"])
        if (current_time - state_time).seconds > 600:  # 10 minutes
            del st.session_state.oauth_states[stored_state]
    
    if state in st.session_state.oauth_states:
        return st.session_state.oauth_states[state]["provider"]
    
    return None

def exchange_code_for_token(provider_name: str, code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token"""
    try:
        provider = oauth_config.get_provider(provider_name)
        
        data = {
            "client_id": provider.client_id,
            "client_secret": provider.client_secret,
            "code": code,
            "redirect_uri": provider.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        headers = {
            "Accept": "application/json",
            "User-Agent": "TalkHeal-OAuth/1.0"
        }
        
        response = requests.post(provider.token_url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        st.error(f"Error exchanging code for token: {str(e)}")
        return None

def get_user_info(provider_name: str, access_token: str) -> Optional[Dict[str, Any]]:
    """Get user information from OAuth provider"""
    try:
        provider = oauth_config.get_provider(provider_name)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "TalkHeal-OAuth/1.0"
        }
        
        response = requests.get(provider.user_info_url, headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        
        # Normalize user data across providers
        return normalize_user_data(provider_name, user_data)
    
    except Exception as e:
        st.error(f"Error fetching user info: {str(e)}")
        return None

def normalize_user_data(provider_name: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize user data from different OAuth providers"""
    normalized = {
        "provider": provider_name,
        "provider_id": None,
        "email": None,
        "name": None,
        "picture": None,
        "verified": False
    }
    
    if provider_name == "google":
        normalized.update({
            "provider_id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture"),
            "verified": user_data.get("verified_email", False)
        })
    
    elif provider_name == "github":
        normalized.update({
            "provider_id": str(user_data.get("id")),
            "email": user_data.get("email"),
            "name": user_data.get("name") or user_data.get("login"),
            "picture": user_data.get("avatar_url"),
            "verified": True  # GitHub emails are verified by default
        })
        
        if not normalized["email"]:
            # Try to get email from GitHub API
            try:
                email_response = requests.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((e for e in emails if e.get("primary")), emails[0] if emails else None)
                    if primary_email:
                        normalized["email"] = primary_email.get("email")
                        normalized["verified"] = primary_email.get("verified", False)
            except:
                pass
    
    elif provider_name == "microsoft":
        normalized.update({
            "provider_id": user_data.get("id"),
            "email": user_data.get("mail") or user_data.get("userPrincipalName"),
            "name": user_data.get("displayName"),
            "picture": user_data.get("photo", {}).get("@odata.mediaReadLink") if user_data.get("photo") else None,
            "verified": True  # Microsoft emails are verified
        })
    
    return normalized

def create_or_get_oauth_user(normalized_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Create or get existing OAuth user"""
    try:
        # Initialize database
        init_db()
        
        # Check if user exists by email
        if normalized_data["email"]:
            user_data = get_user_by_email(normalized_data["email"])
            
            if user_data:
                # User exists, return their data
                return True, {
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "provider": user_data["provider"],
                    "provider_id": user_data["provider_id"],
                    "profile_picture": user_data["profile_picture"],
                    "verified": user_data["verified"]
                }
        
        # Create new user with OAuth data
        success, message = register_user(
            name=normalized_data["name"] or "OAuth User",
            email=normalized_data["email"] or f"{normalized_data['provider']}_{normalized_data['provider_id']}@talkheal.app",
            password=None,  # OAuth users don't need passwords
            provider=normalized_data["provider"],
            provider_id=normalized_data["provider_id"],
            profile_picture=normalized_data["picture"],
            verified=normalized_data["verified"]
        )
        
        if success:
            return True, {
                "name": normalized_data["name"],
                "email": normalized_data["email"],
                "provider": normalized_data["provider"],
                "provider_id": normalized_data["provider_id"],
                "profile_picture": normalized_data["picture"],
                "verified": normalized_data["verified"]
            }
        else:
            return False, {"error": message}
    
    except Exception as e:
        return False, {"error": str(e)}

def handle_oauth_callback(provider_name: str, code: str, state: str) -> Tuple[bool, str]:
    """Handle OAuth callback and authenticate user"""
    try:
        # Verify state
        verified_provider = verify_oauth_state(state)
        if verified_provider != provider_name:
            return False, "Invalid OAuth state"
        
        # Exchange code for token
        token_data = exchange_code_for_token(provider_name, code)
        if not token_data:
            return False, "Failed to exchange code for token"
        
        access_token = token_data.get("access_token")
        if not access_token:
            return False, "No access token received"
        
        # Get user info
        user_data = get_user_info(provider_name, access_token)
        if not user_data:
            return False, "Failed to fetch user information"
        
        # Create or get user
        success, user_info = create_or_get_oauth_user(user_data)
        if not success:
            return False, user_info.get("error", "Failed to create/get user")
        
        # Set session state
        user_profile = {
            "name": user_info["name"],
            "email": user_info["email"],
            "profile_picture": user_info["profile_picture"],
            "join_date": datetime.now().strftime("%B %Y"),
            "font_size": "Medium",
            "provider": user_info["provider"],
            "provider_id": user_info["provider_id"],
            "verified": user_info["verified"]
        }
        st.session_state.authenticated = True
        st.session_state.user_profile = user_profile
        st.session_state.user_name = user_info["name"]
        
        # Save session to cookie for persistence across page refreshes
        from auth.session_manager import set_session_cookie
        set_session_cookie(user_info["email"], user_profile)
        
        # Clean up OAuth state
        if "oauth_states" in st.session_state and state in st.session_state.oauth_states:
            del st.session_state.oauth_states[state]
        
        return True, "Authentication successful"
    
    except Exception as e:
        return False, f"OAuth authentication failed: {str(e)}"

def get_oauth_login_url(provider_name: str) -> str:
    """Get OAuth login URL for a provider"""
    if not oauth_config.is_provider_available(provider_name):
        raise ValueError(f"OAuth provider '{provider_name}' not available")
    
    state = generate_state()
    store_oauth_state(state, provider_name)
    
    return oauth_config.get_auth_url(provider_name, state)
