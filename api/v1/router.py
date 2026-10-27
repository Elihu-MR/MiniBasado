from fastapi import APIRouter

from api.v1.ai_chat_log_api import router as ai_chat_log_router
from api.v1.camera_api import router as camera_router
from api.v1.camera_event_api import router as camera_event_router
from api.v1.emergency_contact_api import router as emergency_contact_router
from api.v1.food_api import router as food_router
from api.v1.food_image_api import router as food_image_router
from api.v1.location_api import router as location_router
from api.v1.purchase_ticket_api import router as purchase_ticket_router
from api.v1.refrigerator_api import router as refrigerator_router
from api.v1.sensor_api import router as sensor_router
from api.v1.sensor_reading_api import router as sensor_reading_router
from api.v1.user_api import router as user_router

router = APIRouter()
router.include_router(user_router)
router.include_router(refrigerator_router)
router.include_router(food_router)
router.include_router(location_router)
router.include_router(purchase_ticket_router)
router.include_router(food_image_router)
router.include_router(sensor_router)
router.include_router(camera_router)
router.include_router(camera_event_router)
router.include_router(sensor_reading_router)
router.include_router(emergency_contact_router)
router.include_router(ai_chat_log_router)