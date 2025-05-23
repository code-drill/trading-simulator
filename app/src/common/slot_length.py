import enum


class SlotLength(enum.IntEnum):
    HOUR = 3600
    QUARTER = 1900

    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]

    def __str__(self):
        return self.value