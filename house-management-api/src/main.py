from fastapi import FastAPI
# from src.api.routes.houses import houses_bp
# from src.api.routes.users import users_bp
# from src.api.routes.rooms import rooms_bp
# from src.api.routes.devices import devices_bp
from src.api.routes import houses, users, rooms, devices
from src.core.config import settings
import logging

log_level = logging.DEBUG if settings.DEBUG else logging.INFO

logging.basicConfig(level=log_level)

app = FastAPI()

app.include_router(houses.router, prefix="/api/houses", tags=["houses"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(devices.router, prefix="/api/devices", tags=["devices"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the House Management API"}