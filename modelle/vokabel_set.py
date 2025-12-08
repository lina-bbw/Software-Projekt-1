# modelle/vokabel_set.py


class VokabelSet:
    """
    Repräsentiert ein Set / Thema, z. B. 'Tiere', 'Farben', 'Urlaub'.
    """

    def __init__(self, set_id: int, benutzer_id: int, name: str):
        self.id = set_id
        self.benutzer_id = benutzer_id
        self.name = name

    def __str__(self) -> str:
        return f"Set(id={self.id}, name='{self.name}')"
