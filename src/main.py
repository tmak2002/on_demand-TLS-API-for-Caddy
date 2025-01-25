from fastapi import FastAPI, HTTPException, BackgroundTasks
from sqlmodel import SQLModel, Session, select
import os
import tldextract
from models import Users
from database import engine

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def symlink(domain: str, user: str):
    path = f"/var/www/{user}/{domain}"
    if not os.path.exists(path):
        os.makedirs(path)
        os.chown(path, 1000, 1000)
        with open(os.path.join(path, "index.html"), "w") as f:
            f.write("<html><body>It works!</body></html>")
        os.chown(os.path.join(path, "index.html"), 1000, 1000)

    symlink_path = f"/var/www/{domain}"
    if not os.path.islink(symlink_path):
        os.symlink(path, symlink_path)

@app.post("/create")
def create(domain: str, user: str):
    with Session(engine) as session:
        statement = select(Users).where(Users.domain == domain)
        if session.exec(statement).first():
            raise HTTPException(status_code=400, detail="Domain already exists")

        session.add(Users(user=user, domain=domain))
        session.commit()

        user_directory = f"/var/www/{user}"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory)
            os.chown(user_directory, 1000, 1000)

    return {"message": f"User {user} and domain {domain} created successfully"}

@app.get("/check")
def check_domain(domain: str, background_tasks: BackgroundTasks):
    extracted = tldextract.extract(domain)
    main_domain = f"{extracted.domain}.{extracted.suffix}"

    with Session(engine) as session:
        statement = select(Users).where(Users.domain == main_domain)
        results = session.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="Main domain not found in database")

        user = results[0].user
        background_tasks.add_task(symlink, domain, user)

    return {"domain": domain}

