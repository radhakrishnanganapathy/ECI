import streamlit as st
import pandas as pd
from database import init_db, get_db, User, Alliance, Party, Candidate, ElectionStat, AllianceParty, Constituency, OpinionPoll, OpinionPollOption, PollVote, hash_password, verify_password
from sqlalchemy.orm import Session
import os
import base64
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ECI Election Stats Dashboard",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLE ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(0, 0, 0) 0%, rgb(24, 24, 24) 90.2%);
        color: #ffffff;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #00d4ff;
        font-family: 'Outfit', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00d4ff, #0055ff);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- DB INIT ---
try:
    init_db()
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.info("Make sure your PostgreSQL server is running and credentials are correct in database.py")
    st.stop()

# --- SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

# --- TRANSLATIONS ---
LANGUAGES = {
    "English": {
        "dashboard": "🚀 Election Dashboard",
        "alliances": "🤝 Alliances",
        "parties": "🚩 Political Parties",
        "constituencies": "� Constituencies",
        "candidates": "� Candidates",
        "election_stats": "� Election Stats",
        "admin_panel": "🛠️ Admin Panel",
        "logout": "Logout",
        "logged_in_as": "Logged in as",
        "view": "View",
        "grid": "Grid",
        "list": "List",
        "add_new": "Add New",
        "edit": "✏️ Edit",
        "delete": "🗑️ Delete",
        "save": "Save",
        "cancel": "Cancel",
        "name": "Name",
        "full_name": "Full Name",
        "leader": "Leader",
        "symbol": "Symbol",
        "description": "Description",
        "constituency": "Constituency",
        "district": "District",
        "bio": "Bio",
        "primary_party": "Primary Party",
        "seats": "Seats Contested",
        "filter_by_alliance": "Filter by Alliance",
        "all": "All",
        "election_type": "Election Type",
        "state": "State",
        "center": "Center",
        "election_year": "Election Year",
        "seats_sharing": "Seat Sharing",
        "seats_sharing_tn": "Seat Sharing (TN)",
        "seats_sharing_py": "Seat Sharing (PY)",
        "view_details": "View Full Details",
        "alliance_details": "Alliance Member Details",
        "add_member": "Add Alliance Member",
        "select_party": "Select Party",
        "symbol_name": "Symbol Name",
        "state": "State",
        "tn": "Tamil Nadu",
        "py": "Pondicherry",
        "ind": "India",
        "total_voters": "Total Voters",
        "male": "Male",
        "female": "Female",
        "reserved": "Reserved",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "other": "Other",
        "election_link": "Election Link",
        "opinion_poll": "📊 Opinion Poll",
        "duration": "Duration (Days)",
        "start_poll": "Start Poll",
        "stop_poll": "Stop Poll",
        "display_dashboard": "Display on Dashboard",
        "hide_dashboard": "Hide on Dashboard",
        "vote": "Vote",
        "voted_successfully": "Voted successfully!",
        "already_voted": "You have already voted from this device.",
        "candidate_growth": "Recent Candidate Growth",
        "cumulative_candidates": "Cumulative Candidates",
        "category": "Category"
    },
    "Tamil": {
        "dashboard": "🚀 தேர்தல் டேஷ்போர்டு",
        "alliances": "🤝 கூட்டணிகள்",
        "parties": "🚩 அரசியல் கட்சிகள்",
        "constituencies": "� தொகுதிகள்",
        "candidates": "� வேட்பாளர்கள்",
        "election_stats": "� தேர்தல் புள்ளிவிவரங்கள்",
        "admin_panel": "🛠️ நிர்வாக குழு",
        "logout": "வெளியேறு",
        "logged_in_as": "உள்நுழைந்துள்ளவர்",
        "view": "பார்வை",
        "grid": "கட்டம்",
        "list": "பட்டியல்",
        "add_new": "புதியதைச் சேர்",
        "edit": "✏️ திருத்து",
        "delete": "🗑️ நீக்கு",
        "save": "சேமி",
        "cancel": "ரத்துசெய்",
        "name": "பெயர்",
        "full_name": "முழு பெயர்",
        "leader": "தலைவர்",
        "symbol": "சின்னம்",
        "description": "விளக்கம்",
        "constituency": "தொகுதி",
        "district": "மாவட்டம்",
        "bio": "சுயசரிதை",
        "primary_party": "முதன்மை கட்சி",
        "seats": "போட்டியிட்ட இடங்கள்",
        "filter_by_alliance": "கூட்டணி மூலம் வடிகட்டவும்",
        "all": "அனைத்தும்",
        "election_type": "தேர்தல் வகை",
        "state": "மாநிலம்",
        "center": "மத்திய",
        "election_year": "தேர்தல் ஆண்டு",
        "seats_sharing": "இடப் பங்கீடு",
        "seats_sharing_tn": "இடப் பங்கீடு (தமிழ்நாடு)",
        "seats_sharing_py": "இடப் பங்கீடு (புதுச்சேரி)",
        "view_details": "முழு விவரங்களைப் பார்க்கவும்",
        "alliance_details": "கூட்டணி உறுப்பினர் விவரங்கள்",
        "add_member": "கூட்டணி உறுப்பினரைச் சேர்க்கவும்",
        "select_party": "கட்சியைத் தேர்ந்தெடுக்கவும்",
        "symbol_name": "சின்னம் பெயர்",
        "state": "மாநிலம்",
        "tn": "தமிழ்நாடு",
        "py": "புதுச்சேரி",
        "ind": "இந்தியா",
        "total_voters": "மொத்த வாக்காளர்கள்",
        "male": "ஆண்",
        "female": "பெண்",
        "reserved": "தனி",
        "gender": "பாலினம்",
        "male": "ஆண்",
        "female": "பெண்",
        "other": "மற்றவை",
        "election_link": "தேர்தல் இணைப்பு",
        "opinion_poll": "📊 கருத்துக்கணிப்பு",
        "duration": "கால அளவு (நாட்கள்)",
        "start_poll": "வாக்கெடுப்பைத் தொடங்கு",
        "stop_poll": "வாக்கெடுப்பை நிறுத்து",
        "display_dashboard": "டேஷ்போர்டில் காண்பி",
        "hide_dashboard": "டேஷ்போர்டில் மறை",
        "vote": "வாக்களி",
        "voted_successfully": "வெற்றிகரமாக வாக்களிக்கப்பட்டது!",
        "already_voted": "இந்த சாதனத்திலிருந்து நீங்கள் ஏற்கனவே வாக்களித்துவிட்டீர்கள்.",
        "candidate_growth": "சமீபத்திய வேட்பாளர் வளர்ச்சி",
        "cumulative_candidates": "மொத்த வேட்பாளர்கள்",
        "category": "வகை"
    },
}

if 'lang' not in st.session_state:
    st.session_state.lang = "English"

if "viewing_alliance_id" not in st.session_state:
    st.session_state.viewing_alliance_id = None

def t(key):
    return LANGUAGES[st.session_state.lang].get(key, key)

def get_val(obj, field):
    if st.session_state.lang == "Tamil":
        ta_val = getattr(obj, f"{field}_ta", None)
        if ta_val: return ta_val
    return getattr(obj, field, "")

def image_to_base64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

st.image_url_to_base64 = image_to_base64  # Monkeypatching for easy access in f-strings if needed or just use it directly

# --- MAIN APP LOGIC ---

# Language Selector (Top of Sidebar)
st.sidebar.markdown(f"### 🌐 Language / மொழி")
st.session_state.lang = st.sidebar.selectbox("Select Language", ["English", "Tamil"], index=0 if st.session_state.lang == "English" else 1, label_visibility="collapsed")
st.sidebar.divider()

# User Section (Login or Info)
user = st.session_state.user
if user is None:
    with st.sidebar.expander("👤 Login / Sign Up"):
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        with login_tab:
            l_user = st.text_input("Username", key="sidebar_l_user")
            l_pass = st.text_input("Password", type="password", key="sidebar_l_pass")
            if st.button("Login", key="sidebar_l_btn"):
                db = next(get_db())
                auth_user = db.query(User).filter(User.username == l_user).first()
                if auth_user and verify_password(l_pass, auth_user.password_hash):
                    st.session_state.user = {"username": auth_user.username, "role": auth_user.role, "id": auth_user.id}
                    st.success("Logged in!")
                    st.rerun()
                else: st.error("Invalid credentials")
        with signup_tab:
            s_user = st.text_input("Username", key="sidebar_s_user")
            s_pass = st.text_input("Password", type="password", key="sidebar_s_pass")
            if st.button("Register", key="sidebar_s_btn"):
                db = next(get_db())
                if db.query(User).filter(User.username == s_user).first(): st.error("Exists")
                else:
                    new_u = User(username=s_user, password_hash=hash_password(s_pass), role="user")
                    db.add(new_u); db.commit()
                    st.success("Created! Please login.")
else:
    if user:
        st.sidebar.success(f"{t('logged_in_as')}: {user['username']} ({user['role']})")
        if st.sidebar.button(t("logout")):
            logout()
st.sidebar.divider()

