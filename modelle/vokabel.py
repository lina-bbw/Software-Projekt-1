# modelle/vokabel.py

class Vokabel:
    """
    Repräsentiert eine einzelne Vokabel.

    status:
      - neu
      - unsicher
      - sicher
    """

    def __init__(
        self,
        vokabel_id: int,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        bemerkungen: str | None,
        status: str,
        set_id: int | None = None,
        set_name: str | None = None,
    ):
        self.id = vokabel_id
        self.benutzer_id = benutzer_id
        self.wort = wort
        self.uebersetzung = uebersetzung
        self.beispielsatz = beispielsatz
        self.bemerkungen = bemerkungen
        self.status = status
        self.set_id = set_id
        self.set_name = set_name

    def __str__(self) -> str:
        return f"{self.wort} -> {self.uebersetzung} ({self.status})"