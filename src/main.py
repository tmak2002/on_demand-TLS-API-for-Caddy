from fastapi import FastAPI, HTTPException, BackgroundTasks
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
import os

from models import Users
from database import engine, get_session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def symlink(domain: str, user: str):
    path = "/var/www/" + user + "/" + domain
    if not os.path.exists(path):
        os.makedirs(path)
        os.chown(path, 1000, 1000)
        html_file_path = os.path.join(path, "index.html")
        with open(html_file_path, "w") as f:
            f.write("<html><body>It's works!</body></html>")
            os.chown(html_file_path, 1000, 1000)

    symlink_path = "/var/www/" + domain
    if not os.path.islink(symlink_path):
        os.symlink(path, symlink_path)

@app.post("/create")
def create(domain: str, user: str):
    with Session(engine) as session:
        statement = select(Users).where(Users.domain == domain)
        existing_domain = session.exec(statement).first()
        
        if existing_domain:
            raise HTTPException(status_code=400, detail="Domain already exists")
        new_user = Users(user=user, domain=domain)
        session.add(new_user)
        session.commit()

    user_directory = f"/var/www/" + user
    
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)
        os.chown(user_directory, 1000, 1000)

    return {"message": f"User {user} and domain {domain} created successfully"}

@app.get("/check")
def check_domain(domain: str, background_tasks: BackgroundTasks):
    with Session(engine) as session:
        statement = select(Users).where(Users.domain == domain)
        results = session.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="Domain not found")

        user = results[0].user

        background_tasks.add_task(symlink,domain, user)

        return {"domain": domain}
