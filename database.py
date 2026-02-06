import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext

# Database Configuration
# You should set these environment variables or change them here
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "redblox009")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "election2026")

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
    primary_party = Column(String)
    symbol = Column(String)
    leader = Column(String)
    seats_contested = Column(Integer)
    description = Column(Text)
    logo_url = Column(String)
    parties = relationship("Party", back_populates="alliance")

class Party(Base):
    __tablename__ = "parties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    alliance_id = Column(Integer, ForeignKey("alliances.id"))
    description = Column(Text)
    logo_url = Column(String)
    alliance = relationship("Alliance", back_populates="parties")
    candidates = relationship("Candidate", back_populates="party")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    party_id = Column(Integer, ForeignKey("parties.id"))
    constituency = Column(String)
    bio = Column(Text)
    image_url = Column(String)
    party = relationship("Party", back_populates="candidates")
    stats = relationship("ElectionStat", back_populates="candidate")

class ElectionStat(Base):
    __tablename__ = "election_stats"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    year = Column(Integer)
    votes_received = Column(Integer)
    total_votes = Column(Integer)
    candidate = relationship("Candidate", back_populates="stats")

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
