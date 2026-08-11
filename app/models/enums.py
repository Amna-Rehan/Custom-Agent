from enum import Enum


class OrganizationType(str, Enum):
    INVESTOR = "investor"
    STARTUP = "startup"
    INCUBATOR = "incubator"
    ACCELERATOR = "accelerator"
    GRANT = "grant"
    PROGRAM = "program"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"


class SourceType(str, Enum):
    OFFICIAL = "official"
    APPLICATION = "application"
    GOVERNMENT = "government"
    PROGRAM = "program"
    DOCUMENTATION = "documentation"
    SECONDARY = "secondary"
