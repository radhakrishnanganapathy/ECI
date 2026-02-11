import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext

# Database Configuration
# You should set these environment variables or change them here
DB_USER = os.getenv("DB_USER", "neondb_owner")
DB_PASSWORD = os.getenv("DB_PASSWORD", "npg_u0kp8rHWZdDB")
DB_HOST = os.getenv("DB_HOST", "ep-crimson-frog-ah3d3dhp-pooler.c-3.us-east-1.aws.neon.tech")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "neondb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user") # 'admin' or 'user'

class Alliance(Base):
    __tablename__ = "alliances"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    name_ta = Column(String)
    full_name = Column(String)
    full_name_ta = Column(String)
    primary_party = Column(String)
    primary_party_ta = Column(String)
    symbol = Column(String)
    leader = Column(String)
    leader_ta = Column(String)
    seats_contested = Column(Integer)
    description = Column(Text)
    description_ta = Column(Text)
    election_type = Column(String) # 'state' or 'center'
    year = Column(Integer)
    logo_url = Column(String)
    created_at = Column(String)
    parties = relationship("Party", back_populates="alliance")
    members = relationship("AllianceParty", back_populates="alliance", cascade="all, delete-orphan")

class Party(Base):
    __tablename__ = "parties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    name_ta = Column(String)
    full_name = Column(String)
    full_name_ta = Column(String)
    leader = Column(String)
    leader_ta = Column(String)
    symbol_name = Column(String)
    symbol_name_ta = Column(String)
    symbol_image_url = Column(String)
    alliance_id = Column(Integer, ForeignKey("alliances.id"))
    seats_sharing = Column(Integer)
    state = Column(String) # For multiple states, stored as comma-separated
    description = Column(Text)
    description_ta = Column(Text)
    logo_url = Column(String)
    category = Column(String) # National, State, Unrecognized
    created_at = Column(String)
    alliance = relationship("Alliance", back_populates="parties")
    candidates = relationship("Candidate", back_populates="party")
    alliances_joined = relationship("AllianceParty", back_populates="party")

class AllianceParty(Base):
    __tablename__ = "alliance_parties"
    id = Column(Integer, primary_key=True, index=True)
    alliance_id = Column(Integer, ForeignKey("alliances.id"))
    party_id = Column(Integer, ForeignKey("parties.id"))
    seats_sharing_tn = Column(Integer)
    seats_sharing_py = Column(Integer)
    symbol_name = Column(String)
    symbol_name_ta = Column(String)
    symbol_image_url = Column(String)

    alliance = relationship("Alliance", back_populates="members")
    party = relationship("Party", back_populates="alliances_joined")

class Constituency(Base):
    __tablename__ = "constituencies"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String) # 'Tamil Nadu' or 'Pondicherry'
    district = Column(String)
    district_ta = Column(String)
    name = Column(String, index=True)
    name_ta = Column(String)
    total_voters = Column(Integer, default=0)
    male_voters = Column(Integer, default=0)
    female_voters = Column(Integer, default=0)
    third_gender_voters = Column(Integer, default=0)
    type = Column(String, default="General") # 'General' or 'Reserved'

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    name_ta = Column(String)
    age = Column(Integer, nullable=True)
    gender = Column(String) # 'Male', 'Female', 'Other'
    party_id = Column(Integer, ForeignKey("parties.id"))
    alliance_id = Column(Integer, ForeignKey("alliances.id"), nullable=True)
    constituency_id = Column(Integer, ForeignKey("constituencies.id"), nullable=True)
    constituency = Column(String) # Legacy text field
    district = Column(String) # Legacy text field
    symbol_name = Column(String)
    symbol_name_ta = Column(String)
    symbol_image_url = Column(String)
    bio = Column(Text)
    bio_ta = Column(Text)
    image_url = Column(String)
    election_link = Column(String) # New field
    created_at = Column(String)
    
    party = relationship("Party", back_populates="candidates")
    alliance = relationship("Alliance")
    constituency_rel = relationship("Constituency")
    stats = relationship("ElectionStat", back_populates="candidate")

class ElectionStat(Base):
    __tablename__ = "election_stats"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    year = Column(Integer)
    votes_received = Column(Integer)
    total_votes = Column(Integer)
    candidate = relationship("Candidate", back_populates="stats")

class OpinionPoll(Base):
    __tablename__ = "opinion_polls"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String) # Question or Poll Title
    start_datetime = Column(String) 
    end_datetime = Column(String)
    is_active = Column(Integer, default=0) # 0: stopped, 1: started
    show_on_dashboard = Column(Integer, default=0) # 0: hide, 1: show
    created_at = Column(String)
    
    options = relationship("OpinionPollOption", back_populates="poll", cascade="all, delete-orphan")

class OpinionPollOption(Base):
    __tablename__ = "opinion_poll_options"
    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("opinion_polls.id"))
    name = Column(String) # Party or Alliance Name
    symbol_image_url = Column(String)
    color = Column(String, default="#00d4ff")
    
    poll = relationship("OpinionPoll", back_populates="options")
    votes = relationship("PollVote", back_populates="option", cascade="all, delete-orphan")

class PollVote(Base):
    __tablename__ = "poll_votes"
    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("opinion_polls.id"))
    option_id = Column(Integer, ForeignKey("opinion_poll_options.id"))
    ip_address = Column(String)
    voted_at = Column(String)
    
    option = relationship("OpinionPollOption", back_populates="votes")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
