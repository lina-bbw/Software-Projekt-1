# services/lern_tag_service.py

from datenbank.lern_tag_repository import LernTagRepository


class LernTagService:
    """
    Service für Streaks / Lerntage.
    """

    def __init__(self):
        self.repo = LernTagRepository()

    def uebung_heute_markieren(self, benutzer_id: int) -> None:
        """
        Wird aufgerufen, sobald der Benutzer heute geübt hat.
        """
        self.repo.markiere_heute(benutzer_id)

    def streak_holen(self, benutzer_id: int) -> int:
        """
        Gibt die aktuelle Streak zurück (wie viele Tage in Folge geübt wurde).
        """
        return self.repo.berechne_streak(benutzer_id)