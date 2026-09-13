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
    """Default citizen and safety commuter accounts."""
    users = {}
    
    # 1. Citizen Commuter Account
    hash1, salt1 = _hash_password("Citizen@2026")
    users["ananya.sharma@gmail.com"] = {
        "name": "Ananya Sharma",
        "email": "ananya.sharma@gmail.com",
        "role": "Daily Metro & Walking Commuter",
        "district": "South Delhi",
        "hash": hash1,
        "salt": salt1,
        "created_at": "2026-01-15T09:00:00Z",
        "is_verified": True
    }
    
    # 2. Neighborhood Watch Member
    hash2, salt2 = _hash_password("Safety@2026")
    users["rahul.verma@gmail.com"] = {
        "name": "Rahul Verma",
        "email": "rahul.verma@gmail.com",
        "role": "Neighborhood Safety Volunteer",
        "district": "Central Delhi",
        "hash": hash2,
        "salt": salt2,
        "created_at": "2026-02-01T14:30:00Z",
        "is_verified": True
    }

    # 3. Student / Night Traveler
    hash3, salt3 = _hash_password("Delhi@2026")
    users["rohit.gupta@delhiuniv.ac.in"] = {
        "name": "Rohit Gupta",
        "email": "rohit.gupta@delhiuniv.ac.in",
        "role": "Student & Night Traveler",
        "district": "North Delhi",
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
    Authenticates a citizen against the store.
    Returns: (success, message, user_data)
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return False, "Please provide both your email and password.", {}

    users = load_users()
    user = users.get(email)
    if not user:
        return False, "Invalid email or password. Please check your credentials.", {}

    if not _verify_password(password, user["hash"], user["salt"]):
        return False, "Invalid email or password. Please check your credentials.", {}

    return True, "Login successful! Welcome back.", user

def register_user(email: str, password: str, name: str, role: str, district: str) -> tuple[bool, str, dict]:
    """
    Registers a new citizen user and persists their account.
    Returns: (success, message, user_data)
    """
    email = (email or "").strip().lower()
    name = (name or "").strip()
    
    if not email or "@" not in email:
        return False, "Please enter a valid email address.", {}
    
    if not name:
        return False, "Please enter your name.", {}
        
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long.", {}

    users = load_users()
    if email in users:
        return False, "An account with this email address already exists. Please sign in.", {}

    pwd_hash, salt = _hash_password(password)
    new_user = {
        "name": name,
        "email": email,
        "role": role or "Citizen User",
        "district": district or "Delhi NCR",
        "hash": pwd_hash,
        "salt": salt,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "is_verified": True
    }
    users[email] = new_user
    save_users(users)
    return True, "Account created successfully! You are now logged in.", new_user

def check_rate_limit() -> tuple[bool, str]:
    now = time.time()
    lockout_until = st.session_state.get("auth_lockout_until", 0)
    if now < lockout_until:
        rem_sec = int(lockout_until - now)
        return False, f"Too many failed login attempts. Please wait {rem_sec} seconds before trying again."
    return True, ""

def record_failed_attempt():
    attempts = st.session_state.get("auth_failed_attempts", 0) + 1
    st.session_state["auth_failed_attempts"] = attempts
    if attempts >= 5:
        st.session_state["auth_lockout_until"] = time.time() + 180  # 3 minute lockout
        st.session_state["auth_failed_attempts"] = 0

def record_successful_login(user: dict):
    st.session_state["authenticated"] = True
    st.session_state["user_email"] = user.get("email", "citizen@rakshak.ai")
    st.session_state["user_name"] = user.get("name", "Citizen User")
    st.session_state["user_role"] = user.get("role", "Citizen Commuter")
    st.session_state["user_district"] = user.get("district", "Delhi NCR")
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
    Renders the citizen-centric Cruip Open PRO styled secure authentication portal.
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
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 11px;
        font-family: 'Geist Mono', monospace;
        font-weight: 700;
        margin-bottom: 14px;
        letter-spacing: 0.05em;
    }
    .login-title {
        font-size: 28px;
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
            CITIZEN SAFETY PORTAL
        </div>
        <div class="login-title">Rakshak.ai</div>
        <div class="login-subtitle">
            Sign in to access real-time neighborhood danger heatmaps, live safe walking corridors, emergency SOS, and safe travel navigation.
        </div>
        <div class="feature-pill-bar">
            <span class="feature-pill">🚶 Safe Walking Routes</span>
            <span class="feature-pill">🚗 Safe Vehicle Corridors</span>
            <span class="feature-pill">🚨 Real-Time Risk Alerts</span>
            <span class="feature-pill">🔒 Private & Secure</span>
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
        ["🔐 Sign In", "📝 Create Citizen Account", "🚀 Instant 1-Click Guest Access"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col_wrap = st.columns([1, 2, 1])
    with col_wrap[1]:
        # --- TAB 1: SIGN IN ---
        if auth_tab_choice.startswith("🔐 Sign In"):
            with st.form("form_citizen_login"):
                st.markdown("##### 👤 Sign in to your Account")
                login_email = st.text_input("Email Address", placeholder="e.g. ananya.sharma@gmail.com", key="in_login_email")
                login_password = st.text_input("Password", type="password", placeholder="••••••••", key="in_login_pwd")
                
                submitted = st.form_submit_button("🔓 Sign In & Explore Safe Routes", use_container_width=True)
                
                if submitted:
                    ok, msg, user_data = authenticate_user(login_email, login_password)
                    if ok:
                        record_successful_login(user_data)
                        st.success(f"✅ Welcome back, {user_data['name']}!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        record_failed_attempt()
                        st.error(f"❌ {msg}")
            
            st.caption("💡 Quick test account: `ananya.sharma@gmail.com` | Password: `Citizen@2026` or use the **Instant 1-Click Guest Access** tab.")

        # --- TAB 2: CREATE CITIZEN ACCOUNT ---
        elif auth_tab_choice.startswith("📝 Create"):
            with st.form("form_citizen_register"):
                st.markdown("##### 📝 Create Your Free Citizen Account")
                reg_name = st.text_input("Your Full Name", placeholder="e.g. Ananya Sharma")
                reg_email = st.text_input("Email Address", placeholder="e.g. ananya@example.com")
                
                c_role, c_dist = st.columns(2)
                with c_role:
                    reg_role = st.selectbox(
                        "Primary Commute / Safety Profile",
                        ["Daily Metro & Walking Commuter", "Student / Night Traveler", "Neighborhood Resident", "Senior Citizen Commuter", "Neighborhood Safety Volunteer"]
                    )
                with c_dist:
                    reg_district = st.selectbox(
                        "Your Primary District / Neighborhood",
                        ["South Delhi", "Central Delhi", "New Delhi", "North Delhi", "South-East", "South-West", "West Delhi", "North-West", "Rohini", "Dwarka", "East Delhi", "Shahdara", "North-East", "Outer Delhi", "Outer-North"]
                    )
                
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    reg_p1 = st.text_input("Password", type="password", placeholder="Min 6 characters")
                with c_p2:
                    reg_p2 = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                
                reg_submit = st.form_submit_button("📝 Create Free Account", use_container_width=True)
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

        # --- TAB 3: INSTANT GUEST & DEMO ACCESS ---
        elif auth_tab_choice.startswith("🚀 Instant"):
            st.markdown("""
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 16px; padding: 20px; text-align: center; margin-top: 10px; margin-bottom: 14px;">
                <div style="font-size: 16px; font-weight: 800; color: #fff; margin-bottom: 6px;">⚡ Instant One-Click Citizen Access</div>
                <div style="font-size: 12.5px; color: #94a3b8;">
                    No registration or password typing needed. Pick a profile or continue as a guest to explore Delhi safe routes instantly:
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Big prominent guest button
            if st.button("👤 Continue as Public Citizen (Instant Explorer)", use_container_width=True, type="primary"):
                record_successful_login({
                    "name": "Delhi Citizen",
                    "email": "citizen@delhi.gov.in",
                    "role": "Public Citizen",
                    "district": "Delhi NCR"
                })
                st.success("✅ Welcome to Rakshak.ai! Loading safety dashboard...")
                time.sleep(0.3)
                st.rerun()

            st.markdown("<div style='margin-top: 12px; margin-bottom: 8px; font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; text-align: center;'>— Or Choose a Sample Citizen Profile —</div>", unsafe_allow_html=True)

            c_d1, c_d2 = st.columns(2)
            with c_d1:
                if st.button("🚶 Ananya (Metro Commuter)", use_container_width=True):
                    users = load_users()
                    demo_user = users.get("ananya.sharma@gmail.com")
                    if demo_user:
                        record_successful_login(demo_user)
                        st.success("Logged in as Ananya Sharma (South Delhi Commuter)!")
                        time.sleep(0.3)
                        st.rerun()
            with c_d2:
                if st.button("🛡️ Rahul (Safety Volunteer)", use_container_width=True):
                    users = load_users()
                    demo_user = users.get("rahul.verma@gmail.com")
                    if demo_user:
                        record_successful_login(demo_user)
                        st.success("Logged in as Rahul Verma (Central Delhi Resident)!")
                        time.sleep(0.3)
                        st.rerun()
