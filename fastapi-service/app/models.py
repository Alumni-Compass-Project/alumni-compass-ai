from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, SmallInteger, String, Text

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    headline = Column(String(255))
    bio = Column(Text)
    university = Column(String(255))
    current_role = Column(String(255))
    graduation_year = Column(SmallInteger)


class MentorProfile(Base):
    __tablename__ = "mentor_profiles"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    years_experience = Column(SmallInteger, nullable=False, default=0)
    accepting_new_mentees = Column(Boolean, nullable=False, default=True)
    approval_status = Column(String(255), nullable=False)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


class MentorSkill(Base):
    __tablename__ = "mentor_skill"

    id = Column(BigInteger, primary_key=True)
    mentor_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    skill_id = Column(BigInteger, ForeignKey("skills.id"), nullable=False)
    proficiency = Column(SmallInteger)
