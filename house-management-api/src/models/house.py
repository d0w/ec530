class House:
    def __init__(self, id: int, address: str, owner: str):
        self.id = id
        self.address = address
        self.owner = owner

    def update(self, address: str = None, owner: str = None):
        if address is not None:
            self.address = address
        if owner is not None:
            self.owner = owner