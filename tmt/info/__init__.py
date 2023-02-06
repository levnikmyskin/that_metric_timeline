import enum


class Versions(str, enum.Enum):
    ZERO_SEVENTEEN = "0.1.7"
    ZERO_EIGHTEEN = "0.1.8"

    @staticmethod
    def get_last() -> str:
        return Versions.ZERO_EIGHTEEN


__version__ = Versions.get_last()
