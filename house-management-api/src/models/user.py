class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"