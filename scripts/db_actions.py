import os
from dotenv import load_dotenv
import psycopg
from sqlalchemy import create_engine, String, Integer, select, insert, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(25))

    def __repr__(self) -> str:
        return f"Users(id={self.id!r}, name={self.name!r}, email={self.email!r}, password={self.password!r})"
    
def add_user(un, em, pswd):
    with Session(engine) as session:
        new_user = Users(
            name=un,
            email=em,
            password=pswd
        )
        session.add(new_user)
        session.commit()
