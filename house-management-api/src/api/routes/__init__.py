# filepath: /house-management-api/house-management-api/src/api/routes/__init__.py
from .houses import houses_bp
from .users import users_bp
from .rooms import rooms_bp
from .devices import devices_bp

__all__ = ['houses_bp', 'users_bp', 'rooms_bp', 'devices_bp']