from app.schemas.auth import LoginRequest, MeResponse
from app.schemas.booking import BookingCreateRequest, BookingResponse, BookingUpdateRequest
from app.schemas.consulting_room import (
    ConsultingRoomCreateRequest,
    ConsultingRoomResponse,
    ConsultingRoomUpdateRequest,
    RoomOperatingHourCreateRequest,
    RoomOperatingHourResponse,
    RoomOperatingHourUpdateRequest,
)
from app.schemas.location import LocationCreateRequest, LocationResponse, LocationUpdateRequest
from app.schemas.professional import ProfessionalResponse, ProfessionalSyncResponse
from app.schemas.setup import BootstrapAdminRequest
from app.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from app.schemas.weekly_assignment import WeeklyAssignmentCreateRequest, WeeklyAssignmentResponse

__all__ = [
    "LoginRequest",
    "MeResponse",
    "BootstrapAdminRequest",
    "UserCreateRequest",
    "UserUpdateRequest",
    "UserResponse",
    "LocationCreateRequest",
    "LocationUpdateRequest",
    "LocationResponse",
    "ConsultingRoomCreateRequest",
    "ConsultingRoomUpdateRequest",
    "ConsultingRoomResponse",
    "RoomOperatingHourCreateRequest",
    "RoomOperatingHourUpdateRequest",
    "RoomOperatingHourResponse",
    "ProfessionalResponse",
    "ProfessionalSyncResponse",
    "BookingCreateRequest",
    "BookingUpdateRequest",
    "BookingResponse",
    "WeeklyAssignmentCreateRequest",
    "WeeklyAssignmentResponse",
]

