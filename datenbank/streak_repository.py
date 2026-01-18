# datenbank/streak_repository.py

from datetime import date, timedelta
from datenbank.datenbank_verbindung import hole_datenbank_verbindung


class StreakRepository:
    """
    Speichert pro Benutzer:
    - aktueller_streak (int)
    - letzter_uebungstag (YYYY-MM-DD)

    Streak-Regel:
    - Wenn heute schon geübt -> keine Änderung
    - Wenn gestern zuletzt geübt -> streak + 1
    - Sonst -> streak = 1
    """

    def hole_streak_info(self, benutzer_id: int) -> tuple[int, str | None]:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "SELECT aktueller_streak, letzter_uebungstag FROM benutzer_streak WHERE benutzer_id = ?;",
            (benutzer_id,),
        )
        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return 0, None

        return int(zeile["aktueller_streak"]), zeile["letzter_uebungstag"]

    def uebung_heute_markieren(self, benutzer_id: int) -> None:
        """
        Wird aufgerufen, wenn der Benutzer etwas übt (Karteikarten oder Quiz).
        """
        heute = date.today()
        gestern = heute - timedelta(days=1)

        aktueller_streak, letzter_tag = self.hole_streak_info(benutzer_id)

        if letzter_tag == heute.isoformat():
            # heute bereits gezählt
            return

        if letzter_tag == gestern.isoformat():
            neuer_streak = aktueller_streak + 1
        else:
            neuer_streak = 1

        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        # Upsert: wenn Datensatz existiert -> update, sonst insert
        cursor.execute(
            """
            INSERT INTO benutzer_streak (benutzer_id, aktueller_streak, letzter_uebungstag)
            VALUES (?, ?, ?)
            ON CONFLICT(benutzer_id) DO UPDATE SET
                aktueller_streak = excluded.aktueller_streak,
                letzter_uebungstag = excluded.letzter_uebungstag;
            """,
            (benutzer_id, neuer_streak, heute.isoformat()),
        )

        verbindung.commit()
        verbindung.close()