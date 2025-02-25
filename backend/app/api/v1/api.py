from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, workouts, food, measurements, goals, social, notifications, search, admin

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
api_router.include_router(food.router, prefix="/food", tags=["food"])
api_router.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) 