from enum import Enum


class FoodStatus(str, Enum):
    FRESH = "fresh"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    CONSUMED = "consumed"


class FoodImageType(str, Enum):
    FOOD = "food"
    TICKET = "ticket"
    OTHER = "other"


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WEIGHT = "weight"
    DOOR = "door"
    OTHER = "other"


class CameraEventType(str, Enum):
    MOTION = "motion"
    OPENED = "opened"
    CLOSED = "closed"
    OTHER = "other"


class EventSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"