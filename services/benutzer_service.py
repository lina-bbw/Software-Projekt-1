# services/benutzer_service.py

import random

from datenbank.benutzer_repository import BenutzerRepository
from modelle.benutzer import Benutzer

# Import robust machen (VSCode/Startpfad-Probleme abfangen)
try:
    from sicherheit.passwort_hasher import PasswortHasher
except ModuleNotFoundError:
    # Fallback: wenn Python den Projekt-Root nicht sauber als Suchpfad hat
    from ..sicherheit.passwort_hasher import PasswortHasher  # type: ignore


class BenutzerService:
    """
    Logik für Registrierung, Login und Passwort-Reset.
    """

    def __init__(self):
        self.benutzer_repository = BenutzerRepository()

    def registriere_neuen_benutzer(self, email: str, passwort: str) -> bool:
        if not email or not passwort:
            return False

        passwort_hash = PasswortHasher.erstelle_hash(passwort)
        return self.benutzer_repository.benutzer_anlegen(email, passwort_hash)

    def melde_benutzer_an(self, email: str, passwort: str):
        zeile = self.benutzer_repository.hole_benutzer_daten_per_email(email)
        if zeile is None:
            return None

        gespeicherter_hash = zeile["passwort_hash"]
        if not PasswortHasher.pruefe_passwort(passwort, gespeicherter_hash):
            return None

        return Benutzer(benutzer_id=zeile["id"], email=zeile["email"])

    def reset_code_erstellen(self, email: str) -> str | None:
        """
        Demo: Erzeugt einen 6-stelligen Code und speichert ihn.
        """
        zeile = self.benutzer_repository.hole_benutzer_daten_per_email(email)
        if zeile is None:
            return None

        code = f"{random.randint(100000, 999999)}"
        self.benutzer_repository.speichere_reset_code(email, code)
        return code

    def passwort_zuruecksetzen(self, email: str, code: str, neues_passwort: str) -> bool:
        if not email or not code or not neues_passwort:
            return False

        ok = self.benutzer_repository.pruefe_reset_code(email, code)
        if not ok:
            return False

        neuer_hash = PasswortHasher.erstelle_hash(neues_passwort)
        return self.benutzer_repository.setze_passwort_hash(email, neuer_hash)