from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from siteDB import SessionLocal, engine, User
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/submit_username/")
def submit_username(username: str = Form(...), db: Session = Depends(get_db)):
    # Check if the username already exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Save the username to the database
    db_user = User(username=username)
    db.add(db_user)
    db.commit()

    # Use HTMLResponse with content type explicitly set
    return HTMLResponse(content=f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/user/{username}" />
    </head>
    <body>
        Redirecting...
    </body>
    </html>
    """, status_code=200, media_type="text/html")


def get_settings():
    return {"background_image": "/static/blurred-color-background-gradient-design_437781-1073.jpg"}


@app.get("/user/{username}", response_class=HTMLResponse)
def show_user_page(username: str, request: Request, db: Session = Depends(get_db), settings: dict = Depends(get_settings)):
    # Fetch user details from the database
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("user.html", {"request": request, "username": db_user.username, **settings})


@app.get("/quiz", response_class=HTMLResponse)
def show_quiz(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})


@app.post("/submit_quiz/")
def redirect_back(username: str = Form(...)):
    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/user/{username}" />
    </head>
    <body>
        Redirecting...
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, settings: dict = Depends(get_settings)):
    return templates.TemplateResponse("index.html", {"request": request, **settings})


@app.get("/user/{username}", response_class=HTMLResponse)
def show_user_page(username: str, request: Request, settings: dict = Depends(get_settings)):
    return templates.TemplateResponse("user.html", {"request": request, "username": username, **settings})


@app.get("/quiz", response_class=HTMLResponse)
def show_quiz(request: Request, settings: dict = Depends(get_settings)):
    return templates.TemplateResponse("quiz.html", {"request": request, **settings})