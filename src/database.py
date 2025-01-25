from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://api:api@postgres:5432/users"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    return Session(engine)

