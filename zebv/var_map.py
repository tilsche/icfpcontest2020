class VarMap:
    mapping: dict

    def __init__(self, mapping=None):
        if mapping:
            self.mapping = mapping
        else:
            self.mapping = {}

    def __getitem__(self, item: int):
        return self.mapping[item]

    def merge(self, other: "VarMap"):
        assert not set(self.mapping.keys()).intersection(set(other.mapping.keys()))
        new_mapping = self.mapping.copy()
        new_mapping.update(other.mapping)
        return VarMap(new_mapping)
