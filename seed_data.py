from datetime import datetime
from cb_models import Article
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///crystalball.db")
Session = sessionmaker(bind=engine)
session = Session()

# Clear old articles first
session.query(Article).delete()

# Add test articles with IDs
articles = [
    Article(
        id=1,
        headline="LIKELY: Team A wins championship",
        label="LIKELY",
        section="sports",
        probability=0.62,
        body_paragraph_1="Team A has been dominant all season, making this outcome very probable.",
        body_paragraph_2="Factors like injuries, coaching, and public betting trends may have increased confidence in this outcome.",
        created_at=datetime.utcnow()
    ),
    Article(
        id=2,
        headline="TRENDING: Will X win election??",
        label="TRENDING",
        section="politics",
        probability=0.58,
        body_paragraph_1="Candidate X's chances have surged due to recent polling shifts.",
        body_paragraph_2="Media coverage, debates, and major endorsements likely drove the rapid increase in predicted probability.",
        created_at=datetime.utcnow()
    )
]

session.add_all(articles)
session.commit()
session.close()

print("Seed data added successfully with IDs!")
