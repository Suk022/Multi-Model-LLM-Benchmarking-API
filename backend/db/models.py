from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid import UUID
from datetime import datetime
from .database import Base

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    prompt: Mapped[str] = mapped_column(Text)
    criteria: Mapped[str] = mapped_column(String)
    tier: Mapped[str] = mapped_column(String)
    total_duration_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    model_results: Mapped[list["ModelResult"]] = relationship(
        "ModelResult",
        back_populates="benchmark_run",
        cascade="all, delete-orphan"
    )

class ModelResult(Base):
    __tablename__ = "model_results"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    benchmark_id: Mapped[UUID] = mapped_column(ForeignKey("benchmark_runs.id"))
    model_key: Mapped[str] = mapped_column(String)
    api_name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    response_text: Mapped[str] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    benchmark_run: Mapped["BenchmarkRun"] = relationship(
        "BenchmarkRun",
        back_populates="model_results"
    )
