import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(25))
    role: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"Users(id={self.id!r}, name={self.name!r}, password={self.password!r})"

def init_db():
    Base.metadata.create_all(engine)

def add_user(un, pswd, r):
    with Session(engine) as session:
        new_user = Users(
            name = un,
            password = pswd,
            role = r
        )
        session.add(new_user)
        session.commit()
