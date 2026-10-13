"""
Rakshak.ai Emergency SOS Alert Component for Left Sidebar
Completely Client-Side Alert & Distress Notification System:
- Primary SOS EMERGENCY Button with pulsing animated red ring / glow
- Emergency Contact configuration modal via settings gear icon next to SOS button
- Primary Contact Name & Email with client-side validation and localStorage persistence (`rakshak_primary_contact`)
- SOS click interceptor when no primary contact is configured
- Native Browser Notification API permission flow & visual status badge
- In-dashboard persistent emergency alert banner with live Google Maps coordinate telemetry link
- Web Audio API continuous pulsing emergency beep alternating rapidly between 880Hz and 1200Hz
- Visible Dismiss / Silence Alarm button directly on the interface
- 100% Client-Side execution with zero third-party APIs, external backends, or API keys
"""

import json
from typing import Optional, List, Dict, Any
import streamlit.components.v1 as components

DEFAULT_HOTSPOTS_DATA = [
    {"name": "Rajiv Chowk Metro / CP Outer Circle", "lat": 28.6328, "lon": 77.2197, "risk": "CRITICAL"},
    {"name": "Seelampur Market & Flyover Underpass", "lat": 28.6644, "lon": 77.2711, "risk": "CRITICAL"},
    {"name": "Kashmere Gate ISBT & Metro Interchange", "lat": 28.6675, "lon": 77.2285, "risk": "CRITICAL"},
    {"name": "Old Delhi Railway Station / Chandni Chowk", "lat": 28.6560, "lon": 77.2301, "risk": "CRITICAL"},
    {"name": "Nand Nagri Depo Transit Corridor", "lat": 28.6942, "lon": 77.3060, "risk": "CRITICAL"},
    {"name": "Govindpuri & Giri Nagar Transit Hub", "lat": 28.5284, "lon": 77.2619, "risk": "HIGH"},
    {"name": "Anand Vihar ISBT & Railway Terminal", "lat": 28.6469, "lon": 77.3160, "risk": "CRITICAL"},
    {"name": "Uttam Nagar East Metro Junc & Arya Samaj Rd", "lat": 28.6219, "lon": 77.0601, "risk": "HIGH"},
    {"name": "Mangolpuri Y-Block Industrial Belt", "lat": 28.6980, "lon": 77.0980, "risk": "CRITICAL"},
    {"name": "Sultanpuri Central Commercial Market", "lat": 28.6924, "lon": 77.0815, "risk": "HIGH"},
    {"name": "Jahangirpuri Metro Corridor & K-Block", "lat": 28.7259, "lon": 77.1690, "risk": "CRITICAL"},
    {"name": "Badarpur Border Terminal Highway", "lat": 28.4980, "lon": 77.3015, "risk": "HIGH"}
]


