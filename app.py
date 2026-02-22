from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cb_models import Base, Article  # make sure your models file is named cb_models.py

app = FastAPI()

# Database setup
engine = create_engine("sqlite:///crystalball.db")
Session = sessionmaker(bind=engine)

# Templates
templates = Jinja2Templates(directory="templates")

# Root page - serves the HTML
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Feed endpoint - returns all articles
@app.get("/feed")
def feed():
    session = Session()
    articles = session.query(Article).all()
    session.close()
    # Return only the fields needed for the feed
    return [{"id": a.id, "headline": a.headline, "label": a.label, "section": a.section} for a in articles]

# Article endpoint - returns full article by ID
@app.get("/article/{article_id}")
def get_article(article_id: int):
    session = Session()
    article = session.query(Article).filter(Article.id == article_id).first()
    session.close()
    if article:
        return {
            "headline": article.headline,
            "label": article.label,
            "section": article.section,
            "body_paragraph_1": article.body_paragraph_1,
            "body_paragraph_2": article.body_paragraph_2,
        }
    return {"error": "Article not found"}
