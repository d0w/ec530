from fastapi import FastAPI
from src.api.routes.houses import houses_bp
from src.api.routes.users import users_bp
from src.api.routes.rooms import rooms_bp
from src.api.routes.devices import devices_bp

app = FastAPI()

app.include_router(houses_bp, prefix="/api/houses", tags=["houses"])
app.include_router(users_bp, prefix="/api/users", tags=["users"])
app.include_router(rooms_bp, prefix="/api/rooms", tags=["rooms"])
app.include_router(devices_bp, prefix="/api/devices", tags=["devices"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the House Management API"}