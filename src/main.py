from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
import os

app = FastAPI()

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: str
    domain: str

engine = create_engine("sqlite:///users.db")

SQLModel.metadata.create_all(engine)

# Only for testing we add later a endpoint for user creating
user1 = Users(user="tim", domain="bot-tec.de")

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

@app.get("/check")
def check_domain(domain: str):
    with Session(engine) as session:
        session.add(user1)
        session.commit()
        statement = select(Users).where(Users.domain == domain)
        results = session.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="Domain not found")

        user = results[0].user

        symlink(domain, user)

        return {"domain": domain}
