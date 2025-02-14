class Device:
    def __init__(self, id: int, name: str, room_id: int):
        self.id = id
        self.name = name
        self.room_id = room_id

    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, room_id={self.room_id})>"