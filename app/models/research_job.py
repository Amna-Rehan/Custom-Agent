from sqlalchemy import Enum, ForeignKey, String

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base_model import BaseModel
from app.models.enums import JobStatus


class ResearchJob(BaseModel):
    __tablename__ = "research_jobs"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )

    query: Mapped[str] = mapped_column(
        String(500)
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
    )