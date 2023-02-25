from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from src.structures.domain.devices.models import Device
from src.structures.domain.workers.models import Worker


class EventType(Enum):
    START = 0
    DATA = 1  # Maybe make district data events?
    END = 2
    RESULT = 3

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def max():
        return 3


class InspectionFailReason(Enum):
    ALCOHOL = 0
    PRESSURE = 1
    CONDITIONS = 2
    OTHER = 3

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def max():
        return 3


class Measurements(Enum):
    ALCOHOL = 0
    PRESSURE = 1
    CONDITIONS = 2
    HEADACHE = 3
    INJURIES = 4
    PULSE = 5
    SLEEP = 6
    FRACTURE = 7

    def __str__(self):
        return f"{self.name}"

    @staticmethod
    def max():
        return 7


class EventBase(BaseModel):
    inspection_id: str
    worker: Worker
    device: Device
    datetime: datetime


class Event(BaseModel):
    inspection_id: str
    worker_id: str
    device_id: str
    event_type: EventType
    event_data: dict
    datetime: datetime
