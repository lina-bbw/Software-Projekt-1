# modelle/vokabel.py


class Vokabel:
    
    # Repräsentiert eine einzelne Vokabel eines Benutzers.
    

    def __init__(
        self,
        vokabel_id: int,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        status: str,
        set_id: int | None = None,
        set_name: str | None = None,
    ):
        self.id = vokabel_id
        self.benutzer_id = benutzer_id
        self.wort = wort
        self.uebersetzung = uebersetzung
        self.beispielsatz = beispielsatz
        self.status = status
        self.set_id = set_id
        self.set_name = set_name

    def __str__(self) -> str:
        set_anzeige = f" | Set: {self.set_name}" if self.set_name else ""
        return f"{self.wort} -> {self.uebersetzung} ({self.status}){set_anzeige}"