# Navigation
menu_options = [t("dashboard"), t("alliances"), t("parties"), t("constituencies"), t("candidates"), t("election_stats")]
if user and user['role'] == 'admin':
    menu_options.append(t("opinion_poll"))
    menu_options.append(t("admin_panel"))
    
choice = st.sidebar.selectbox("Navigate", menu_options)

if choice != t("alliances"):
    st.session_state.viewing_alliance_id = None
if choice == t("dashboard"):
    st.title(t("dashboard"))
    
    # Summary Stats
    db = next(get_db())
    total_alliances = db.query(Alliance).count()
    total_parties = db.query(Party).count()
    total_candidates = db.query(Candidate).count()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="glass-card"><h3>{t("alliances")}</h3><h1>{total_alliances}</h1></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h3>{t("parties")}</h3><h1>{total_parties}</h1></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="glass-card"><h3>{t("candidates")}</h3><h1>{total_candidates}</h1></div>', unsafe_allow_html=True)
        
    # --- Opinion Poll Display on Dashboard ---
    db = next(get_db())
    active_poll = db.query(OpinionPoll).filter(OpinionPoll.show_on_dashboard == 1, OpinionPoll.is_active == 1).first()
    if active_poll:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        # Calculate remaining time
        remaining_str = ""
        try:
            end_dt = datetime.fromisoformat(active_poll.end_datetime)
            now = datetime.now()
            rem = end_dt - now
            if rem.total_seconds() > 0:
                days = rem.days
                hours = rem.seconds // 3600
                mins = (rem.seconds % 3600) // 60
                if days > 0: 
                    remaining_str = f"⏳ {days}d {hours}h remaining"
                elif hours > 0:
                    remaining_str = f"⏳ {hours}h {mins}m remaining"
                else:
                    remaining_str = f"⏳ {mins}m remaining"
            else:
                remaining_str = "⌛ Poll Ended"
        except: pass

        st.subheader(f"📊 {active_poll.title}")
        if remaining_str: st.markdown(f"**{remaining_str}**")
        
        # IP Check using modern st.context if available
        client_ip = "127.0.0.1" 
        try:
            # Try new method first
            if hasattr(st, "context") and hasattr(st.context, "headers"):
                headers = st.context.headers
            else:
                # Fallback to deprecated method
                from streamlit.web.server.websocket_headers import _get_websocket_headers
                headers = _get_websocket_headers()
            
            if headers:
                client_ip = headers.get("X-Forwarded-For", headers.get("Remote-Addr", "127.0.0.1")).split(',')[0].strip()
        except: pass
        
        has_voted = db.query(PollVote).filter(PollVote.poll_id == active_poll.id, PollVote.ip_address == client_ip).first()
        
        options = active_poll.options
        if not options:
            st.info("No options available for this poll.")
        else:
            if has_voted:
                st.info(t("already_voted"))
                # Show results as bar chart
                result_data = []
                for opt in options:
                    v_count = db.query(PollVote).filter(PollVote.option_id == opt.id).count()
                    result_data.append({"Party": opt.name, "Votes": v_count, "Color": opt.color, "Symbol": opt.symbol_image_url})
                
                df_res = pd.DataFrame(result_data)
                
                # Use a custom HTML/CSS visualization for the bars with symbols at the bottom
                st.write("**Live Results**")
                cols = st.columns(len(options))
                max_votes = df_res['Votes'].max() or 1
                
                for i, opt in enumerate(result_data):
                    with cols[i]:
                        # Bar height relative to max votes
                        height = (opt['Votes'] / max_votes) * 200 # max 200px
                        st.markdown(f"""
                            <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 250px;">
                                <div style="color: white; font-weight: bold; margin-bottom: 5px;">{opt['Votes']}</div>
                                <div style="background: {opt['Color']}; width: 60px; height: {height}px; border-radius: 5px 5px 0 0; box-shadow: 0 0 10px {opt['Color']}66;"></div>
                                <div style="margin-top: 10px; width: 50px; height: 50px; border-radius: 50%; overflow: hidden; background: white; padding: 2px;">
                                    <img src="data:image/png;base64,{base64.b64encode(open(opt['Symbol'], 'rb').read()).decode() if opt['Symbol'] and os.path.exists(opt['Symbol']) else ''}" style="width: 100%; height: 100%; object-fit: contain;">
                                </div>
                                <div style="font-size: 0.8em; text-align: center; margin-top: 5px; color: #aaa;">{opt['Party']}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("Cast your vote:")
                vcols = st.columns(len(options))
                for i, opt in enumerate(options):
                    with vcols[i]:
                        if opt.symbol_image_url and os.path.exists(opt.symbol_image_url):
                            st.image(opt.symbol_image_url, width=80)
                        st.write(f"**{opt.name}**")
                        if st.button(t("vote"), key=f"vote_opt_{opt.id}"):
                            from datetime import datetime
                            new_vote = PollVote(poll_id=active_poll.id, option_id=opt.id, ip_address=client_ip, voted_at=str(datetime.now()))
                            db.add(new_vote)
                            db.commit()
                            st.success(t("voted_successfully"))
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == t("alliances"):
    db = next(get_db())
    # DEBUG: Removed in next step
    # st.write(f"DEBUG: Entered Alliances Block. Choice: {choice}")
    
    if st.session_state.viewing_alliance_id is not None:
        a_id = st.session_state.viewing_alliance_id
        alliance = db.query(Alliance).filter(Alliance.id == a_id).first()
        
        if alliance:
            detail_col1, detail_col2 = st.columns([5, 1])
        else:
            st.error("Alliance not found.")
            st.session_state.viewing_alliance_id = None
            st.rerun()
            
        if alliance:
            with detail_col1:
                if st.button("⬅️ " + t("alliances")):
                    st.session_state.viewing_alliance_id = None
                    st.rerun()
            
            if user and user['role'] == 'admin':
                with detail_col2:
                    if st.button("➕", key="add_mem_btn"):
                        st.session_state.show_add_member = True
            
            short_n = get_val(alliance, 'name')
            full_n = get_val(alliance, 'full_name')
            disp_name = f"{short_n} ({full_n})" if full_n else short_n
            
            st.title(f"{alliance.symbol if alliance.symbol else '🤝'} {disp_name}")
            st.subheader(t("alliance_details"))
            
            # Form to add member
            if user and user['role'] == 'admin' and st.session_state.get('show_add_member', False):
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(t("add_member"))
                all_parties = db.query(Party).all()
                
                with st.form("add_alliance_member_form"):
                    p_options = {p.name: p.id for p in all_parties}
                    sel_p_name = st.selectbox(t("select_party"), list(p_options.keys()))
                    
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        m_seats_tn = st.number_input(t("seats_sharing_tn"), min_value=0, step=1)
                        m_seats_py = st.number_input(t("seats_sharing_py"), min_value=0, step=1)
                        m_sym_name = st.text_input(f"{t('symbol_name')} (EN)")
                    with m_col2:
                        m_sym_img = st.file_uploader(f"Upload {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                        m_sym_name_ta = st.text_input(f"{t('symbol_name')} (TA)")
                    
                    mbc1, mbc2 = st.columns([1, 5])
                    if mbc1.form_submit_button(t("save")):
                        img_path = None
                        if m_sym_img:
                            if not os.path.exists("images"): os.makedirs("images")
                            img_path = f"images/mem_sym_{m_sym_img.name}"
                            with open(img_path, "wb") as f: f.write(m_sym_img.getbuffer())
                        
                        new_mem = AllianceParty(
                            alliance_id=alliance.id,
                            party_id=p_options[sel_p_name],
                            seats_sharing_tn=m_seats_tn,
                            seats_sharing_py=m_seats_py,
                            symbol_name=m_sym_name,
                            symbol_name_ta=m_sym_name_ta,
                            symbol_image_url=img_path
                        )
                        db.add(new_mem)
                        db.commit()
                        st.success(f"{sel_p_name} added to {alliance.name}")
                        st.session_state.show_add_member = False
                        st.rerun()
                    if mbc2.form_submit_button(t("cancel")):
                        st.session_state.show_add_member = False
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Form to edit member
            if user and user['role'] == 'admin' and st.session_state.get('editing_member_id'):
                m_id = st.session_state.editing_member_id
                mem_to_edit = db.query(AllianceParty).filter(AllianceParty.id == m_id).first()
                if mem_to_edit:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.subheader(f"{t('edit')} {t('alliance_details')}: {mem_to_edit.party.name}")
                    
                    with st.form("edit_alliance_member_form"):
                        me_col1, me_col2 = st.columns(2)
                        with me_col1:
                            me_seats_tn = st.number_input(t("seats_sharing_tn"), min_value=0, step=1, value=mem_to_edit.seats_sharing_tn or 0)
                            me_seats_py = st.number_input(t("seats_sharing_py"), min_value=0, step=1, value=mem_to_edit.seats_sharing_py or 0)
                            me_sym_name = st.text_input(f"{t('symbol_name')} (EN)", value=mem_to_edit.symbol_name or "")
                        with me_col2:
                            me_sym_img = st.file_uploader(f"Update {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                            me_sym_name_ta = st.text_input(f"{t('symbol_name')} (TA)", value=mem_to_edit.symbol_name_ta or "")
                        
                        mebc1, mebc2 = st.columns([1, 5])
                        if mebc1.form_submit_button(t("save")):
                            if me_sym_img:
                                if not os.path.exists("images"): os.makedirs("images")
                                img_path = f"images/mem_sym_{me_sym_img.name}"
                                with open(img_path, "wb") as f: f.write(me_sym_img.getbuffer())
                                mem_to_edit.symbol_image_url = img_path
                            
                            mem_to_edit.seats_sharing_tn = me_seats_tn
                            mem_to_edit.seats_sharing_py = me_seats_py
                            mem_to_edit.symbol_name = me_sym_name
                            mem_to_edit.symbol_name_ta = me_sym_name_ta
                            
                            db.commit()
                            st.success(f"Updated {mem_to_edit.party.name} details")
                            st.session_state.editing_member_id = None
                            st.rerun()
                        if mebc2.form_submit_button(t("cancel")):
                            st.session_state.editing_member_id = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            # Member parties table-like view
            members = db.query(AllianceParty).filter(AllianceParty.alliance_id == alliance.id).all()
            if not members:
                st.info("No member parties found.")
            else:
                # Header
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); padding: 8px 10px; border-radius: 5px; font-weight: bold; display: flex; align-items: center; margin-bottom: 2px;">
                    <div style="width: 8%;">Symbol</div>
                    <div style="width: 22%;">Party Name</div>
                    <div style="width: 10%;">Short</div>
                    <div style="width: 10%;">TN Seats</div>
                    <div style="width: 10%;">PY Seats</div>
                    <div style="width: 10%;">Alliance</div>
                    <div style="width: 10%;">Type</div>
                    <div style="width: 10%;">Year</div>
                    <div style="width: 10%; text-align: center;">Actions</div>
                </div>
                """, unsafe_allow_html=True)
                
                for m in members:
                    p = m.party
                    # Use columns for everything to remove gaps and align perfectly
                    # symbol(1), name(3), short(1.5), tn(1), py(1), alliance(1.5), type(1), year(1), actions(1)
                    # Total = 12 parts
                    cols = st.columns([1, 2.5, 1.2, 1, 1, 1.2, 1, 1, 1.2])
                    
                    # Background wrapper via HTML (since Streamlit columns don't have backgrounds)
                    st.markdown("""
                    <style>
                    div[data-testid="stHorizontalBlock"] {
                        background: rgba(255,255,255,0.03);
                        border-radius: 4px;
                        margin-bottom: 1px;
                        padding: 2px 0;
                        align-items: center;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    with cols[0]:
                        if m.symbol_image_url:
                            st.image(m.symbol_image_url, width=30)
                        else:
                            st.write("🚩")
                    with cols[1]: st.markdown(f"**{get_val(p, 'full_name')}**")
                    with cols[2]: st.write(get_val(p, 'name'))
                    with cols[3]: st.markdown(f'<span style="color:#00d4ff">{m.seats_sharing_tn or 0}</span>', unsafe_allow_html=True)
                    with cols[4]: st.markdown(f'<span style="color:#00d4ff">{m.seats_sharing_py or 0}</span>', unsafe_allow_html=True)
                    with cols[5]: st.write(get_val(alliance, 'name'))
                    with cols[6]: st.write(t('state') if alliance.election_type == 'state' else t('center'))
                    with cols[7]: st.write(alliance.year)
                    with cols[8]:
                        if user and user['role'] == 'admin':
                            b_c1, b_c2 = st.columns(2)
                            if b_c1.button("✏️", key=f"ed_m_{m.id}", help=t("edit")):
                                st.session_state.editing_member_id = m.id
                                st.rerun()
                            if b_c2.button("🗑️", key=f"de_m_{m.id}", help=t("delete")):
                                db.delete(m)
                                db.commit()
                                st.rerun()

    else:
        header_col1, header_col2 = st.columns([5, 1])
        with header_col1:
            st.title(t("alliances"))
        
        # Admin Add (+) Button
        if user and user['role'] == 'admin':
            with header_col2:
                if st.button("➕", help=f"{t('add_new')} {t('alliances')}"):
                    st.session_state.show_add_alliance = True
            
            if st.session_state.get('show_add_alliance', False):
                with st.container():
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader(f"{t('add_new')} {t('alliances')}")
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input(f"{t('alliances')} {t('name')} (Short EN)")
                            new_name_ta = st.text_input(f"{t('alliances')} {t('name')} (Short TA)")
                            new_fullname = st.text_input(f"{t('alliances')} {t('full_name')} (EN)")
                            new_fullname_ta = st.text_input(f"{t('alliances')} {t('full_name')} (TA)")
                            new_party = st.text_input(f"{t('primary_party')} (EN)")
                            new_party_ta = st.text_input(f"{t('primary_party')} (TA)")
                            new_leader = st.text_input(f"{t('leader')} (EN)")
                            new_leader_ta = st.text_input(f"{t('leader')} (TA)")
                        with col2:
                            new_etype = st.selectbox(t("election_type"), [t("state"), t("center")])
                            new_year = st.number_input(t("election_year"), min_value=1950, max_value=2100, value=2026)
                            new_desc = st.text_area(f"{t('description')} (EN)")
                            new_desc_ta = st.text_area(f"{t('description')} (TA)")
                        
                        if st.button(t("save")):
                            new_a = Alliance(
                                name=new_name, name_ta=new_name_ta,
                                full_name=new_fullname, full_name_ta=new_fullname_ta,
                                primary_party=new_party, primary_party_ta=new_party_ta,
                                leader=new_leader, leader_ta=new_leader_ta,
                                election_type="state" if new_etype == t("state") else "center",
                                year=new_year,
                                description=new_desc, description_ta=new_desc_ta,
                                created_at=datetime.now().isoformat()
                            )
                            db.add(new_a)
                            db.commit()
                            st.success(f"{t('alliances')} {new_name} {t('save')}d!")
                            st.session_state.show_add_alliance = False
                            st.rerun()
                        if st.button(t("cancel")):
                            st.session_state.show_add_alliance = False
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

        # Filter
        all_alliances = db.query(Alliance).all()
        alliance_names = ["All"] + [a.name for a in all_alliances]
        selected_alliance = st.selectbox(f"Filter by {t('alliances')}", alliance_names)
        
        # Listing
        query = db.query(Alliance)
        if selected_alliance != "All":
            query = query.filter(Alliance.name == selected_alliance)
        
        display_alliances = query.all()
        
        if not display_alliances:
            st.info("No alliances found.")
        
        for alliance in display_alliances:
            with st.container():
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    
                    # Data preparation
                    short_n = get_val(alliance, 'name')
                    full_n = get_val(alliance, 'full_name')
                    disp_name = f"{short_n} ({full_n})" if full_n else short_n
                    etype_disp = t("state") if alliance.election_type == "state" else t("center")
                    
                    # Layout: Info (Left) | Icons (Right)
                    col_info, col_actions = st.columns([8, 1])
                    
                    with col_info:
                        if st.button(f"🤝 {disp_name} ({etype_disp} - {alliance.year})", 
                                     key=f"card_btn_{alliance.id}", use_container_width=True):
                            st.session_state.viewing_alliance_id = alliance.id
                            st.rerun()
                        
                        # Info Grid
                        i1, i2, i3, i4 = st.columns(4)
                        i1.markdown(f"**{t('primary_party')}:** {get_val(alliance, 'primary_party')}")
                        i2.markdown(f"**{t('leader')}:** {get_val(alliance, 'leader')}")
                        i3.markdown(f"**{t('election_type')}:** {etype_disp}")
                        i4.markdown(f"**{t('election_year')}:** {alliance.year}")
                        
                        # Description
                        if get_val(alliance, 'description'):
                            st.caption(f"**{t('description')}:** {get_val(alliance, 'description')}")

                    with col_actions:
                        if user and user['role'] == 'admin':
                            ia1, ia2 = st.columns(2)
                            if ia1.button("📝", key=f"edit_icon_{alliance.id}", help=t("edit")):
                                st.session_state.editing_alliance_id = alliance.id
                                st.rerun()
                            if ia2.button("🗑️", key=f"del_icon_{alliance.id}", help=t("delete")):
                                db.delete(alliance)
                                db.commit()
                                st.success(f"{t('delete')}d {alliance.name}")
                                st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
            # Edit Alliance Overlay
            # Edit Alliance Overlay (Placed explicitly outside the loop)
            if user and user['role'] == 'admin' and st.session_state.get('editing_alliance_id'):
                edit_aid = st.session_state.editing_alliance_id
                edit_all = db.query(Alliance).filter(Alliance.id == edit_aid).first()
                if edit_all:
                    st.divider()
                    st.subheader(f"{t('edit')} {t('alliances')}: {edit_all.name}")
                    # Use a dynamic key just in case, or ensure single instance
                    with st.form(key=f"edit_alliance_form_{edit_aid}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            upd_name = st.text_input(f"{t('alliances')} {t('name')} (Short EN)", value=edit_all.name)
                            upd_name_ta = st.text_input(f"{t('alliances')} {t('name')} (Short TA)", value=edit_all.name_ta if edit_all.name_ta else "")
                            upd_fullname = st.text_input(f"{t('alliances')} {t('full_name')} (EN)", value=edit_all.full_name if edit_all.full_name else "")
                            upd_fullname_ta = st.text_input(f"{t('alliances')} {t('full_name')} (TA)", value=edit_all.full_name_ta if edit_all.full_name_ta else "")
                            upd_party = st.text_input(f"{t('primary_party')} (EN)", value=edit_all.primary_party if edit_all.primary_party else "")
                            upd_party_ta = st.text_input(f"{t('primary_party')} (TA)", value=edit_all.primary_party_ta if edit_all.primary_party_ta else "")
                            upd_leader = st.text_input(f"{t('leader')} (EN)", value=edit_all.leader if edit_all.leader else "")
                            upd_leader_ta = st.text_input(f"{t('leader')} (TA)", value=edit_all.leader_ta if edit_all.leader_ta else "")
                        with col2:
                            etype_options = [t("state"), t("center")]
                            current_etype_idx = 0 if edit_all.election_type == "state" else 1
                            upd_etype = st.selectbox(t("election_type"), etype_options, index=current_etype_idx)
                            upd_year = st.number_input(t("election_year"), min_value=1950, max_value=2100, value=edit_all.year if edit_all.year else 2026)
                        
                        upd_desc = st.text_area(f"{t('description')} (EN)", value=edit_all.description if edit_all.description else "")
                        upd_desc_ta = st.text_area(f"{t('description')} (TA)", value=edit_all.description_ta if edit_all.description_ta else "")
                        
                        bc1, bc2 = st.columns([1, 5])
                        with bc1:
                            if st.form_submit_button(t("save")):
                                edit_all.name = upd_name
                                edit_all.name_ta = upd_name_ta
                                edit_all.full_name = upd_fullname
                                edit_all.full_name_ta = upd_fullname_ta
                                edit_all.primary_party = upd_party
                                edit_all.primary_party_ta = upd_party_ta
                                edit_all.leader = upd_leader
                                edit_all.leader_ta = upd_leader_ta
                                edit_all.election_type = "state" if upd_etype == t("state") else "center"
                                edit_all.year = upd_year
                                edit_all.description = upd_desc
                                edit_all.description_ta = upd_desc_ta
                                db.commit()
                                st.success(t("save") + "d!")
                                st.session_state.editing_alliance_id = None
                                st.rerun()
                        with bc2:
                            if st.form_submit_button(t("cancel")):
                                st.session_state.editing_alliance_id = None
                                st.rerun()

elif choice == t("parties"):
    header_col1, header_col2, header_col3 = st.columns([5, 1.5, 0.5])
    with header_col1:
        st.title(t("parties"))
    with header_col2:
        try:
            view_mode = st.segmented_control(t("view"), options=["Grid", "List"], default="Grid", label_visibility="collapsed")
        except:
            view_mode = st.radio(t("view"), ["Grid", "List"], horizontal=True, label_visibility="collapsed")
    
    db = next(get_db())
    
    # Admin Add (+) Button
    if user and user['role'] == 'admin':
        with header_col2:
            if st.button("➕", key="add_party_btn", help=f"{t('add_new')} {t('parties')}"):
                st.session_state.show_add_party = True

        if st.session_state.get('show_add_party', False):
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(f"{t('add_new')} {t('parties')}")
                with st.form("add_party_form", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_p_name = st.text_input(f"{t('name')} (Short EN)*")
                        new_p_name_ta = st.text_input(f"{t('name')} (Short TA)*")
                        new_p_fullname = st.text_input(f"{t('full_name')} (EN)*")
                        new_p_fullname_ta = st.text_input(f"{t('full_name')} (TA)*")
                    with col2:
                        new_p_leader = st.text_input(f"{t('leader')} (EN)*")
                        new_p_leader_ta = st.text_input(f"{t('leader')} (TA)*")
                        new_p_sym_name = st.text_input(f"{t('symbol')} (EN)*")
                        new_p_sym_name_ta = st.text_input(f"{t('symbol')} (TA)*")
                        new_p_category = st.selectbox(f"{t('category')}*", ["National", "State", "Unrecognized"])
                    
                    state_options = [t("tn"), t("py"), t("ind")]
                    new_p_states = st.multiselect(t("state"), state_options)
                    new_p_sym_img = st.file_uploader(f"Upload {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                    new_p_desc = st.text_area(f"{t('description')} (EN)")
                    new_p_desc_ta = st.text_area(f"{t('description')} (TA)")
                    
                    bc1, bc2 = st.columns([1, 5])
                    with bc1:
                        submitted = st.form_submit_button(t("save"))
                    with bc2:
                        if st.form_submit_button(t("cancel")):
                            st.session_state.show_add_party = False
                            st.rerun()

                    if submitted:
                        if not new_p_name or not new_p_fullname or not new_p_leader or not new_p_sym_name:
                            st.error("Please fill in all required fields (*)")
                        else:
                            sym_img_path = None
                            if new_p_sym_img:
                                if not os.path.exists("images"): os.makedirs("images")
                                sym_img_path = f"images/party_sym_{new_p_sym_img.name}"
                                with open(sym_img_path, "wb") as f: f.write(new_p_sym_img.getbuffer())
                            
                            # Convert selected states back to English for DB storage uniformity
                            db_states = []
                            for s in new_p_states:
                                if s == t("tn"): db_states.append("Tamil Nadu")
                                elif s == t("py"): db_states.append("Pondicherry")
                                elif s == t("ind"): db_states.append("India")
                            
                            new_p = Party(
                                name=new_p_name, name_ta=new_p_name_ta,
                                full_name=new_p_fullname, full_name_ta=new_p_fullname_ta,
                                leader=new_p_leader, leader_ta=new_p_leader_ta,
                                symbol_name=new_p_sym_name, symbol_name_ta=new_p_sym_name_ta,
                                symbol_image_url=sym_img_path,
                                state=",".join(db_states),
                                description=new_p_desc, description_ta=new_p_desc_ta,
                                category=new_p_category,
                                created_at=datetime.now().isoformat()
                            )
                            db.add(new_p)
                            db.commit()
                            st.success(f"Party {new_p_name} added!")
                            st.session_state.show_add_party = False
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Listing
    query = db.query(Party)
    parties = query.all()
    
    if not parties:
        st.info("No parties found. Click the + button to add one.")
    else:
        if view_mode == "Grid":
            p_idx = 0
            while p_idx < len(parties):
                cols = st.columns(3)
                for col in cols:
                    if p_idx < len(parties):
                        party = parties[p_idx]
                        with col:
                            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
                            
                            # Actions at top right
                            if user and user['role'] == 'admin':
                                act_c1, act_c2 = st.columns([3, 2])
                                with act_c2:
                                    ip1, ip2 = st.columns(2)
                                    if ip1.button("📝", key=f"edit_g_{party.id}", help=t("edit")):
                                        st.session_state.editing_party_id = party.id
                                        st.rerun()
                                    if ip2.button("🗑️", key=f"del_g_{party.id}", help=t("delete")):
                                        db.delete(party)
                                        db.commit()
                                        st.rerun()
                            
                            if party.symbol_image_url and os.path.exists(party.symbol_image_url):
                                st.image(party.symbol_image_url, use_container_width=True)
                            else:
                                st.markdown("<h1 style='text-align: center;'>🚩</h1>", unsafe_allow_html=True)
                            
                            display_name = f"{get_val(party, 'name')} ({get_val(party, 'full_name')})"
                            st.markdown(f"### {display_name}")
                            st.write(f"**{t('leader')}:** {get_val(party, 'leader')}")
                            st.write(f"**{t('symbol')}:** {get_val(party, 'symbol_name')}")
                            if party.category:
                                st.write(f"**{t('category')}:** {party.category}")
                            if party.state:
                                # Show states with Tamil translation if applicable
                                state_list = party.state.split(",")
                                disp_states = []
                                for s in state_list:
                                    if s == "Tamil Nadu": disp_states.append(t("tn"))
                                    elif s == "Pondicherry": disp_states.append(t("py"))
                                st.write(f"**{t('state')}:** {', '.join(disp_states)}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        p_idx += 1
        else: # List View
            for party in parties:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                col1, col2, col_act = st.columns([1, 3.5, 0.5])
                with col1:
                    if party.symbol_image_url and os.path.exists(party.symbol_image_url):
                        st.image(party.symbol_image_url, width=100)
                    else:
                        st.markdown("### 🚩")
                with col2:
                    display_name = f"{get_val(party, 'name')} ({get_val(party, 'full_name')})"
                    st.markdown(f"### {display_name}")
                    st.write(f"**{t('leader')}:** {get_val(party, 'leader')} | **{t('symbol')}:** {get_val(party, 'symbol_name')}")
                    if party.category:
                        st.write(f"**{t('category')}:** {party.category}")
                    if party.state:
                        state_list = party.state.split(",")
                        disp_states = []
                        for s in state_list:
                            if s == "Tamil Nadu": disp_states.append(t("tn"))
                            elif s == "Pondicherry": disp_states.append(t("py"))
                        st.write(f"**{t('state')}:** {', '.join(disp_states)}")
                    if get_val(party, 'description'):
                        st.write(get_val(party, 'description'))
                with col_act:
                    if user and user['role'] == 'admin':
                        ip1, ip2 = st.columns(2)
                        if ip1.button("📝", key=f"edit_l_{party.id}", help=t("edit")):
                            st.session_state.editing_party_id = party.id
                            st.rerun()
                        if ip2.button("🗑️", key=f"del_l_{party.id}", help=t("delete")):
                            db.delete(party)
                            db.commit()
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    
    # Edit Party Form Overlay
    if user and user['role'] == 'admin' and st.session_state.get('editing_party_id'):
        editing_id = st.session_state.editing_party_id
        edit_party = db.query(Party).filter(Party.id == editing_id).first()
        if edit_party:
            st.divider()
            st.subheader(f"{t('edit')} {t('parties')}: {edit_party.name}")
            with st.form("edit_party_form"):
                col1, col2 = st.columns(2)
                with col1:
                    upd_name = st.text_input(f"{t('name')} (Short EN)", value=edit_party.name)
                    upd_name_ta = st.text_input(f"{t('name')} (Short TA)", value=edit_party.name_ta if edit_party.name_ta else "")
                    upd_fullname = st.text_input(f"{t('full_name')} (EN)", value=edit_party.full_name if edit_party.full_name else "")
                    upd_fullname_ta = st.text_input(f"{t('full_name')} (TA)", value=edit_party.full_name_ta if edit_party.full_name_ta else "")
                with col2:
                    upd_leader = st.text_input(f"{t('leader')} (EN)", value=edit_party.leader if edit_party.leader else "")
                    upd_leader_ta = st.text_input(f"{t('leader')} (TA)", value=edit_party.leader_ta if edit_party.leader_ta else "")
                    upd_sym_name = st.text_input(f"{t('symbol')} (EN)", value=edit_party.symbol_name if edit_party.symbol_name else "")
                    upd_sym_name_ta = st.text_input(f"{t('symbol')} (TA)", value=edit_party.symbol_name_ta if edit_party.symbol_name_ta else "")
                    
                    cat_opts = ["National", "State", "Unrecognized"]
                    cat_idx = 0
                    if edit_party.category in cat_opts:
                        cat_idx = cat_opts.index(edit_party.category)
                    upd_category = st.selectbox(f"{t('category')}", cat_opts, index=cat_idx)
                
                state_options = [t("tn"), t("py")]
                current_states = []
                if edit_party.state:
                    for s in edit_party.state.split(","):
                        if s == "Tamil Nadu": current_states.append(t("tn"))
                        elif s == "Pondicherry": current_states.append(t("py"))
                
                upd_states = st.multiselect(t("state"), state_options, default=current_states)
                upd_sym_img = st.file_uploader(f"Update {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                upd_desc = st.text_area(f"{t('description')} (EN)", value=edit_party.description if edit_party.description else "")
                upd_desc_ta = st.text_area(f"{t('description')} (TA)", value=edit_party.description_ta if edit_party.description_ta else "")
                
                bc1, bc2 = st.columns([1, 5])
                with bc1:
                    if st.form_submit_button(t("save")):
                        edit_party.name = upd_name
                        edit_party.name_ta = upd_name_ta
                        edit_party.full_name = upd_fullname
                        edit_party.full_name_ta = upd_fullname_ta
                        edit_party.leader = upd_leader
                        edit_party.leader_ta = upd_leader_ta
                        edit_party.symbol_name = upd_sym_name
                        edit_party.symbol_name_ta = upd_sym_name_ta
                        edit_party.category = upd_category
                        edit_party.description = upd_desc
                        edit_party.description_ta = upd_desc_ta
                        
                        # Update states
                        db_upd_states = []
                        for s in upd_states:
                            if s == t("tn"): db_upd_states.append("Tamil Nadu")
                            elif s == t("py"): db_upd_states.append("Pondicherry")
                        edit_party.state = ",".join(db_upd_states)
                        
                        if upd_sym_img:
                            if not os.path.exists("images"): os.makedirs("images")
                            sym_img_path = f"images/party_sym_{upd_sym_img.name}"
                            with open(sym_img_path, "wb") as f: f.write(upd_sym_img.getbuffer())
                            edit_party.symbol_image_url = sym_img_path
                            
                        db.commit()
                        st.success(t("save") + "d!")
                        st.session_state.editing_party_id = None
                        st.rerun()
                with bc2:
                    if st.form_submit_button(t("cancel")):
                        st.session_state.editing_party_id = None
                        st.rerun()

elif choice == t("constituencies"):
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.title(t("constituencies"))
    
    db = next(get_db())
    
    # Admin Add (+) Button
    if user and user['role'] == 'admin':
        with header_col2:
            if st.button("➕", help=f"{t('add_new')} {t('constituencies')}"):
                st.session_state.show_add_const = True
        
        if st.session_state.get('show_add_const', False):
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(f"{t('add_new')} {t('constituencies')}")
                with st.form("add_const_form"):
                    ac_col1, ac_col2 = st.columns(2)
                    with ac_col1:
                        new_c_state = st.selectbox(t("state"), [t("tn"), t("py")])
                        new_c_dist = st.text_input(f"{t('district')} (EN)")
                        new_c_dist_ta = st.text_input(f"{t('district')} (TA)")
                    with ac_col2:
                        new_c_name = st.text_input(f"{t('constituency')} (EN)")
                        new_c_name_ta = st.text_input(f"{t('constituency')} (TA)")
                        new_c_type = st.selectbox(t("type"), [t("general"), t("reserved")])
                    
                    st.write(f"**{t('total_voters')}**")
                    v_col1, v_col2, v_col3, v_col4 = st.columns(4)
                    with v_col1: nv_total = st.number_input(t("total_voters"), min_value=0, step=1)
                    with v_col2: nv_male = st.number_input(t("male"), min_value=0, step=1)
                    with v_col3: nv_female = st.number_input(t("female"), min_value=0, step=1)
                    with v_col4: nv_third = st.number_input(t("third_gender"), min_value=0, step=1)

                    ac_sub1, ac_sub2 = st.columns([1, 5])
                    if ac_sub1.form_submit_button(t("save")):
                        c_state_val = "Tamil Nadu" if new_c_state == t("tn") else "Pondicherry"
                        new_const = Constituency(
                            state=c_state_val, 
                            district=new_c_dist, district_ta=new_c_dist_ta,
                            name=new_c_name, name_ta=new_c_name_ta,
                            type="General" if new_c_type == t("general") else "Reserved",
                            total_voters=nv_total, male_voters=nv_male,
                            female_voters=nv_female, third_gender_voters=nv_third
                        )
                        db.add(new_const)
                        db.commit()
                        st.success(f"{new_c_name} added!")
                        st.session_state.show_add_const = False
                        st.rerun()
                    if ac_sub2.form_submit_button(t("cancel")):
                        st.session_state.show_add_const = False
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Filters
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        f_state = st.selectbox(f"Filter by {t('state')}", ["All", t("tn"), t("py")])
    with fcol2:
        # Dynamic districts based on state filter
        dist_query = db.query(Constituency.district).distinct()
        if f_state != "All":
            s_val = "Tamil Nadu" if f_state == t("tn") else "Pondicherry"
            dist_query = dist_query.filter(Constituency.state == s_val)
        dist_list = ["All"] + [d[0] for d in dist_query.all() if d[0]]
        f_dist = st.selectbox(f"Filter by {t('district')}", dist_list)

    # Listing
    query = db.query(Constituency)
    if f_state != "All":
        s_val = "Tamil Nadu" if f_state == t("tn") else "Pondicherry"
        query = query.filter(Constituency.state == s_val)
    if f_dist != "All":
        query = query.filter(Constituency.district == f_dist)
    
    consts = query.all()
    
    if not consts:
        st.info("No constituencies found.")
    else:
        # Sync ratios with indices below: [2, 1, 1.2, 1.2, 1, 1, 1, 1, 1.2]
        h_cols = st.columns([2, 1, 1.2, 1.2, 1, 1, 1, 1, 1.2])
        header_style = """
            background: rgba(255,255,255,0.1); 
            padding: 8px 10px; 
            border-radius: 5px; 
            font-weight: bold;
            display: flex;
            align-items: center;
            margin-bottom: 2px;
        """
        with h_cols[0]: st.markdown("**Name**")
        with h_cols[1]: st.markdown("**Type**")
        with h_cols[2]: st.markdown("**District**")
        with h_cols[3]: st.markdown("**State**")
        with h_cols[4]: st.markdown("**Total**")
        with h_cols[5]: st.markdown("**Male**")
        with h_cols[6]: st.markdown("**Female**")
        with h_cols[7]: st.markdown("**Other**")
        with h_cols[8]: st.markdown("**Actions**")
        
        # Additional CSS to make header columns more robust
        st.markdown("""
            <style>
            [data-testid="stHorizontalBlock"]:first-child {
                background: rgba(255,255,255,0.1);
                border-radius: 5px;
                padding: 4px 0;
                margin-bottom: 5px;
            }
            </style>
        """, unsafe_allow_html=True)

        
        for c in consts:
            type_color = "#00d4ff" if c.type == "General" else "#ffaa00"
            type_label = t("general") if c.type == "General" else t("reserved")
            # Edit Form Overlay
            if user and user['role'] == 'admin' and st.session_state.get('editing_const_id') == c.id:
                with st.container():
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.subheader(f"{t('edit')} {t('constituency')}: {c.name}")
                    with st.form(f"edit_const_form_{c.id}"):
                        ec_col1, ec_col2 = st.columns(2)
                        with ec_col1:
                            curr_state_t = t("tn") if c.state == "Tamil Nadu" else t("py")
                            upd_c_state = st.selectbox(t("state"), [t("tn"), t("py")], index=0 if c.state == "Tamil Nadu" else 1)
                            upd_c_dist = st.text_input(f"{t('district')} (EN)", value=c.district)
                            upd_c_dist_ta = st.text_input(f"{t('district')} (TA)", value=c.district_ta if c.district_ta else "")
                        with ec_col2:
                            upd_c_name = st.text_input(f"{t('constituency')} (EN)", value=c.name)
                            upd_c_name_ta = st.text_input(f"{t('constituency')} (TA)", value=c.name_ta if c.name_ta else "")
                            upd_c_type = st.selectbox(t("type"), [t("general"), t("reserved")], index=0 if c.type == "General" else 1)
                        
                        st.write(f"**{t('total_voters')}**")
                        ev_col1, ev_col2, ev_col3, ev_col4 = st.columns(4)
                        upd_v_total = ev_col1.number_input(t("total_voters"), min_value=0, step=1, value=c.total_voters or 0)
                        upd_v_male = ev_col2.number_input(t("male"), min_value=0, step=1, value=c.male_voters or 0)
                        upd_v_female = ev_col3.number_input(t("female"), min_value=0, step=1, value=c.female_voters or 0)
                        upd_v_third = ev_col4.number_input(t("third_gender"), min_value=0, step=1, value=c.third_gender_voters or 0)

                        ec_sub1, ec_sub2 = st.columns([1, 5])
                        if ec_sub1.form_submit_button(t("save")):
                            c.state = "Tamil Nadu" if upd_c_state == t("tn") else "Pondicherry"
                            c.district = upd_c_dist
                            c.district_ta = upd_c_dist_ta
                            c.name = upd_c_name
                            c.name_ta = upd_c_name_ta
                            c.type = "General" if upd_c_type == t("general") else "Reserved"
                            c.total_voters = upd_v_total
                            c.male_voters = upd_v_male
                            c.female_voters = upd_v_female
                            c.third_gender_voters = upd_v_third
                            db.commit()
                            st.success(f"{upd_c_name} updated!")
                            st.session_state.editing_const_id = None
                            st.rerun()
                        if ec_sub2.form_submit_button(t("cancel")):
                            st.session_state.editing_const_id = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            cols = st.columns([2, 1, 1.2, 1.2, 1, 1, 1, 1, 1.2])
            with cols[0]: st.markdown(f"**{get_val(c, 'name')}**")
            with cols[1]: st.markdown(f'<span style="background: {type_color}33; color: {type_color}; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; border: 1px solid {type_color}66;">{type_label}</span>', unsafe_allow_html=True)
            with cols[2]: st.write(get_val(c, 'district'))
            with cols[3]: st.write(t('tn') if c.state == 'Tamil Nadu' else t('py'))
            with cols[4]: st.markdown(f'<span style="color:#00d4ff">{c.total_voters or 0}</span>', unsafe_allow_html=True)
            with cols[5]: st.write(c.male_voters or 0)
            with cols[6]: st.write(c.female_voters or 0)
            with cols[7]: st.write(c.third_gender_voters or 0)
            with cols[8]:
                if user and user['role'] == 'admin':
                    act_c1, act_c2 = st.columns(2)
                    if act_c1.button("✏️", key=f"edit_c_{c.id}", help=t("edit")):
                        st.session_state.editing_const_id = c.id
                        st.rerun()
                    if act_c2.button("🗑️", key=f"del_c_{c.id}", help=t("delete")):
                        db.delete(c)
                        db.commit()
                        st.rerun()



elif choice == t("candidates"):
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.title(t("candidates"))
    
    db = next(get_db())
    
    # Admin Add (+) Button
    if user and user['role'] == 'admin':
        with header_col2:
            if st.button("➕", help=f"{t('add_new')} {t('candidates')}"):
                st.session_state.show_add_cand = True
        
        if st.session_state.get('show_add_cand', False):
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(f"{t('add_new')} {t('candidates')}")
                with st.form("add_candidate_merged_form", clear_on_submit=True):
                    ac_col1, ac_col2, ac_col3 = st.columns(3)
                    with ac_col1:
                        ca_name = st.text_input(f"{t('name')} (EN)*")
                        ca_name_ta = st.text_input(f"{t('name')} (TA)*")
                        ca_age = st.number_input("Age (Optional)", min_value=18, max_value=120, value=None)
                        ca_gender = st.selectbox(t("gender"), [t("male"), t("female"), t("other")])
                    with ac_col2:
                        all_parties = db.query(Party).all()
                        ca_party = st.selectbox(f"{t('select_party')}*", [p.name for p in all_parties])
                        all_consts = db.query(Constituency).all()
                        ca_const_name = st.selectbox(f"{t('constituency')}*", [c.name for c in all_consts])
                        ca_link = st.text_input(t("election_link"))
                    with ac_col3:
                        ca_sym_name = st.text_input(f"{t('symbol_name')} (EN)")
                        ca_sym_name_ta = st.text_input(f"{t('symbol_name')} (TA)")
                        ca_sym_img = st.file_uploader(f"Upload {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                    
                    ca_photo = st.file_uploader("Candidate Photo", type=["png", "jpg", "jpeg"])
                    ca_bio = st.text_area(f"{t('bio')} (EN)")
                    ca_bio_ta = st.text_area(f"{t('bio')} (TA)")

                    ac_sub1, ac_sub2 = st.columns([1, 5])
                    if ac_sub1.form_submit_button(t("save")):
                        p_obj = db.query(Party).filter(Party.name == ca_party).first()
                        c_obj = db.query(Constituency).filter(Constituency.name == ca_const_name).first()
                        
                        sym_path = None
                        if ca_sym_img:
                            if not os.path.exists("images"): os.makedirs("images")
                            sym_path = f"images/cand_sym_{ca_sym_img.name}"
                            with open(sym_path, "wb") as f: f.write(ca_sym_img.getbuffer())
                        
                        photo_path = None
                        if ca_photo:
                            if not os.path.exists("images"): os.makedirs("images")
                            photo_path = f"images/cand_photo_{ca_photo.name}"
                            with open(photo_path, "wb") as f: f.write(ca_photo.getbuffer())
                            
                        new_cand = Candidate(
                            name=ca_name, name_ta=ca_name_ta,
                            age=ca_age, gender="Male" if ca_gender == t("male") else "Female" if ca_gender == t("female") else "Other",
                            party_id=p_obj.id,
                            alliance_id=p_obj.alliance_id,
                            constituency_id=c_obj.id,
                            constituency=c_obj.name, # Sync legacy
                            district=c_obj.district, # Sync legacy
                            symbol_name=ca_sym_name, symbol_name_ta=ca_sym_name_ta,
                            symbol_image_url=sym_path,
                            image_url=photo_path,
                            bio=ca_bio, bio_ta=ca_bio_ta,
                            election_link=ca_link,
                            created_at=datetime.now().isoformat()
                        )
                        db.add(new_cand)
                        db.commit()
                        st.success(f"Candidate {ca_name} added successfully!")
                        st.session_state.show_add_cand = False
                        st.rerun()
                    if ac_sub2.form_submit_button(t("cancel")):
                        st.session_state.show_add_cand = False
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Filters
    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        f_state = st.selectbox(f"Filter by {t('state')}", ["All", t("tn"), t("py")])
    with fcol2:
        # Dynamic districts
        d_query = db.query(Constituency.district).distinct()
        if f_state != "All":
            s_val = "Tamil Nadu" if f_state == t("tn") else "Pondicherry"
            d_query = d_query.filter(Constituency.state == s_val)
        dist_list = ["All"] + [d[0] for d in d_query.all() if d[0]]
        f_dist = st.selectbox(f"Filter by {t('district')}", dist_list)
    with fcol3:
        # Dynamic constituencies
        c_query = db.query(Constituency)
        if f_state != "All":
            s_val = "Tamil Nadu" if f_state == t("tn") else "Pondicherry"
            c_query = c_query.filter(Constituency.state == s_val)
        if f_dist != "All":
            c_query = c_query.filter(Constituency.district == f_dist)
        const_list = ["All"] + [c.name for c in c_query.all()]
        f_const = st.selectbox(f"Filter by {t('constituency')}", const_list)
    with fcol4:
        f_party = st.selectbox(f"Filter by {t('parties')}", ["All"] + [p.name for p in db.query(Party).all()])

    # Build Query
    query = db.query(Candidate).join(Candidate.constituency_rel)
    if f_state != "All":
        s_val = "Tamil Nadu" if f_state == t("tn") else "Pondicherry"
        query = query.filter(Constituency.state == s_val)
    if f_dist != "All":
        query = query.filter(Constituency.district == f_dist)
    if f_const != "All":
        query = query.filter(Constituency.name == f_const)
    if f_party != "All":
        party_obj = db.query(Party).filter(Party.name == f_party).first()
        if party_obj:
            query = query.filter(Candidate.party_id == party_obj.id)
    
    candidates = query.all()

    if not candidates:
        st.info("No candidates found matching the criteria.")
    else:
        for cand in candidates:
            # Edit Form Overlay (Inline)
            if user and user['role'] == 'admin' and st.session_state.get('editing_cand_id') == cand.id:
                with st.container():
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.subheader(f"{t('edit')} {t('candidates')}: {cand.name}")
                    with st.form(f"edit_cand_form_{cand.id}"):
                        ec_col1, ec_col2, ec_col3 = st.columns(3)
                        with ec_col1:
                            ec_name = st.text_input(f"{t('name')} (EN)*", value=cand.name)
                            ec_name_ta = st.text_input(f"{t('name')} (TA)*", value=cand.name_ta or "")
                            ec_age = st.number_input("Age (Optional)", min_value=18, max_value=120, value=cand.age)
                            gender_opts = [t("male"), t("female"), t("other")]
                            gender_idx = gender_opts.index(t(cand.gender.lower())) if cand.gender and t(cand.gender.lower()) in gender_opts else 0
                            ec_gender = st.selectbox(t("gender"), gender_opts, index=gender_idx)
                        with ec_col2:
                            all_parties = db.query(Party).all()
                            p_names = [p.name for p in all_parties]
                            p_idx = p_names.index(cand.party.name) if cand.party and cand.party.name in p_names else 0
                            ec_party = st.selectbox(f"{t('select_party')}*", p_names, index=p_idx)
                            
                            all_consts = db.query(Constituency).all()
                            c_names = [c.name for c in all_consts]
                            c_idx = c_names.index(cand.constituency_rel.name) if cand.constituency_rel and cand.constituency_rel.name in c_names else 0
                            ec_const_name = st.selectbox(f"{t('constituency')}*", c_names, index=c_idx)
                            ec_link = st.text_input(t("election_link"), value=cand.election_link or "")
                        with ec_col3:
                            ec_sym_name = st.text_input(f"{t('symbol_name')} (EN)", value=cand.symbol_name or "")
                            ec_sym_name_ta = st.text_input(f"{t('symbol_name')} (TA)", value=cand.symbol_name_ta or "")
                            ec_sym_img = st.file_uploader(f"Update {t('symbol')} Image", type=["png", "jpg", "jpeg"])
                        
                        ec_photo = st.file_uploader("Update Candidate Photo", type=["png", "jpg", "jpeg"])
                        ec_bio = st.text_area(f"{t('bio')} (EN)", value=cand.bio or "")
                        ec_bio_ta = st.text_area(f"{t('bio')} (TA)", value=cand.bio_ta or "")

                        ec_b1, ec_b2 = st.columns([1, 5])
                        if ec_b1.form_submit_button(t("save")):
                            p_obj = db.query(Party).filter(Party.name == ec_party).first()
                            con_obj = db.query(Constituency).filter(Constituency.name == ec_const_name).first()
                            
                            if ec_sym_img:
                                if not os.path.exists("images"): os.makedirs("images")
                                sym_path = f"images/cand_sym_{ec_sym_img.name}"
                                with open(sym_path, "wb") as f: f.write(ec_sym_img.getbuffer())
                                cand.symbol_image_url = sym_path
                            
                            if ec_photo:
                                if not os.path.exists("images"): os.makedirs("images")
                                photo_path = f"images/cand_photo_{ec_photo.name}"
                                with open(photo_path, "wb") as f: f.write(ec_photo.getbuffer())
                                cand.image_url = photo_path
                                
                            cand.name = ec_name
                            cand.name_ta = ec_name_ta
                            cand.age = ec_age
                            cand.gender = "Male" if ec_gender == t("male") else "Female" if ec_gender == t("female") else "Other"
                            cand.party_id = p_obj.id
                            cand.alliance_id = p_obj.alliance_id
                            cand.constituency_id = con_obj.id
                            cand.constituency = con_obj.name
                            cand.district = con_obj.district
                            cand.symbol_name = ec_sym_name
                            cand.symbol_name_ta = ec_sym_name_ta
                            cand.bio = ec_bio
                            cand.bio_ta = ec_bio_ta
                            cand.election_link = ec_link
                            
                            db.commit()
                            st.success(f"Candidate {ec_name} updated!")
                            st.session_state.editing_cand_id = None
                            st.rerun()
                        if ec_b2.form_submit_button(t("cancel")):
                            st.session_state.editing_cand_id = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                col_img, col_info, col_sym, col_acts = st.columns([1, 2.5, 1, 0.5])
                
                with col_img:
                    if cand.image_url and os.path.exists(cand.image_url):
                        st.image(cand.image_url, width=120)
                    else:
                        st.markdown('<div style="width:120px; height:150px; background:rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; border-radius:10px;">👤</div>', unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"### {get_val(cand, 'name')}")
                    st.markdown(f"**{t('parties')}:** {get_val(cand.party, 'name') if cand.party else 'N/A'}")
                    if cand.alliance:
                        st.markdown(f"**{t('alliances')}:** {get_val(cand.alliance, 'name')}")
                    
                    st_name = t('tn') if cand.constituency_rel and cand.constituency_rel.state == 'Tamil Nadu' else t('py') if cand.constituency_rel else 'N/A'
                    dist_name = cand.constituency_rel.district if cand.constituency_rel else 'N/A'
                    const_name = cand.constituency_rel.name if cand.constituency_rel else 'N/A'
                    
                    st.markdown(f"**{t('constituency')}:** {const_name} ({st_name} - {dist_name})")
                    if cand.age: st.write(f"Age: {cand.age} | Gender: {cand.gender}")
                    if cand.election_link:
                        st.markdown(f"[Official Election Link]({cand.election_link})")

                with col_sym:
                    if cand.symbol_image_url and os.path.exists(cand.symbol_image_url):
                        st.image(cand.symbol_image_url, width=60)
                        st.caption(get_val(cand, 'symbol_name'))
                    elif cand.symbol_name:
                        st.write(f"**{t('symbol')}:** {get_val(cand, 'symbol_name')}")
                        
                with col_acts:
                    if user and user['role'] == 'admin':
                        ia1, ia2 = st.columns(2)
                        if ia1.button("✏️", key=f"edit_cand_{cand.id}", help="Edit Candidate"):
                            st.session_state.editing_cand_id = cand.id
                            st.rerun()
                        if ia2.button("🗑️", key=f"del_cand_{cand.id}", help="Delete Candidate"):
                            db.delete(cand)
                            db.commit()
                            st.rerun()
                            
                st.markdown('</div>', unsafe_allow_html=True)
            st.write("")


elif choice == t("election_stats"):
    st.title(t("election_stats"))
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.info("Comprehensive election statistics and historical comparisons will be available here soon.")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == t("opinion_poll") and user and user['role'] == 'admin':
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.title(t("opinion_poll"))
    
    db = next(get_db())
    
    with header_col2:
        if st.button("➕", help=f"{t('add_new')} {t('opinion_poll')}"):
            st.session_state.show_add_poll = True
    
    if st.session_state.get('show_add_poll', False):
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader(f"{t('add_new')} {t('opinion_poll')}")
            
            # Form for Poll Details
            with st.form("add_poll_unified_form", clear_on_submit=False):
                op_title = st.text_input("Poll Question*", placeholder="e.g., Who will win 2026 election?")
                
                col_s, col_e = st.columns(2)
                with col_s:
                    st.write("**Start Date & Time**")
                    sd = st.date_input("Start Date", key="sd_new")
                    s_time = st.time_input("Start Time", key="st_new")
                with col_e:
                    st.write("**End Date & Time**")
                    ed = st.date_input("End Date", value=sd + timedelta(days=7), key="ed_new")
                    e_time = st.time_input("End Time", key="et_new")
                
                start_dt = datetime.combine(sd, s_time)
                end_dt = datetime.combine(ed, e_time)
                duration = end_dt - start_dt
                if duration.total_seconds() > 0:
                    st.info(f"Calculated Duration: {duration.days}d {duration.seconds // 3600}h")
                else:
                    st.error("End date/time must be after start date/time")

                st.divider()
                st.write("**Parties / Options in this Contest**")
                
                # Dynamic Option List in Session State
                if 'pending_poll_options' not in st.session_state:
                    st.session_state.pending_poll_options = []
                
                # Form cannot have dynamic adding of fields easily without rerun, 
                # so we use session state to show what's added so far.
                for idx, opt in enumerate(st.session_state.pending_poll_options):
                    st.write(f"Option {idx+1}: **{opt['name']}**")
                
                ap_sub1, ap_sub2 = st.columns([1, 5])
                if ap_sub1.form_submit_button(t("save")):
                    if not op_title:
                        st.error("Poll question is required")
                    elif not st.session_state.pending_poll_options:
                        st.error("Please add at least one option")
                    elif duration.total_seconds() <= 0:
                        st.error("Invalid duration")
                    else:
                        new_poll = OpinionPoll(
                            title=op_title,
                            start_datetime=start_dt.isoformat(),
                            end_datetime=end_dt.isoformat(),
                            created_at=datetime.now().isoformat()
                        )
                        db.add(new_poll)
                        db.commit() # Get the poll ID
                        
                        for opt_data in st.session_state.pending_poll_options:
                            new_opt = OpinionPollOption(
                                poll_id=new_poll.id,
                                name=opt_data['name'],
                                symbol_image_url=opt_data['symbol'],
                                color=opt_data['color']
                            )
                            db.add(new_opt)
                        db.commit()
                        
                        st.success("Poll Saved Successfully!")
                        st.session_state.pending_poll_options = []
                        st.session_state.show_add_poll = False
                        st.rerun()

                if ap_sub2.form_submit_button(t("cancel")):
                    st.session_state.pending_poll_options = []
                    st.session_state.show_add_poll = False
                    st.rerun()

            # Separate UI for adding options to the pending list (since nesting forms isn't allowed)
            st.markdown("---")
            st.write("### Add Option")
            with st.container():
                o_col1, o_col2, o_col3 = st.columns([2, 1, 2])
                o_name = o_col1.text_input("Party Name", key="opt_name_tmp")
                o_color = o_col2.color_picker("Color", value="#00d4ff", key="opt_color_tmp")
                o_sym = o_col3.file_uploader("Symbol", type=["png", "jpg", "jpeg"], key="opt_sym_tmp")
                
                if st.button("Add Option (+)", type="secondary"):
                    if o_name:
                        sym_path = None
                        if o_sym:
                            if not os.path.exists("images/polls"): os.makedirs("images/polls", exist_ok=True)
                            sym_path = f"images/polls/pending_{o_sym.name}"
                            with open(sym_path, "wb") as f: f.write(o_sym.getbuffer())
                        
                        st.session_state.pending_poll_options.append({
                            "name": o_name,
                            "color": o_color,
                            "symbol": sym_path
                        })
                        st.rerun()
                    else:
                        st.warning("Please enter a party name")
            st.markdown('</div>', unsafe_allow_html=True)

    # Edit Poll Form
    if user and user['role'] == 'admin' and st.session_state.get('editing_poll_id'):
        ep_id = st.session_state.editing_poll_id
        edit_poll = db.query(OpinionPoll).filter(OpinionPoll.id == ep_id).first()
        if edit_poll:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.subheader(f"Edit Poll: {edit_poll.title}")
                with st.form("edit_poll_form_overlap"):
                    upd_title = st.text_input("Poll Question", value=edit_poll.title)
                    
                    try:
                        curr_start = datetime.fromisoformat(edit_poll.start_datetime)
                        curr_end = datetime.fromisoformat(edit_poll.end_datetime)
                    except:
                        curr_start = datetime.now()
                        curr_end = datetime.now() + timedelta(days=7)
                    
                    ce_col1, ce_col2 = st.columns(2)
                    with ce_col1:
                        usd = st.date_input("Start Date", value=curr_start.date(), key="usd_edit")
                        ust = st.time_input("Start Time", value=curr_start.time(), key="ust_edit")
                    with ce_col2:
                        ued = st.date_input("End Date", value=curr_end.date(), key="ued_edit")
                        uet = st.time_input("End Time", value=curr_end.time(), key="uet_edit")
                    
                    ce_b1, ce_b2 = st.columns([1, 5])
                    if ce_b1.form_submit_button(t("save")):
                        edit_poll.title = upd_title
                        edit_poll.start_datetime = datetime.combine(usd, ust).isoformat()
                        edit_poll.end_datetime = datetime.combine(ued, uet).isoformat()
                        db.commit()
                        st.success("Poll Updated!")
                        st.session_state.editing_poll_id = None
                        st.rerun()
                    if ce_b2.form_submit_button(t("cancel")):
                        st.session_state.editing_poll_id = None
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # Listing
    all_polls = db.query(OpinionPoll).order_by(OpinionPoll.id.desc()).all()
    if not all_polls:
        st.info("No opinion polls found.")
    else:
        for poll in all_polls:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                pcols = st.columns([3, 1])
                with pcols[0]:
                    st.write(f"### {poll.title}")
                    try:
                        s_dt = datetime.fromisoformat(poll.start_datetime)
                        e_dt = datetime.fromisoformat(poll.end_datetime)
                        st.caption(f"Starts: {s_dt.strftime('%d %b %H:%M')} | Ends: {e_dt.strftime('%d %b %H:%M')}")
                    except: pass
                    
                with pcols[1]:
                    # The 4 Icons Section: Edit, Delete, Start/Stop, Visible/Hide
                    i1, i2, i3, i4 = st.columns(4)
                    
                    # 1. Edit
                    if i1.button("✏️", key=f"edit_p_{poll.id}", help="Edit Poll"):
                        st.session_state.editing_poll_id = poll.id
                    
                    # 2. Start/Stop
                    if not poll.is_active:
                        if i2.button("▶️", key=f"start_{poll.id}", help="Start Poll"):
                            poll.is_active = 1
                            db.commit(); st.rerun()
                    else:
                        if i2.button("⏹️", key=f"stop_{poll.id}", help="Stop Poll"):
                            poll.is_active = 0
                            poll.show_on_dashboard = 0
                            db.commit(); st.rerun()
                    
                    # 3. Visible/Hide
                    if poll.is_active:
                        if not poll.show_on_dashboard:
                            if i3.button("👁️", key=f"show_{poll.id}", help="Show on Dashboard"):
                                db.query(OpinionPoll).update({OpinionPoll.show_on_dashboard: 0})
                                poll.show_on_dashboard = 1
                                db.commit(); st.rerun()
                        else:
                            if i3.button("🙈", key=f"hide_{poll.id}", help="Hide from Dashboard"):
                                poll.show_on_dashboard = 0
                                db.commit(); st.rerun()
                    else:
                        i3.button("👁️", key=f"dis_show_{poll.id}", disabled=True, help="Activate poll first")
                    
                    # 4. Delete
                    if i4.button("🗑️", key=f"del_poll_{poll.id}", help="Delete Poll"):
                        db.delete(poll)
                        db.commit(); st.rerun()

                # Results Summary
                v_count = db.query(PollVote).filter(PollVote.poll_id == poll.id).count()
                st.write(f"**Total Votes:** {v_count}")

                # Options Management within Each Poll
                st.divider()
                st.subheader("🏁 Contestants (Options)")
                
                if not poll.options:
                    st.warning("No parties added to this contest yet. Use the form below to add them.")
                else:
                    opt_cols = st.columns(len(poll.options) if len(poll.options) < 6 else 6)
                    for idx, opt in enumerate(poll.options):
                        with opt_cols[idx % 6]:
                            st.markdown('<div style="text-align: center; border: 1px solid rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05);">', unsafe_allow_html=True)
                            if opt.symbol_image_url and os.path.exists(opt.symbol_image_url):
                                st.image(opt.symbol_image_url, width=60)
                            st.write(f"**{opt.name}**")
                            # Delete Option Button
                            if st.button("🗑️", key=f"del_opt_{opt.id}", help=f"Remove {opt.name}"):
                                db.delete(opt)
                                db.commit(); st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                
                # Add Option Section (Now Always Visible)
                st.write("")
                st.write("**➕ Add Party/Alliance to this Contest**")
                with st.form(f"add_opt_form_{poll.id}", clear_on_submit=True):
                    ao_col1, ao_col2, ao_col3 = st.columns([2, 1, 2])
                    with ao_col1:
                        ao_name = st.text_input("Party/Alliance Name*", placeholder="e.g. DMK, ADMK, etc.")
                    with ao_col2:
                        ao_color = st.color_picker("Bar Color", value="#00d4ff")
                    with ao_col3:
                        ao_sym = st.file_uploader("Upload Symbol Image*", type=["png", "jpg", "jpeg"], key=f"sym_up_{poll.id}")
                    
                    if st.form_submit_button("Add Party to Contest"):
                        if not ao_name:
                            st.error("Party name is required")
                        else:
                            sym_path = None
                            if ao_sym:
                                if not os.path.exists("images/polls"): os.makedirs("images/polls", exist_ok=True)
                                sym_path = f"images/polls/opt_{poll.id}_{ao_sym.name}"
                                with open(sym_path, "wb") as f: f.write(ao_sym.getbuffer())
                            
                            new_opt = OpinionPollOption(
                                poll_id=poll.id, 
                                name=ao_name, 
                                symbol_image_url=sym_path, 
                                color=ao_color
                            )
                            db.add(new_opt)
                            db.commit()
                            st.success(f"{ao_name} added successfully!")
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif choice == t("admin_panel") and user and user['role'] == 'admin':
    st.title(t("admin_panel"))
    
    admin_tab = st.tabs([t("alliances"), t("parties")])
    
    db = next(get_db())
    
    with admin_tab[0]:
        st.info(f"{t('alliances')} management has been moved to the '{t('alliances')}' menu.")
        if st.button(f"Go to {t('alliances')}"):
            st.write(f"Please select '{t('alliances')}' from the sidebar.")
            
    with admin_tab[1]:
        st.info(f"{t('parties')} management has been moved to the '{t('parties')}' menu.")
        if st.button(f"Go to {t('parties')}"):
            st.write(f"Please select '{t('parties')}' from the sidebar.")
