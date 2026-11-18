from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel


class AlertLevel(str, Enum):
    OFF = "off"
    NOTIFICATION = "notification"
    WARNING = "warning"
    CRITICAL = "critical"


class BolusStatus(str, Enum):
    PUMP_OFF = "pump_off"
    LIMIT_CHECK = "limit_check"
    ALLOWED = "allowed"
    WITH_WARNING = "with_warning"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"


class GlucoseLevel(str, Enum):
    NORMAL = "normal"
    LOW = "low"
    HIGH = "high"


class PumpStateResponse(BaseModel):
    is_on: Optional[bool] = None
    current_glucose_value: Optional[float] = None
    glucose_level: Optional[GlucoseLevel] = None
    alert_level: Optional[AlertLevel] = None
    bolus_status: Optional[BolusStatus] = None
    basal_speed_pc: Optional[int] = None
    manual_action_required: Optional[bool] = None
    message: Optional[str] = None
    action_message: Optional[str] = None
    alerts_count: int = 0


class AlertRequest(BaseModel):
    level: AlertLevel = AlertLevel.OFF
    level_str: str = ""
    message: str = ""
    action_message: str = ""
    timestamp: Union[datetime, str]


class AlertResponse(BaseModel):
    level: AlertLevel
    level_str: str = ""
    message: str = ""
    action_message: str = ""
    timestamp: datetime


class BolusDeliverResponse(BaseModel):
    status: str
    message: str


class ResetBlockResponse(BaseModel):
    status: str
    message: str


class ValidationErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: List[ValidationErrorDetail]