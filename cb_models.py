from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ----------------------------
# BASE SETUP
# ----------------------------
Base = declarative_base()


# ----------------------------
# ARTICLES TABLE
# ----------------------------
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    headline = Column(String, unique=True)
    label = Column(String)  # LIKELY / TRENDING
    section = Column(String)  # politics, sports, etc
    probability = Column(Float)
    content = Column(String)  # generated two-paragraph article
    last_updated = Column(DateTime, default=datetime.utcnow)


# ----------------------------
# HISTORICAL PROBABILITY TABLE
# ----------------------------
class ProbabilityHistory(Base):
    __tablename__ = "probability_history"

    id = Column(Integer, primary_key=True)
    market_name = Column(String)  # name of the market/event
    probability = Column(Float)  # recorded probability
    timestamp = Column(DateTime, default=datetime.utcnow)


# ----------------------------
# DATABASE ENGINE + SESSION
# ----------------------------
engine = create_engine("sqlite:///crystalball.db")
SessionLocal = sessionmaker(bind=engine)

# ----------------------------
# CREATE TABLES IF NOT EXIST
# ----------------------------
Base.metadata.create_all(engine)