def render_sos_emergency_sidebar_widget(
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    hotspots: Optional[List[Dict[str, Any]]] = None,
    height: int = 490
):
    """
    Renders the primary SOS EMERGENCY button at the top of the left sidebar.
    Operates 100% client-side with native Web Audio API, Notification API, and localStorage.
    """
    hotspots_data = hotspots or DEFAULT_HOTSPOTS_DATA
    initial_lat_js = f"{user_lat}" if user_lat is not None else "null"
    initial_lon_js = f"{user_lon}" if user_lon is not None else "null"
    hotspots_json = json.dumps(hotspots_data)

    sos_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
        }}
        body {{
            background: transparent;
            color: #f8fafc;
            overflow-x: hidden;
            padding: 2px 2px 14px 2px;
        }}

        .sos-container {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
            position: relative;
        }}

        /* Persistent In-Dashboard Alert Banner */
        .alert-banner {{
            display: none;
            background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #450a0a 100%);
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 10px 12px;
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.75);
            animation: bannerPulse 1.5s infinite alternate;
            flex-direction: column;
            gap: 6px;
        }}
        .alert-banner.active {{
            display: flex;
        }}
        @keyframes bannerPulse {{
            0% {{ box-shadow: 0 0 15px rgba(239, 68, 68, 0.6); border-color: #ef4444; }}
            100% {{ box-shadow: 0 0 30px rgba(239, 68, 68, 0.95); border-color: #fca5a5; }}
        }}
        .alert-banner-header {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 800;
            color: #fee2e2;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .alert-banner-text {{
            font-size: 11px;
            color: #f8fafc;
            line-height: 1.4;
            font-weight: 500;
        }}
        .alert-banner-link {{
            color: #fde047;
            font-family: monospace;
            font-size: 10.5px;
            text-decoration: underline;
            word-break: break-all;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .alert-banner-link:hover {{
            color: #ffffff;
        }}

        /* Button Action Group (SOS + Settings Icon) */
        .sos-button-group {{
            display: flex;
            align-items: stretch;
            gap: 6px;
            width: 100%;
        }}

        /* Primary Glowing SOS Emergency Button */
        .sos-main-btn {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 50%, #991b1b 100%);
            color: #ffffff;
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 12px 12px;
            border-radius: 12px;
            border: 2px solid #ef4444;
            cursor: pointer;
            box-shadow: 0 0 16px rgba(239, 68, 68, 0.6), inset 0 1px 2px rgba(255, 255, 255, 0.4);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            outline: none;
            user-select: none;
        }}
        .sos-main-btn:hover {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
            box-shadow: 0 0 24px rgba(239, 68, 68, 0.9), inset 0 1px 4px rgba(255, 255, 255, 0.6);
            transform: translateY(-1px);
        }}
        .sos-main-btn:active {{
            transform: scale(0.98);
        }}

        /* Visual Feedback: Animated Pulsing Red Ring / Glow while Emergency Alert is Active */
        .sos-main-btn.emergency-active {{
            background: linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #ef4444 100%) !important;
            border-color: #fca5a5 !important;
            animation: emergencyPulseRing 1.1s infinite alternate ease-in-out !important;
        }}
        @keyframes emergencyPulseRing {{
            0% {{
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.95), 0 0 16px rgba(239, 68, 68, 0.8), inset 0 0 8px rgba(255, 255, 255, 0.5);
                transform: scale(1);
            }}
            50% {{
                box-shadow: 0 0 0 9px rgba(239, 68, 68, 0.45), 0 0 32px rgba(239, 68, 68, 1), inset 0 0 16px rgba(255, 255, 255, 0.8);
                transform: scale(1.02);
            }}
            100% {{
                box-shadow: 0 0 0 18px rgba(239, 68, 68, 0), 0 0 46px rgba(255, 0, 0, 0.9), inset 0 0 12px rgba(255, 255, 255, 0.6);
                transform: scale(1);
            }}
        }}

        /* Settings Gear Icon Button Next to SOS Button */
        .sos-settings-btn {{
            width: 44px;
            background: rgba(15, 23, 42, 0.85);
            border: 1.5px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: #94a3b8;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            outline: none;
            backdrop-filter: blur(8px);
            flex-shrink: 0;
        }}
        .sos-settings-btn:hover {{
            background: rgba(30, 41, 59, 0.95);
            border-color: #38bdf8;
            color: #38bdf8;
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.35);
            transform: rotate(25deg);
        }}

        /* Visible Dismiss / Silence Alarm Button */
        .dismiss-alarm-btn {{
            display: none;
            width: 100%;
            background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
            color: #090d16;
            font-size: 11.5px;
            font-weight: 900;
            padding: 9px 12px;
            border-radius: 10px;
            border: 1.5px solid #fde047;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 0 18px rgba(234, 179, 8, 0.6);
            transition: all 0.2s;
            outline: none;
        }}
        .dismiss-alarm-btn.active {{
            display: block;
        }}
        .dismiss-alarm-btn:hover {{
            background: #facc15;
            box-shadow: 0 0 25px rgba(250, 204, 21, 0.9);
            transform: translateY(-1px);
        }}

        /* Secondary Status Drawer */
        .status-drawer {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 7px 10px;
            display: flex;
            flex-direction: column;
            gap: 5px;
            font-size: 10.5px;
        }}
        .status-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
        }}

        /* Status Badges */
        .badge-pill {{
            font-size: 9.5px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 9999px;
            text-transform: uppercase;
            font-family: monospace;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .badge-granted {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}
        .badge-blocked {{
            background: rgba(239, 68, 68, 0.25);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }}
        .badge-default {{
            background: rgba(234, 179, 8, 0.2);
            color: #facc15;
            border: 1px solid rgba(234, 179, 8, 0.4);
        }}
        .badge-safe {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .badge-danger {{
            background: rgba(239, 68, 68, 0.25);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.5);
            animation: pulseRedGlow 1s infinite;
        }}

        @keyframes pulseRedGlow {{
            0%, 100% {{ box-shadow: 0 0 6px rgba(239, 68, 68, 0.4); }}
            50% {{ box-shadow: 0 0 14px rgba(239, 68, 68, 0.8); }}
        }}

        /* Toast Notification */
        .toast-notification {{
            display: none;
            position: absolute;
            top: -4px;
            left: 0;
            right: 0;
            background: rgba(15, 23, 42, 0.98);
            border: 1.5px solid #10b981;
            border-radius: 10px;
            padding: 8px 10px;
            font-size: 11px;
            z-index: 10000;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.8);
            animation: toastSlide 0.25s ease-out;
        }}
        .toast-notification.warning {{
            border-color: #f59e0b;
        }}
        .toast-notification.error {{
            border-color: #ef4444;
        }}
        @keyframes toastSlide {{
            from {{ transform: translateY(-8px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        /* Emergency Contact Setup Modal */
        .modal-backdrop {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(6px);
            z-index: 99999;
            align-items: center;
            justify-content: center;
            padding: 10px;
        }}
        .modal-backdrop.active {{
            display: flex;
        }}
        .modal-window {{
            background: #0f172a;
            border: 1.5px solid #334155;
            border-radius: 14px;
            width: 100%;
            max-width: 320px;
            padding: 14px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.9);
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .modal-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 8px;
        }}
        .modal-title {{
            font-size: 12.5px;
            font-weight: 800;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .modal-close {{
            cursor: pointer;
            font-size: 15px;
            color: #94a3b8;
            padding: 2px 6px;
            border-radius: 4px;
            transition: all 0.15s;
        }}
        .modal-close:hover {{
            color: #ffffff;
            background: #334155;
        }}

        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .form-label {{
            font-size: 10px;
            font-weight: 700;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .modal-input {{
            width: 100%;
            background: #1e293b;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 7px 10px;
            color: #f8fafc;
            font-size: 11.5px;
            outline: none;
            transition: border-color 0.15s;
        }}
        .modal-input:focus {{
            border-color: #38bdf8;
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
        }}
        .modal-input.input-error {{
            border-color: #ef4444;
            background: rgba(239, 68, 68, 0.05);
        }}
        .error-message {{
            color: #f87171;
            font-size: 9.5px;
            display: none;
            font-weight: 600;
        }}

        .modal-btn-row {{
            display: flex;
            gap: 8px;
            margin-top: 4px;
        }}
        .btn-primary {{
            flex: 1;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 11.5px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn-primary:hover {{
            background: #3b82f6;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
        }}
        .btn-secondary {{
            background: #1e293b;
            color: #cbd5e1;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
        }}
        .btn-secondary:hover {{
            background: #334155;
            color: #ffffff;
        }}
    </style>
    </head>
    <body>

    <div class="sos-container">
        <!-- Floating Toast Notification -->
        <div id="sosToast" class="toast-notification">
            <div id="sosToastContent" style="color: #f8fafc; font-weight: 600;"></div>
        </div>

        <!-- Persistent In-Dashboard Alert Banner (Top of Interface) -->
        <div id="sosWidgetAlertBanner" class="alert-banner">
            <div class="alert-banner-header">
                <span>🚨 EMERGENCY ALERT TRIGGERED</span>
            </div>
            <div id="sosWidgetAlertText" class="alert-banner-text">
                EMERGENCY ALERT: Distress signal triggered for primary contact <strong id="bannerTargetName">--</strong> (<span id="bannerTargetEmail">--</span>) with current GPS coordinates.
            </div>
            <a id="bannerMapsLink" class="alert-banner-link" href="#" target="_blank" rel="noopener noreferrer">
                📍 Open Live Coordinates on Google Maps ↗
            </a>
            <button class="dismiss-alarm-btn active" style="margin-top: 4px;" onclick="stopEmergencyAlarm()">
                ⏹️ Dismiss / Silence Alarm
            </button>
        </div>

        <!-- 1. Primary Action Row: SOS EMERGENCY Button + Settings Gear Icon -->
        <div class="sos-button-group">
            <button id="sosButton" class="sos-main-btn" onclick="handleSosClick()" title="Trigger SOS Emergency Distress Alert">
                <span id="beaconIcon" style="font-size: 15px;">🚨</span>
                <span id="sosButtonLabel">SOS EMERGENCY</span>
                <span style="font-size: 13px;">🔔</span>
            </button>
            <button id="settingsBtn" class="sos-settings-btn" onclick="openContactModal()" title="Emergency Contact Setup & Permissions">
                ⚙️
            </button>
        </div>

        <!-- Visible Dismiss / Silence Alarm Button -->
        <button id="dismissAlarmBtn" class="dismiss-alarm-btn" onclick="stopEmergencyAlarm()">
            ⏹️ Dismiss / Silence Alarm
        </button>

        <!-- Status Drawer: Notification Permission & Contact Indicator -->
        <div class="status-drawer">
            <div class="status-row">
                <span style="color: #94a3b8;">App Notifications:</span>
                <span id="notifStatusBadge" class="badge-pill badge-default" onclick="requestNotificationPermission()">
                    Checking...
                </span>
            </div>
            <div class="status-row">
                <span style="color: #94a3b8;">Primary Contact:</span>
                <span id="contactDisplayPill" style="color: #38bdf8; font-weight: 700; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer;" onclick="openContactModal()">
                    Not Configured
                </span>
            </div>
            <div class="status-row">
                <span style="color: #94a3b8;">Zone Proximity:</span>
                <span id="proximityBadge" class="badge-pill badge-safe">Scanning GPS...</span>
            </div>
        </div>

        <!-- Geofence Proximity Simulator Buttons for Testing -->
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 9px; color: #64748b; padding: 0 2px;">
            <span>Simulate Geofence:</span>
            <div style="display: flex; gap: 4px;">
                <button onclick="simulateGeofence(55)" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; border-radius: 4px; padding: 2px 6px; cursor: pointer; font-size: 8.5px;">&lt;100m Hotspot</button>
                <button onclick="simulateGeofence(650)" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: #cbd5e1; border-radius: 4px; padding: 2px 6px; cursor: pointer; font-size: 8.5px;">Reset Safe</button>
            </div>
        </div>
    </div>

    <!-- 2. Emergency Contact Configuration Modal / Dialog -->
    <div id="contactModal" class="modal-backdrop">
        <div class="modal-window">
            <div class="modal-header">
                <span class="modal-title">🛡️ Emergency Contact Setup</span>
                <span class="modal-close" onclick="closeContactModal()">✕</span>
            </div>

            <div style="font-size: 10px; color: #94a3b8; line-height: 1.35;">
                Configure your verified primary emergency contact. When SOS is triggered, distress notifications and coordinate links will be targeted to this contact completely client-side.
            </div>

            <!-- Intercept Warning Banner inside Modal (Shown when triggered via intercept) -->
            <div id="interceptBanner" style="display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 6px 8px; color: #fca5a5; font-size: 10px; font-weight: 600;">
                ⚠️ Please save a primary contact before triggering an emergency alert!
            </div>

            <!-- Contact Name Field -->
            <div class="form-group">
                <label class="form-label" for="inputContactName">Primary Contact Name *</label>
                <input id="inputContactName" class="modal-input" placeholder="e.g. Inspector Sharma / Guardian" autocomplete="name" />
                <div id="nameError" class="error-message">Contact name is required.</div>
            </div>

            <!-- Contact Email Field -->
            <div class="form-group">
                <label class="form-label" for="inputContactEmail">Primary Contact Email *</label>
                <input id="inputContactEmail" class="modal-input" type="email" placeholder="e.g. emergency@contact.com" autocomplete="email" />
                <div id="emailError" class="error-message">Please enter a valid email address.</div>
            </div>

            <!-- Notification Permission Trigger within Modal -->
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 8px; padding: 7px 8px; display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 10px; color: #cbd5e1;">
                    Browser Notifications:
                </div>
                <button type="button" onclick="requestNotificationPermission()" style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; border-radius: 6px; padding: 3px 8px; font-size: 9.5px; font-weight: 700; cursor: pointer;">
                    Request Permission
                </button>
            </div>

            <div class="modal-btn-row">
                <button id="btnSaveContact" class="btn-primary" onclick="handleSaveOrUpdateContact()">
                    Save Contact
                </button>
                <button class="btn-secondary" onclick="closeContactModal()">
                    Cancel
                </button>
            </div>
        </div>
    </div>

    <script>
    // ------------------------------------------------------------------------
    // STATE & LOCAL STORAGE PERSISTENCE
    // ------------------------------------------------------------------------
    const HOTSPOTS = {hotspots_json};
    let currentLat = {initial_lat_js};
    let currentLon = {initial_lon_js};
    let isWithin100m = false;
    let isAlarmActive = false;
    let audioContext = null;
    let toneInterval = null;

    // Shield icon as an embedded SVG data URI (Guaranteed 100% offline & client-side)
    const SHIELD_ICON_DATA_URI = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ef4444'%3E%3Cpath d='M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z'/%3E%3C/svg%3E";

    function getStoredPrimaryContact() {{
        try {{
            const stored = localStorage.getItem("rakshak_primary_contact");
            if (stored) {{
                const parsed = JSON.parse(stored);
                if (parsed && parsed.name && parsed.email) {{
                    return parsed;
                }}
            }}
        }} catch (e) {{
            console.warn("localStorage read note:", e);
        }}
        return null;
    }}

    function storePrimaryContact(contact) {{
        try {{
            localStorage.setItem("rakshak_primary_contact", JSON.stringify(contact));
        }} catch (e) {{
            console.error("localStorage write error:", e);
        }}
    }}

    function isValidEmail(email) {{
        const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
        return re.test(String(email).toLowerCase());
    }}

    function updateContactUI() {{
        const contact = getStoredPrimaryContact();
        const displayPill = document.getElementById("contactDisplayPill");
        const modalBtn = document.getElementById("btnSaveContact");
        const nameInput = document.getElementById("inputContactName");
        const emailInput = document.getElementById("inputContactEmail");

        if (contact) {{
            if (displayPill) {{
                displayPill.innerText = `${{contact.name}} (${{contact.email}})`;
                displayPill.title = `Primary Contact: ${{contact.name}} <${{contact.email}}> (Click to edit)`;
                displayPill.style.color = "#38bdf8";
            }}
            if (modalBtn) {{
                modalBtn.innerText = "Update Contact";
            }}
            if (nameInput && !nameInput.value) nameInput.value = contact.name;
            if (emailInput && !emailInput.value) emailInput.value = contact.email;
        }} else {{
            if (displayPill) {{
                displayPill.innerText = "⚠️ Not Configured";
                displayPill.title = "Click to setup Primary Emergency Contact";
                displayPill.style.color = "#facc15";
            }}
            if (modalBtn) {{
                modalBtn.innerText = "Save Contact";
            }}
        }}

        updateNotificationBadge();
    }}

    // ------------------------------------------------------------------------
    // BROWSER NOTIFICATION PERMISSION FLOW & BADGE
    // ------------------------------------------------------------------------
    function updateNotificationBadge() {{
        const badge = document.getElementById("notifStatusBadge");
        if (!badge) return;

        if (!("Notification" in window)) {{
            badge.className = "badge-pill badge-blocked";
            badge.innerText = "❌ Not Supported";
            return;
        }}

        const permission = Notification.permission;
        if (permission === "granted") {{
            badge.className = "badge-pill badge-granted";
            badge.innerText = "🟢 Granted";
            badge.title = "Browser notifications enabled";
        }} else if (permission === "denied") {{
            badge.className = "badge-pill badge-blocked";
            badge.innerText = "🔴 Blocked";
            badge.title = "Browser notifications are blocked in browser settings";
        }} else {{
            badge.className = "badge-pill badge-default";
            badge.innerText = "🟡 Default / Allow";
            badge.title = "Click to grant browser notification permission";
        }}
    }}

    async function requestNotificationPermission() {{
        if (!("Notification" in window)) {{
            showToast("ℹ️ Notifications are not supported in this browser.", "warning");
            return;
        }}

        try {{
            const permission = await Notification.requestPermission();
            updateNotificationBadge();
            if (permission === "granted") {{
                showToast("✅ Browser notification permission granted!", "success");
            }} else if (permission === "denied") {{
                showToast("⚠️ Browser notifications were blocked.", "warning");
            }}
        }} catch (e) {{
            console.error("Permission request error:", e);
        }}
    }}

    // ------------------------------------------------------------------------
    // CONTACT CONFIGURATION MODAL
    // ------------------------------------------------------------------------
    function openContactModal(fromIntercept = false) {{
        const modal = document.getElementById("contactModal");
        const interceptBanner = document.getElementById("interceptBanner");
        const nameInput = document.getElementById("inputContactName");
        const emailInput = document.getElementById("inputContactEmail");
        const nameErr = document.getElementById("nameError");
        const emailErr = document.getElementById("emailError");

        if (nameErr) nameErr.style.display = "none";
        if (emailErr) emailErr.style.display = "none";
        if (nameInput) nameInput.classList.remove("input-error");
        if (emailInput) emailInput.classList.remove("input-error");

        const contact = getStoredPrimaryContact();
        if (contact) {{
            if (nameInput) nameInput.value = contact.name;
            if (emailInput) emailInput.value = contact.email;
        }}

        if (interceptBanner) {{
            interceptBanner.style.display = fromIntercept ? "block" : "none";
        }}

        if (modal) modal.classList.add("active");
        if (nameInput) setTimeout(() => nameInput.focus(), 100);

        // Request notification permission during setup if still default
        if ("Notification" in window && Notification.permission === "default") {{
            Notification.requestPermission().then(() => updateNotificationBadge()).catch(() => {{}});
        }}
    }}

    function closeContactModal() {{
        const modal = document.getElementById("contactModal");
        if (modal) modal.classList.remove("active");
    }}

    function handleSaveOrUpdateContact() {{
        const nameInput = document.getElementById("inputContactName");
        const emailInput = document.getElementById("inputContactEmail");
        const nameErr = document.getElementById("nameError");
        const emailErr = document.getElementById("emailError");

        const name = nameInput ? nameInput.value.trim() : "";
        const email = emailInput ? emailInput.value.trim() : "";

        let valid = true;
        if (!name) {{
            if (nameErr) nameErr.style.display = "block";
            if (nameInput) nameInput.classList.add("input-error");
            valid = false;
        }} else {{
            if (nameErr) nameErr.style.display = "none";
            if (nameInput) nameInput.classList.remove("input-error");
        }}

        if (!email || !isValidEmail(email)) {{
            if (emailErr) emailErr.style.display = "block";
            if (emailInput) emailInput.classList.add("input-error");
            valid = false;
        }} else {{
            if (emailErr) emailErr.style.display = "none";
            if (emailInput) emailInput.classList.remove("input-error");
        }}

        if (!valid) return;

        const isUpdate = !!getStoredPrimaryContact();
        const contactData = {{ name, email }};
        storePrimaryContact(contactData);
        updateContactUI();
        closeContactModal();

        // Prompt notification permission if not yet granted
        if ("Notification" in window && Notification.permission === "default") {{
            Notification.requestPermission().then(() => updateNotificationBadge()).catch(() => {{}});
        }}

        showToast(
            isUpdate ? `✅ Primary Contact updated: ${{name}}` : `✅ Primary Contact saved: ${{name}}`,
            "success"
        );
    }}

    // ------------------------------------------------------------------------
    // WEB AUDIO API PULSING EMERGENCY BEEP (880Hz alternating with 1200Hz)
    // ------------------------------------------------------------------------
    function startEmergencyAlarm() {{
        try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;

            if (!audioContext) {{
                audioContext = new AudioCtx();
            }}
            if (audioContext.state === "suspended") {{
                audioContext.resume();
            }}

            stopEmergencyToneOnly();
            isAlarmActive = true;

            let isHighTone = false;
            toneInterval = setInterval(() => {{
                if (!isAlarmActive || !audioContext) return;
                try {{
                    const osc = audioContext.createOscillator();
                    const gain = audioContext.createGain();

                    // Continuous pulsing emergency beep alternating rapidly between 880Hz and 1200Hz
                    const freq = isHighTone ? 1200 : 880;
                    isHighTone = !isHighTone;

                    osc.type = "sawtooth";
                    osc.frequency.setValueAtTime(freq, audioContext.currentTime);

                    gain.gain.setValueAtTime(0.35, audioContext.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.16);

                    osc.connect(gain);
                    gain.connect(audioContext.destination);

                    osc.start(audioContext.currentTime);
                    osc.stop(audioContext.currentTime + 0.17);
                }} catch (err) {{
                    console.warn("Oscillator tick error:", err);
                }}
            }}, 180);
        }} catch (e) {{
            console.warn("AudioContext error:", e);
        }}
    }}

    function stopEmergencyToneOnly() {{
        if (toneInterval) {{
            clearInterval(toneInterval);
            toneInterval = null;
        }}
    }}

    function stopEmergencyAlarm() {{
        isAlarmActive = false;
        stopEmergencyToneOnly();

        // Visual feedback reset
        const sosBtn = document.getElementById("sosButton");
        const btnLabel = document.getElementById("sosButtonLabel");
        const dismissBtn = document.getElementById("dismissAlarmBtn");
        const inWidgetBanner = document.getElementById("sosWidgetAlertBanner");

        if (sosBtn) {{
            sosBtn.classList.remove("emergency-active");
        }}
        if (btnLabel) {{
            btnLabel.innerText = isWithin100m ? "🚨 HIGH RISK (<100m)" : "SOS EMERGENCY";
        }}
        if (dismissBtn) {{
            dismissBtn.classList.remove("active");
        }}
        if (inWidgetBanner) {{
            inWidgetBanner.classList.remove("active");
        }}

        // Remove persistent banner in parent dashboard if injected
        try {{
            if (window.parent && window.parent.document) {{
                const pBanner = window.parent.document.getElementById("rakshakGlobalSosBanner");
                if (pBanner) pBanner.remove();
            }}
        }} catch (e) {{}}

        showToast("🔇 Emergency alarm silenced.", "success");
    }}

    // ------------------------------------------------------------------------
    // IN-DASHBOARD PERSISTENT ALERT BANNER
    // ------------------------------------------------------------------------
    function renderAlertBanners(contact, lat, lng) {{
        const mapsUrl = `https://www.google.com/maps?q=${{lat.toFixed(5)}},${{lng.toFixed(5)}}`;
        const alertMsg = `EMERGENCY ALERT: Distress signal triggered for primary contact ${{contact.name}} (${{contact.email}}) with current GPS coordinates.`;

        // 1. In-Widget Persistent Banner
        const inWidgetBanner = document.getElementById("sosWidgetAlertBanner");
        const targetName = document.getElementById("bannerTargetName");
        const targetEmail = document.getElementById("bannerTargetEmail");
        const bannerLink = document.getElementById("bannerMapsLink");

        if (targetName) targetName.innerText = contact.name;
        if (targetEmail) targetEmail.innerText = contact.email;
        if (bannerLink) {{
            bannerLink.href = mapsUrl;
            bannerLink.innerText = `📍 Open Live GPS on Google Maps (${{lat.toFixed(4)}}, ${{lng.toFixed(4)}}) ↗`;
        }}
        if (inWidgetBanner) {{
            inWidgetBanner.classList.add("active");
        }}

        // 2. High-Priority Persistent Alert Banner across top of the interface (Parent DOM Injection)
        try {{
            if (window.parent && window.parent.document) {{
                let pBanner = window.parent.document.getElementById("rakshakGlobalSosBanner");
                if (!pBanner) {{
                    pBanner = window.parent.document.createElement("div");
                    pBanner.id = "rakshakGlobalSosBanner";
                    window.parent.document.body.prepend(pBanner);
                }}

                pBanner.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    z-index: 99999999;
                    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 50%, #991b1b 100%);
                    color: #ffffff;
                    padding: 10px 18px;
                    border-bottom: 3px solid #f87171;
                    box-shadow: 0 4px 30px rgba(220, 38, 38, 0.95);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 13px;
                    font-weight: 700;
                    gap: 12px;
                    box-sizing: border-box;
                `;

                pBanner.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1; flex-wrap: wrap;">
                        <span style="font-size: 18px;">🚨</span>
                        <span>${{alertMsg}}</span>
                        <a href="${{mapsUrl}}" target="_blank" rel="noopener noreferrer" style="color: #fef08a; background: rgba(0,0,0,0.3); padding: 3px 10px; border-radius: 6px; text-decoration: underline; font-family: monospace; font-size: 12px; display: inline-flex; align-items: center; gap: 4px;">
                            📍 ${{mapsUrl}} ↗
                        </a>
                    </div>
                    <button id="btnParentSilenceAlarm" style="background: #ffffff; color: #991b1b; border: none; font-weight: 900; font-size: 12px; padding: 6px 14px; border-radius: 8px; cursor: pointer; text-transform: uppercase; letter-spacing: 0.05em; box-shadow: 0 2px 8px rgba(0,0,0,0.3); white-space: nowrap;">
                        ⏹️ Dismiss / Silence Alarm
                    </button>
                `;

                const pBtn = pBanner.querySelector("#btnParentSilenceAlarm");
                if (pBtn) {{
                    pBtn.onclick = () => stopEmergencyAlarm();
                }}
            }}
        }} catch (err) {{
            console.log("Parent window banner note:", err);
        }}
    }}

    // ------------------------------------------------------------------------
    // NATIVE BROWSER NOTIFICATION TRIGGER
    // ------------------------------------------------------------------------
    function triggerNativeNotification(contact, lat, lng) {{
        if (!("Notification" in window)) return;

        const notifTitle = "EMERGENCY SOS: Help Needed!";
        const notifOptions = {{
            body: `Alert for ${{contact.name}} (${{contact.email}}): The user is in an active danger zone! Lat: ${{lat.toFixed(5)}}, Lng: ${{lng.toFixed(5)}}`,
            icon: SHIELD_ICON_DATA_URI,
            requireInteraction: true,
            tag: "sos-alert"
        }};

        if (Notification.permission === "granted") {{
            try {{
                new Notification(notifTitle, notifOptions);
            }} catch (e) {{
                console.warn("Notification instance error:", e);
            }}
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(perm => {{
                updateNotificationBadge();
                if (perm === "granted") {{
                    try {{
                        new Notification(notifTitle, notifOptions);
                    }} catch (e) {{}}
                }}
            }});
        }}
    }}

    // ------------------------------------------------------------------------
    // PRIMARY SOS BUTTON CLICK HANDLER & INTERCEPT FLOW
    // ------------------------------------------------------------------------
    async function handleSosClick() {{
        // If alarm is already sounding, tapping dismisses it
        if (isAlarmActive) {{
            stopEmergencyAlarm();
            return;
        }}

        // Intercept Rule: If a user clicks SOS before saving a primary contact, intercept and open modal first
        const contact = getStoredPrimaryContact();
        if (!contact || !contact.name || !contact.email) {{
            showToast("⚠️ Configure your Primary Emergency Contact first!", "warning");
            openContactModal(true);
            return;
        }}

        // Start Safety Beep Audio immediately inside onClick event handler to comply with autoplay policy
        startEmergencyAlarm();

        // Coordinates resolution
        const lat = currentLat || 28.6328;
        const lng = currentLon || 77.2197;

        // Visual Feedback: Animated pulsing red ring / glow around the sidebar SOS button
        const sosBtn = document.getElementById("sosButton");
        const btnLabel = document.getElementById("sosButtonLabel");
        const dismissBtn = document.getElementById("dismissAlarmBtn");

        if (sosBtn) {{
            sosBtn.classList.add("emergency-active");
        }}
        if (btnLabel) {{
            btnLabel.innerText = "🔊 ALARM ACTIVE - DISMISS";
        }}
        if (dismissBtn) {{
            dismissBtn.classList.add("active");
        }}

        // Trigger Native Browser Notification
        triggerNativeNotification(contact, lat, lng);

        // Render In-Dashboard High-Priority Alert Banners
        renderAlertBanners(contact, lat, lng);

        showToast(
            `🚨 Distress Signal Triggered for ${{contact.name}} (${{contact.email}})!`,
            "success"
        );
    }}

    // ------------------------------------------------------------------------
    // HAVERSINE PROXIMITY & GEOFENCE EVALUATION
    // ------------------------------------------------------------------------
    function haversineMeters(lat1, lon1, lat2, lon2) {{
        const R = 6371000;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }}

    function evaluateProximity(lat, lon) {{
        if (!lat || !lon) return;
        currentLat = lat;
        currentLon = lon;

        let minD = Infinity;
        let spot = null;

        HOTSPOTS.forEach(h => {{
            const d = haversineMeters(lat, lon, h.lat, h.lon);
            if (d < minD) {{
                minD = d;
                spot = h;
            }}
        }});

        const badge = document.getElementById("proximityBadge");
        const btn = document.getElementById("sosButton");
        const btnLabel = document.getElementById("sosButtonLabel");

        if (minD <= 100) {{
            isWithin100m = true;
            if (badge) {{
                badge.className = "badge-pill badge-danger";
                badge.innerText = `HIGH RISK (${{Math.round(minD)}}m)`;
            }}
            if (btn && !isAlarmActive) {{
                btn.classList.add("high-risk");
            }}
            if (btnLabel && !isAlarmActive) {{
                btnLabel.innerText = "🚨 HIGH RISK (<100m)";
            }}
        }} else {{
            isWithin100m = false;
            if (badge) {{
                badge.className = "badge-pill badge-safe";
                badge.innerText = minD < 1000 ? `${{Math.round(minD)}}m Buffer` : `${{(minD/1000).toFixed(1)}}km Safe`;
            }}
            if (btn && !isAlarmActive) {{
                btn.classList.remove("high-risk");
            }}
            if (btnLabel && !isAlarmActive) {{
                btnLabel.innerText = "SOS EMERGENCY";
            }}
        }}
    }}

    function simulateGeofence(meters) {{
        const refLat = 28.6328;
        const refLon = 77.2197;
        evaluateProximity(refLat + (meters / 111000), refLon);
    }}

    function showToast(message, type = "success") {{
        const toast = document.getElementById("sosToast");
        const content = document.getElementById("sosToastContent");
        if (!toast || !content) return;

        content.innerHTML = message;
        toast.className = "toast-notification" + (type === "warning" ? " warning" : type === "error" ? " error" : "");
        toast.style.display = "block";

        setTimeout(() => {{
            toast.style.display = "none";
        }}, 4500);
    }}

    // Initialization on DOM Ready
    window.addEventListener("DOMContentLoaded", () => {{
        updateContactUI();
        if (currentLat && currentLon) {{
            evaluateProximity(currentLat, currentLon);
        }}
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(
                pos => evaluateProximity(pos.coords.latitude, pos.coords.longitude),
                err => {{ if (currentLat && currentLon) evaluateProximity(currentLat, currentLon); }},
                {{ enableHighAccuracy: true, timeout: 8000 }}
            );
        }}
    }});
    </script>

    </body>
    </html>
    """

    components.html(sos_html, height=height)
