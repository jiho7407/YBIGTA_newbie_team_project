from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from app.user.user_schema import User

Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    email = Column(String(255), primary_key=True, index=True)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        user_db = self.db.query(UserDB).filter(UserDB.email == email).first()
        if user_db:
            return User(email=user_db.email, password=user_db.password, username=user_db.username)
        return None

    def save_user(self, user: User) -> User:
        user_db = self.db.query(UserDB).filter(UserDB.email == user.email).first()
        if user_db:
            user_db.password = user.password
            user_db.username = user.username
        else:
            user_db = UserDB(email=user.email, password=user.password, username=user.username)
            self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)
        return user

    def delete_user(self, user: User) -> User:
        user_db = self.db.query(UserDB).filter(UserDB.email == user.email).first()
        if user_db:
            self.db.delete(user_db)
            self.db.commit()
        return user
