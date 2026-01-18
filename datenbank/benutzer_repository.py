# datenbank/benutzer_repository.py

from datenbank.datenbank_verbindung import hole_datenbank_verbindung


class BenutzerRepository:
    """
    SQL-Operationen für Benutzer:
    - anlegen
    - per email holen
    - passwort ändern
    - reset-code speichern / prüfen
    """

    def benutzer_anlegen(self, email: str, passwort_hash: str) -> bool:
        try:
            verbindung = hole_datenbank_verbindung()
            cursor = verbindung.cursor()

            cursor.execute(
                "INSERT INTO benutzer (email, passwort_hash) VALUES (?, ?);",
                (email, passwort_hash),
            )

            verbindung.commit()
            verbindung.close()
            return True
        except Exception:
            return False

    def hole_benutzer_daten_per_email(self, email: str):
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "SELECT id, email, passwort_hash FROM benutzer WHERE email = ?;",
            (email,),
        )
        zeile = cursor.fetchone()
        verbindung.close()
        return zeile

    def setze_passwort_hash(self, email: str, neuer_hash: str) -> bool:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "UPDATE benutzer SET passwort_hash = ? WHERE email = ?;",
            (neuer_hash, email),
        )

        verbindung.commit()
        aenderungen = cursor.rowcount
        verbindung.close()
        return aenderungen > 0

    def speichere_reset_code(self, email: str, code: str) -> None:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "INSERT INTO passwort_reset (email, code) VALUES (?, ?);",
            (email, code),
        )

        verbindung.commit()
        verbindung.close()

    def pruefe_reset_code(self, email: str, code: str) -> bool:
        """
        Prüft, ob der letzte gespeicherte Code für diese E-Mail übereinstimmt.
        (Studentische Lösung: ohne Ablaufzeit)
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            SELECT code
            FROM passwort_reset
            WHERE email = ?
            ORDER BY id DESC
            LIMIT 1;
            """,
            (email,),
        )

        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return False

        return zeile["code"] == code