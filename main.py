import psycopg
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, String, Integer, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

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

new_user_name = input("Enter a unique name for user: ")
new_users_email = input("Enter a unique email: ")
new_user_password = input("Enter the password for user: ")
new_user = Users(name=new_user_name, email=new_users_email, password=new_user_password)

if __name__ == "__main__":
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(new_user)
        session.commit()
        print(f"Created a new user {new_user_name}")
