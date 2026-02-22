from sqlalchemy import create_engine
from cb_models import Base

engine = create_engine("sqlite:///crystalball.db")
Base.metadata.create_all(engine)

print("Database created!")
