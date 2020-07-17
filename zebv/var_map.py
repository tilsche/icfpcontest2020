class VarMap:
    map: dict

    def __init__(self, map=None):
        if map:
            self.map = map
        else:
            self.map = {}

    def merge(self, other: "VarMap"):
        assert (set(self.map.keys()) & set(other.map.keys())) == set()
        map.update(other.map)
