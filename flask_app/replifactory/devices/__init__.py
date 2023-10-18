

class Device:

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def connect(self, reset: bool = True):
        if reset:
            self.reset()
        self.configure()

    def disconnect(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def configure(self):
        raise NotImplementedError()

    def test(self):
        raise NotImplementedError()
