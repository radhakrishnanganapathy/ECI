import streamlit as st
import pandas as pd
from database import init_db, get_db, User, Alliance, Party, Candidate, ElectionStat, hash_password, verify_password
from sqlalchemy.orm import Session
import os

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

# --- MAIN APP LOGIC ---

if st.session_state.user is None:
    st.title("🗳️ Election Stats & Info System")
    st.markdown("### Welcome to the most advanced election tracking platform.")
    
    tabs = st.tabs(["Login", "Sign Up"])
    
    with tabs[0]:
        st.subheader("Access Your Dashboard")
        col1, col2 = st.columns([1, 2])
        with col1:
             username = st.text_input("Username", key="login_user")
             password = st.text_input("Password", type="password", key="login_pass")
             if st.button("Login", key="login_btn"):
                db = next(get_db())
                user = db.query(User).filter(User.username == username).first()
                if user and verify_password(password, user.password_hash):
                    st.session_state.user = {
                        "username": user.username,
                        "role": user.role,
                        "id": user.id
                    }
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    
    with tabs[1]:
        st.subheader("Join the Platform")
        s_username = st.text_input("Username", key="signup_user")
        s_password = st.text_input("Password", type="password", key="signup_pass")
        
        if st.button("Register"):
            db = next(get_db())
            existing = db.query(User).filter(User.username == s_username).first()
            if existing:
                st.error("Username already exists")
            else:
                user = User(username=s_username, password_hash=hash_password(s_password), role="user")
                db.add(user)
                db.commit()
                st.success("Account created! Switch to Login tab to enter.")

