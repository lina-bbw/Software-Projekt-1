# modelle/benutzer.py


class Benutzer:
    """
    Einfache Datenklasse für einen Benutzer.
    Enthält nur die wichtigsten Informationen, die wir im Programm nutzen.
    """
    
    def __init__(self, benutzer_id: int, email: str):
        self.id = benutzer_id
        self.email = email

    def __str__(self) -> str:
        return f"Benutzer(id={self.id}, email={self.email})"
