from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    robot_folder = Column(String, unique=True, index=True)

    users = relationship("UserRobot", back_populates="robot")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String, default="user")

    # Relation avec les liaisons utilisateur-robot
    robots = relationship("UserRobot", back_populates="user")

class UserRobot(Base):
    __tablename__ = "user_robots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    robot_id = Column(Integer, ForeignKey("robots.id"))

    # Relations vers User et Robot
    user = relationship("User", back_populates="robots")
    robot = relationship("Robot", back_populates="users")
