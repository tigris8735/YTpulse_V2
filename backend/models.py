# backend/models.py
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey,
    JSON, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    plan = Column(String(20), nullable=False, default="free")
    pro_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("GenerationJob", back_populates="user", cascade="all, delete-orphan")


class TrendsCache(Base):
    __tablename__ = "trends_cache"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # qqqqqqq
    filter = Column(String(20), nullable=False, index=True)
    region = Column(String(5), nullable=False, default="US")
    youtube_json = Column(JSON, nullable=False)
    fetched_at = Column(DateTime, nullable=False, default=utc_now)

    __table_args__ = (
        Index("idx_trends_filter_region", "filter", "region"),
    )


class PreviewTags(Base):
    __tablename__ = "preview_tags"

    video_id = Column(String, primary_key=True)
    face_closeup = Column(Boolean, default=False)
    high_contrast = Column(Boolean, default=False)
    text_area = Column(Boolean, default=False)
    center_object = Column(Boolean, default=False)
    score_sum = Column(Integer, default=0)
    analyzed_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # thumb / video
    status = Column(String(20), nullable=False, default="queued")
    prompt_text = Column(Text, nullable=True)
    file_url = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="jobs")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    yookassa_id = Column(String(100), unique=True, nullable=False)
    term = Column(String(20), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    raw_webhook = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="payments")