else:
    # --- LOGGED IN UI ---
    user = st.session_state.user
    st.sidebar.success(f"Logged in as: {user['username']} ({user['role']})")
    if st.sidebar.button("Logout"):
        logout()
        
    st.sidebar.divider()
    
    # Navigation
    menu = ["Dashboard", "Alliances", "Candidates", "Election Stats"]
    if user['role'] == 'admin':
        menu.insert(3, "Manage Candidates")
        menu.append("Admin Panel")
        
    choice = st.sidebar.selectbox("Navigate", menu)
    
    if choice == "Dashboard":
        st.title(f"🚀 Election Dashboard")
        
        # Summary Stats
        db = next(get_db())
        total_alliances = db.query(Alliance).count()
        total_parties = db.query(Party).count()
        total_candidates = db.query(Candidate).count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="glass-card"><h3>Alliances</h3><h1>{total_alliances}</h1></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="glass-card"><h3>Parties</h3><h1>{total_parties}</h1></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="glass-card"><h3>Candidates</h3><h1>{total_candidates}</h1></div>', unsafe_allow_html=True)
            
        st.subheader("Recent Candidate Growth")
        # Placeholder for a chart
        chart_data = pd.DataFrame({
            'Year': [2014, 2019, 2024],
            'Candidates': [450, 520, 610]
        })
        st.line_chart(chart_data.set_index('Year'))

    elif choice == "Alliances":
        header_col1, header_col2 = st.columns([5, 1])
        with header_col1:
            st.title("🤝 Alliances")
        
        db = next(get_db())
        
        # Admin Add (+) Button
        if user['role'] == 'admin':
            with header_col2:
                if st.button("➕", help="Add New Alliance"):
                    st.session_state.show_add_alliance = True
            
            if st.session_state.get('show_add_alliance', False):
                with st.container():
                     st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                     st.subheader("Add New Alliance")
                     col1, col2 = st.columns(2)
                     with col1:
                         new_name = st.text_input("Alliance Name")
                         new_party = st.text_input("Primary Party")
                         new_leader = st.text_input("Leader")
                     with col2:
                         new_symbol = st.text_input("Symbol (Emoji or URL)")
                         new_seats = st.number_input("Seats Contested", min_value=0, step=1)
                         new_desc = st.text_area("Description")
                     
                     if st.button("Save Alliance"):
                         new_a = Alliance(
                             name=new_name, 
                             primary_party=new_party, 
                             leader=new_leader, 
                             symbol=new_symbol, 
                             seats_contested=new_seats,
                             description=new_desc
                         )
                         db.add(new_a)
                         db.commit()
                         st.success(f"Alliance {new_name} saved!")
                         st.session_state.show_add_alliance = False
                         st.rerun()
                     if st.button("Cancel"):
                         st.session_state.show_add_alliance = False
                         st.rerun()
                     st.markdown('</div>', unsafe_allow_html=True)

        # Filter
        all_alliances = db.query(Alliance).all()
        alliance_names = ["All"] + [a.name for a in all_alliances]
        selected_alliance = st.selectbox("Filter by Alliance Name", alliance_names)
        
        # Listing
        query = db.query(Alliance)
        if selected_alliance != "All":
            query = query.filter(Alliance.name == selected_alliance)
        
        display_alliances = query.all()
        
        for alliance in display_alliances:
            with st.expander(f"{alliance.symbol if alliance.symbol else '🤝'} {alliance.name}", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Primary Party:** {alliance.primary_party}")
                    st.write(f"**Leader:** {alliance.leader}")
                with col2:
                    st.write(f"**Seats Contested:** {alliance.seats_contested}")
                    st.write(f"**Symbol:** {alliance.symbol}")
                with col3:
                    st.write(f"**Description:** {alliance.description}")
                
                # Show member parties
                parties = db.query(Party).filter(Party.alliance_id == alliance.id).all()
                if parties:
                    st.divider()
                    st.subheader("Member Parties")
                    p_cols = st.columns(3)
                    for idx, party in enumerate(parties):
                        with p_cols[idx % 3]:
                            st.info(party.name)

    elif choice == "Candidates":
        st.title("👤 Candidate Profiles")
        db = next(get_db())
        
        col1, col2 = st.columns(2)
        with col1:
            party_filter = st.selectbox("Filter by Party", ["All"] + [p.name for p in db.query(Party).all()])
        with col2:
            all_constituencies = sorted(list(set([c.constituency for c in db.query(Candidate).all() if c.constituency])))
            const_filter = st.selectbox("Filter by Constituency", ["All"] + all_constituencies)
        
        query = db.query(Candidate)
        if party_filter != "All":
            party = db.query(Party).filter(Party.name == party_filter).first()
            if party:
                query = query.filter(Candidate.party_id == party.id)
        
        if const_filter != "All":
            query = query.filter(Candidate.constituency == const_filter)
            
        candidates = query.all()
        
        if not candidates:
            st.info("No candidates found.")
        else:
            for cand in candidates:
                with st.container():
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        if cand.image_url and os.path.exists(cand.image_url):
                            st.image(cand.image_url, width=150)
                        else:
                            st.markdown("### 👤")
                    with col2:
                        st.markdown(f"### {cand.name}")
                        st.write(f"**Party:** {cand.party.name if cand.party else 'N/A'}")
                        if cand.alliance:
                            st.write(f"**Alliance:** {cand.alliance.name}")
                        st.write(f"**Constituency:** {cand.constituency} ({cand.district if cand.district else 'N/A'})")
                        if cand.age:
                            st.write(f"**Age:** {cand.age}")
                        st.write(cand.bio)
                    with col3:
                        if cand.symbol_image_url and os.path.exists(cand.symbol_image_url):
                            st.image(cand.symbol_image_url, width=80)
                            st.caption(cand.symbol_name)
                        elif cand.symbol_name:
                            st.markdown(f"**Symbol:** {cand.symbol_name}")
                    st.markdown('</div>', unsafe_allow_html=True)
                st.write("")

    elif choice == "Manage Candidates" and user['role'] == 'admin':
        st.title("👤 Manage Candidates")
        db = next(get_db())
        
        # Reuse the add candidate form logic or move it here
        st.subheader("Add New Candidate")
        with st.form("add_candidate_form_dedicated", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Candidate Name*")
                c_age = st.number_input("Age (Optional)", min_value=18, max_value=120, value=None)
                parties = db.query(Party).all()
                c_party = st.selectbox("Select Party*", [p.name for p in parties])
                alliances = db.query(Alliance).all()
                c_alliance = st.selectbox("Select Alliance (Optional)", ["None"] + [a.name for a in alliances])
            
            with col2:
                c_const = st.text_input("Constituency*")
                c_dist = st.text_input("District*")
                c_sym_name = st.text_input("Symbol Name")
                c_sym_img = st.file_uploader("Upload Symbol Image", type=["png", "jpg", "jpeg"])
            
            c_bio = st.text_area("Bio (Background)")
            c_img = st.file_uploader("Upload Candidate Photo", type=["png", "jpg", "jpeg"])
            
            submitted = st.form_submit_button("Add Candidate")
            
            if submitted:
                if not c_name or not c_party or not c_const or not c_dist:
                    st.error("Please fill in all required fields (*)")
                else:
                    p_obj = db.query(Party).filter(Party.name == c_party).first()
                    a_obj = None
                    if c_alliance != "None":
                        a_obj = db.query(Alliance).filter(Alliance.name == c_alliance).first()
                    
                    sym_img_path = None
                    if c_sym_img:
                        if not os.path.exists("images"): os.makedirs("images")
                        sym_img_path = f"images/symbol_{c_sym_img.name}"
                        with open(sym_img_path, "wb") as f: f.write(c_sym_img.getbuffer())
                    
                    cand_img_path = None
                    if c_img:
                        if not os.path.exists("images"): os.makedirs("images")
                        cand_img_path = f"images/candidate_{c_img.name}"
                        with open(cand_img_path, "wb") as f: f.write(c_img.getbuffer())
                    
                    new_c = Candidate(
                        name=c_name, age=c_age, party_id=p_obj.id, 
                        alliance_id=a_obj.id if a_obj else None,
                        constituency=c_const, district=c_dist,
                        symbol_name=c_sym_name, symbol_image_url=sym_img_path,
                        bio=c_bio, image_url=cand_img_path
                    )
                    db.add(new_c)
                    db.commit()
                    st.success(f"Candidate {c_name} added successfully!")
                    st.rerun()

    elif choice == "Admin Panel" and user['role'] == 'admin':
        st.title("🛠️ Administration Control")
        
        admin_tab = st.tabs(["Manage Alliances", "Manage Parties"])
        
        db = next(get_db())
        
        with admin_tab[0]:
            st.info("Alliance management has been moved to the 'Alliances' menu for better accessibility.")
            if st.button("Go to Alliances Menu"):
                st.write("Please select 'Alliances' from the sidebar.")
                
        with admin_tab[1]:
            st.subheader("Add New Party")
            p_name = st.text_input("Party Name")
            alliances = db.query(Alliance).all()
            p_alliance = st.selectbox("Select Alliance", [a.name for a in alliances])
            p_desc = st.text_area("Party Description")
            if st.button("Add Party"):
                a_obj = db.query(Alliance).filter(Alliance.name == p_alliance).first()
                new_p = Party(name=p_name, alliance_id=a_obj.id, description=p_desc)
                db.add(new_p)
                db.commit()
                st.success(f"Party {p_name} added!")
                st.rerun()
