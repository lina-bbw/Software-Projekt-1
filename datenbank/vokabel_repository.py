# datenbank/vokabel_repository.py

from typing import List
from datenbank.datenbank_verbindung import hole_datenbank_verbindung
from modelle.vokabel import Vokabel


class VokabelRepository:
    """
    SQL-Operationen rund um Vokabeln.
    """

    def vokabel_anlegen(
        self,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        bemerkungen: str | None,
        set_id: int | None,
    ) -> None:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            INSERT INTO vokabel (benutzer_id, wort, uebersetzung, beispielsatz, bemerkungen, set_id)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (benutzer_id, wort, uebersetzung, beispielsatz, bemerkungen, set_id),
        )

        verbindung.commit()
        verbindung.close()

    def hole_alle_vokabeln_fuer_benutzer(
        self, benutzer_id: int, set_id: int | None = None
    ) -> List[Vokabel]:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        sql = """
            SELECT v.id,
                   v.benutzer_id,
                   v.wort,
                   v.uebersetzung,
                   v.beispielsatz,
                   v.bemerkungen,
                   v.status,
                   v.set_id,
                   s.name AS set_name
            FROM vokabel v
            LEFT JOIN vokabel_set s ON v.set_id = s.id
            WHERE v.benutzer_id = ?
        """
        parameter = [benutzer_id]

        if set_id is not None:
            sql += " AND v.set_id = ?"
            parameter.append(set_id)

        sql += " ORDER BY v.erstellt_am;"

        cursor.execute(sql, parameter)
        zeilen = cursor.fetchall()
        verbindung.close()

        vokabeln: List[Vokabel] = []
        for z in zeilen:
            vokabeln.append(
                Vokabel(
                    vokabel_id=z["id"],
                    benutzer_id=z["benutzer_id"],
                    wort=z["wort"],
                    uebersetzung=z["uebersetzung"],
                    beispielsatz=z["beispielsatz"],
                    bemerkungen=z["bemerkungen"],
                    status=z["status"],
                    set_id=z["set_id"],
                    set_name=z["set_name"],
                )
            )
        return vokabeln

    def aktualisiere_vokabel(
        self,
        vokabel_id: int,
        neues_wort: str,
        neue_uebersetzung: str,
        neuer_beispielsatz: str | None,
        neue_bemerkungen: str | None,
        neues_set_id: int | None,
    ) -> None:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            UPDATE vokabel
            SET wort = ?,
                uebersetzung = ?,
                beispielsatz = ?,
                bemerkungen = ?,
                set_id = ?
            WHERE id = ?;
            """,
            (neues_wort, neue_uebersetzung, neuer_beispielsatz, neue_bemerkungen, neues_set_id, vokabel_id),
        )

        verbindung.commit()
        verbindung.close()

    def vokabel_loeschen(self, vokabel_id: int) -> None:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute("DELETE FROM vokabel WHERE id = ?;", (vokabel_id,))

        verbindung.commit()
        verbindung.close()

    def aktualisiere_status(self, vokabel_id: int, neuer_status: str) -> None:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "UPDATE vokabel SET status = ? WHERE id = ?;",
            (neuer_status, vokabel_id),
        )

        verbindung.commit()
        verbindung.close()

    def hole_alle_woerter(self, benutzer_id: int, set_id: int | None = None) -> list[str]:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        sql = "SELECT wort FROM vokabel WHERE benutzer_id = ?"
        parameter = [benutzer_id]
        if set_id is not None:
            sql += " AND set_id = ?"
            parameter.append(set_id)

        cursor.execute(sql + ";", parameter)
        zeilen = cursor.fetchall()
        verbindung.close()
        return [z["wort"] for z in zeilen]

    def hole_alle_uebersetzungen(self, benutzer_id: int, set_id: int | None = None) -> list[str]:
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        sql = "SELECT uebersetzung FROM vokabel WHERE benutzer_id = ?"
        parameter = [benutzer_id]
        if set_id is not None:
            sql += " AND set_id = ?"
            parameter.append(set_id)

        cursor.execute(sql + ";", parameter)
        zeilen = cursor.fetchall()
        verbindung.close()
        return [z["uebersetzung"] for z in zeilen]