from enum import Enum


class OrganizationType(str, Enum):
    INVESTOR = "investor"
    STARTUP = "startup"
    INCUBATOR = "incubator"
    ACCELERATOR = "accelerator"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"