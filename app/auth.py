import os
import json
import hashlib
import secrets
import time
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_FILE = os.path.join(BASE_DIR, "data", "users.json")

def _hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    """Generates a PBKDF2-HMAC-SHA256 hash with a cryptographically secure salt."""
    if salt is None:
        salt = secrets.token_bytes(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return key.hex(), salt.hex()

def _verify_password(password: str, stored_hash: str, stored_salt_hex: str) -> bool:
    """Verifies a plain password against the stored hex hash and salt."""
    try:
        salt = bytes.fromhex(stored_salt_hex)
        key, _ = _hash_password(password, salt)
        return secrets.compare_digest(key, stored_hash)
    except Exception:
        return False

def _init_default_users() -> dict:
    """Default verified law enforcement and civilian accounts."""
    users = {}
    
    # 1. Senior Inspector Account
    hash1, salt1 = _hash_password("Password@123")
    users["inspector@delhipolice.gov.in"] = {
        "name": "Inspector Rajeev Sharma",
        "email": "inspector@delhipolice.gov.in",
        "role": "Senior Crime Branch Inspector",
        "district": "Central",
        "hash": hash1,
        "salt": salt1,
        "created_at": "2026-01-15T09:00:00Z",
        "is_verified": True
    }
    
    # 2. Patrol Dispatcher Account
    hash2, salt2 = _hash_password("Dispatch@2026")
    users["dispatch@delhipolice.gov.in"] = {
        "name": "Sub-Inspector Priya Verma",
        "email": "dispatch@delhipolice.gov.in",
        "role": "Rapid Patrol Dispatcher",
        "district": "New Delhi",
        "hash": hash2,
        "salt": salt2,
        "created_at": "2026-02-01T14:30:00Z",
        "is_verified": True
    }

    # 3. Citizen Safety Analyst
    hash3, salt3 = _hash_password("Citizen@2026")
    users["citizen@rakshak.ai"] = {
        "name": "Ananya Sen (Civic Analyst)",
        "email": "citizen@rakshak.ai",
        "role": "Civic Community Safety Member",
        "district": "South",
        "hash": hash3,
        "salt": salt3,
        "created_at": "2026-03-01T10:00:00Z",
        "is_verified": True
    }

    return users

def load_users() -> dict:
    """Loads users from data/users.json or initializes with defaults."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    defaults = _init_default_users()
    save_users(defaults)
    return defaults

def save_users(users: dict) -> None:
    """Persists users to data/users.json securely."""
    try:
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to persist users: {e}")

def authenticate_user(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Authenticates a user against the store.
    Returns: (success, message, user_data)
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return False, "Please provide both email and password.", {}

    users = load_users()
    user = users.get(email)
    if not user:
        return False, "Invalid email or password.", {}

    if not _verify_password(password, user["hash"], user["salt"]):
        return False, "Invalid email or password.", {}

    return True, "Login successful!", user

def register_user(email: str, password: str, name: str, role: str, district: str) -> tuple[bool, str, dict]:
    """
    Registers a new user and persists their account.
    Returns: (success, message, user_data)
    """
    email = (email or "").strip().lower()
    name = (name or "").strip()
    
    if not email or "@" not in email or "." not in email:
        return False, "Please enter a valid email address.", {}
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long.", {}
    if not name:
        return False, "Please enter your full name.", {}

    users = load_users()
    if email in users:
        return False, "An account with this email already exists.", {}

    pwd_hash, salt = _hash_password(password)
    new_user = {
        "name": name,
        "email": email,
        "role": role or "Patrol Officer",
        "district": district or "Central",
        "hash": pwd_hash,
        "salt": salt,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "is_verified": True
    }
    users[email] = new_user
    save_users(users)
    return True, "Officer account registered successfully! You can now log in.", new_user

def check_rate_limit() -> tuple[bool, str]:
    """Checks for brute force attempts."""
    now = time.time()
    lockout_until = st.session_state.get("auth_lockout_until", 0)
    if now < lockout_until:
        rem_sec = int(lockout_until - now)
        return False, f"Too many failed login attempts. Portal temporarily locked for {rem_sec} seconds."
    return True, ""

def record_failed_attempt():
    attempts = st.session_state.get("auth_failed_attempts", 0) + 1
    st.session_state["auth_failed_attempts"] = attempts
    if attempts >= 5:
        st.session_state["auth_lockout_until"] = time.time() + 180  # 3 minute lockout
        st.session_state["auth_failed_attempts"] = 0

def record_successful_login(user: dict):
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = user.get("email", "officer@delhipolice.gov.in")
    st.session_state["user_name"] = user.get("name", "Verified Officer")
    st.session_state["user_role"] = user.get("role", "Patrol Officer")
    st.session_state["user_district"] = user.get("district", "Central")
    st.session_state["auth_failed_attempts"] = 0
    st.session_state["auth_lockout_until"] = 0

def logout_user():
    """Logs out the user and clears authentication session."""
    st.session_state["authenticated"] = False
    st.session_state.pop("user_email", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("user_role", None)
    st.session_state.pop("user_district", None)
    st.rerun()

def render_cruip_login_page():
    """
    Renders the Cruip Open PRO styled secure authentication portal.
    Halts main app execution until the user is authenticated.
    """
    st.markdown("""
    <style>
    /* Fullscreen Glassmorphic Login Overlay */
    .login-hero-container {
        max-width: 540px;
        margin: 25px auto 25px auto;
        padding: 34px 30px 24px 30px;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 32px rgba(99, 102, 241, 0.2);
        text-align: center;
    }
    .login-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(129, 140, 248, 0.35);
        color: #c7d2fe;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 11px;
        font-family: 'Geist Mono', monospace;
        font-weight: 700;
        margin-bottom: 14px;
        letter-spacing: 0.05em;
    }
    .login-title {
        font-size: 27px;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    .login-subtitle {
        font-size: 13.5px;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 20px;
    }
    .feature-pill-bar {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
    .feature-pill {
        font-size: 11px;
        color: #cbd5e1;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.09);
        padding: 3px 10px;
        border-radius: 9999px;
    }
    </style>
    
    <div class="login-hero-container">
        <div class="login-badge">
            <span style="width:7px; height:7px; border-radius:50%; background:#10b981; box-shadow:0 0 8px #10b981;"></span>
            DELHI POLICE SENTINEL GATEWAY
        </div>
        <div class="login-title">Rakshak.ai Security Enclave</div>
        <div class="login-subtitle">
            Secure Authentication Portal for Law Enforcement, Patrol Dispatches, and Civic Safety Forensics.
        </div>
        <div class="feature-pill-bar">
            <span class="feature-pill">🔐 PBKDF2-SHA256 Encryption</span>
            <span class="feature-pill">🛡️ DBSCAN Enclave</span>
            <span class="feature-pill">⚡ 60fps Radar Access</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Check for lockout
    allowed, lockout_msg = check_rate_limit()
    if not allowed:
        st.error(lockout_msg)
        st.stop()

    auth_tab_choice = st.radio(
        "Authentication Action",
        ["🔐 Sign In (Existing Officer)", "📝 Register Officer Credentials", "🚀 Instant 1-Click Demo Login"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col_wrap = st.columns([1, 2, 1])
    with col_wrap[1]:
        if auth_tab_choice.startswith("🔐 Sign In"):
            with st.form("form_officer_login"):
                st.markdown("##### 👤 Enter Officer Credentials")
                login_email = st.text_input("Official Email ID", placeholder="inspector@delhipolice.gov.in", key="in_login_email")
                login_password = st.text_input("Password", type="password", placeholder="••••••••", key="in_login_pwd")
                
                submitted = st.form_submit_button("🔓 Log In to Dashboard", use_container_width=True)
                
                if submitted:
                    ok, msg, user_data = authenticate_user(login_email, login_password)
                    if ok:
                        record_successful_login(user_data)
                        st.success(f"✅ Verified: Welcome {user_data['name']}!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        record_failed_attempt()
                        st.error(f"❌ {msg}")
            
            st.caption("💡 Default demo account: `inspector@delhipolice.gov.in` | Password: `Password@123`")

        elif auth_tab_choice.startswith("📝 Register"):
            with st.form("form_officer_register"):
                st.markdown("##### 📝 Create Official Account")
                reg_name = st.text_input("Full Officer Name", placeholder="e.g. Inspector Rajat Singh")
                reg_email = st.text_input("Official Email ID", placeholder="r.singh@delhipolice.gov.in")
                
                c_role, c_dist = st.columns(2)
                with c_role:
                    reg_role = st.selectbox(
                        "Designation / Role",
                        ["Senior Crime Branch Inspector", "Rapid Patrol Dispatcher", "Station House Officer (SHO)", "Geospatial Analyst", "Civic Safety Officer"]
                    )
                with c_dist:
                    reg_district = st.selectbox(
                        "Primary Jurisdiction",
                        ["Central", "New Delhi", "North", "South", "South-East", "South-West", "West", "North-West", "Rohini", "Dwarka", "East", "Shahdara", "North-East", "Outer", "Outer-North"]
                    )
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    reg_p1 = st.text_input("New Password", type="password", placeholder="Min 8 characters")
                with c_p2:
                    reg_p2 = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                
                reg_submit = st.form_submit_button("📝 Register & Issue Credentials", use_container_width=True)
                if reg_submit:
                    if reg_p1 != reg_p2:
                        st.error("❌ Passwords do not match.")
                    else:
                        ok, msg, new_user = register_user(reg_email, reg_p1, reg_name, reg_role, reg_district)
                        if ok:
                            st.success(f"✅ {msg}")
                            record_successful_login(new_user)
                            time.sleep(0.6)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

        elif auth_tab_choice.startswith("🚀 Instant"):
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 16px; padding: 20px; text-align: center; margin-top: 10px; margin-bottom: 14px;">
                <div style="font-size: 16px; font-weight: 800; color: #fff; margin-bottom: 6px;">⚡ Quick Evaluator / Demo Access</div>
                <div style="font-size: 12.5px; color: #94a3b8;">
                    Instantly authenticate into Rakshak.ai with pre-configured verified credentials. No typing required.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                if st.button("🛡️ Inspector Sharma (Central)", use_container_width=True):
                    users = load_users()
                    demo_user = users.get("inspector@delhipolice.gov.in")
                    if demo_user:
                        record_successful_login(demo_user)
                        st.success("Authenticated as Senior Inspector Sharma!")
                        time.sleep(0.3)
                        st.rerun()
            with c_d2:
                if st.button("🚓 Dispatcher Verma (New Delhi)", use_container_width=True):
                    users = load_users()
                    demo_user = users.get("dispatch@delhipolice.gov.in")
                    if demo_user:
                        record_successful_login(demo_user)
                        st.success("Authenticated as Dispatcher Verma!")
                        time.sleep(0.3)
                        st.rerun()
            
            st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
            if st.button("👤 Continue as Public Citizen (Guest Explorer)", use_container_width=True):
                record_successful_login({
                    "name": "Citizen Explorer",
                    "email": "citizen@delhi.gov.in",
                    "role": "Public Citizen",
                    "district": "All Districts"
                })
                st.success("Authenticated as Citizen Explorer!")
                time.sleep(0.3)
                st.rerun()
