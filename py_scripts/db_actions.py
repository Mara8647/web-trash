import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

load_dotenv()

DATABASE_URL = f"sqlite:///main.db"

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
    with engine.connect() as conn:
        admin_created = conn.execute(text("SELECT EXISTS(SELECT 1 FROM users WHERE role = 'admin')")).fetchone()[0]
        if admin_created == False:
            conn.execute(text(f"INSERT INTO users (id, name, password, role) VALUES (1, '{os.getenv("ADMIN_LOGIN")}', '{os.getenv("ADMIN_PASSWORD")}', 'admin');"))

        conn.commit()
    print("db was initialized")

def add_user(un, pswd, r):
    with Session(engine) as session:
        new_user = Users(
            name = un,
            password = pswd,
            role = r
        )
        session.add(new_user)
        session.commit()

def get_user(un, pswd):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT role FROM users WHERE name = '{un}' AND password = '{pswd}'"))
        role = result.scalar()

        return role