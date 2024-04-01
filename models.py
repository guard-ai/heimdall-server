from dataclasses import dataclass
import uuid
from datetime import date


@dataclass
class Log:
    id: uuid.UUID
    region: str
    utterance: str
    created_at: date


@dataclass
class Event:
    id: uuid.UUID
    level: int
    location: str
    category: str
    log_id: uuid.UUID
    created_at: date
