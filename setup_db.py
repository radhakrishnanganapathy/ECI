from database import SessionLocal, init_db, Alliance, Party, Candidate, User, hash_password

def populate_mock_data():
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).first():
        print("Database already populated.")
        return

    # Create Admin
    admin = User(
        username="admin", 
        password_hash=hash_password("admin123"), 
        role="admin"
    )
    db.add(admin)

    # Create Alliances
    alliance1 = Alliance(name="National Democratic Alliance", description="A center-right to right-right political alliance.")
    alliance2 = Alliance(name="United Progressive Alliance", description="A center-left political alliance.")
    db.add_all([alliance1, alliance2])
    db.commit()

    # Create Parties
    p1 = Party(name="BJP", alliance_id=alliance1.id, description="Bhartiya Janata Party")
    p2 = Party(name="INC", alliance_id=alliance2.id, description="Indian National Congress")
    p3 = Party(name="Independent", description="Unaffiliated parties")
    db.add_all([p1, p2, p3])
    db.commit()

    # Create Candidates
    c1 = Candidate(name="Narendra Modi", party_id=p1.id, constituency="Varanasi", bio="Prime Minister of India")
    c2 = Candidate(name="Rahul Gandhi", party_id=p2.id, constituency="Wayanad", bio="Leader of Opposition")
    db.add_all([c1, c2])
    db.commit()

    print("Sample data populated successfully!")
    db.close()

if __name__ == "__main__":
    init_db()
    populate_mock_data()
