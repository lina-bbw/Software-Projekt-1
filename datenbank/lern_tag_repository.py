# datenbank/lern_tag_repository.py

from datetime import date, timedelta
from datenbank.datenbank_verbindung import hole_datenbank_verbindung


class LernTagRepository:
    """
    Speichert pro Benutzer pro Tag genau einen Eintrag.
    Aus diesen Tagen berechnen wir die Streak.
    """

    def markiere_heute(self, benutzer_id: int) -> None:
        heute = date.today().isoformat()

        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO lern_tag (benutzer_id, datum)
            VALUES (?, ?);
            """,
            (benutzer_id, heute),
        )

        verbindung.commit()
        verbindung.close()

    def berechne_streak(self, benutzer_id: int) -> int:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "SELECT datum FROM lern_tag WHERE benutzer_id = ? ORDER BY datum DESC;",
            (benutzer_id,),
        )
        zeilen = cursor.fetchall()
        verbindung.close()

        if not zeilen:
            return 0

        gelernt = {z["datum"] for z in zeilen}

        streak = 0
        tag = date.today()
        while tag.isoformat() in gelernt:
            streak += 1
            tag = tag - timedelta(days=1)

        return streak