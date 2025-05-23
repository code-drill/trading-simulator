import enum


class Country(enum.StrEnum):
    FI = "FI"
    SE = "SE"

    @classmethod
    def choices(cls):
        return [(e.value, e.name) for e in cls]

    def __str__(self):
        return self.value