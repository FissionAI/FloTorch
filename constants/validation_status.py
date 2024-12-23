from enum import Enum

class ValidationStatus(Enum):
    QUEUED = "queued"
    INPROGRESS = "inprogress"
    FAILED = "failed"
    COMPLETED = "completed"