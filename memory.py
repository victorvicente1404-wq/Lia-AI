class Memory:
    def __init__(self):
        self.history = []

    def add(self, message: str):
        self.history.append(message)

    def get_last(self, n: int = 10) -> str:
        return "
".join(self.history[-n:])
