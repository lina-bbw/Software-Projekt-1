# datenbank/vokabel_repository.py

from typing import List, Optional
from datenbank.datenbank_verbindung import hole_datenbank_verbindung
from modelle.vokabel import Vokabel


class VokabelRepository:
    """
    Verwaltet die Vokabel-Datensätze in der Datenbank.
    """

    def vokabel_anlegen(
        self,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        set_id: int | None,
    ) -> None:
        """
        Legt eine neue Vokabel für einen Benutzer an.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            INSERT INTO vokabel (benutzer_id, wort, uebersetzung, beispielsatz, set_id)
            VALUES (?, ?, ?, ?, ?);
            """,
            (benutzer_id, wort, uebersetzung, beispielsatz, set_id),
        )

        verbindung.commit()
        verbindung.close()

    def hole_alle_vokabeln_fuer_benutzer(
        self, benutzer_id: int, set_id: int | None = None
    ) -> List[Vokabel]:
        """
        Lädt alle Vokabeln eines Benutzers.
        Optional: nur Vokabeln eines bestimmten Sets.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        sql = """
            SELECT v.id,
                   v.benutzer_id,
                   v.wort,
                   v.uebersetzung,
                   v.beispielsatz,
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

        vokabel_liste: List[Vokabel] = []
        for zeile in zeilen:
            vokabel = Vokabel(
                vokabel_id=zeile["id"],
                benutzer_id=zeile["benutzer_id"],
                wort=zeile["wort"],
                uebersetzung=zeile["uebersetzung"],
                beispielsatz=zeile["beispielsatz"],
                status=zeile["status"],
                set_id=zeile["set_id"],
                set_name=zeile["set_name"],
            )
            vokabel_liste.append(vokabel)

        return vokabel_liste

    def hole_vokabel_nach_id(self, vokabel_id: int) -> Optional[Vokabel]:
        """
        Lädt eine einzelne Vokabel anhand ihrer ID.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            SELECT v.id,
                   v.benutzer_id,
                   v.wort,
                   v.uebersetzung,
                   v.beispielsatz,
                   v.status,
                   v.set_id,
                   s.name AS set_name
            FROM vokabel v
            LEFT JOIN vokabel_set s ON v.set_id = s.id
            WHERE v.id = ?;
            """,
            (vokabel_id,),
        )

        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return None

        return Vokabel(
            vokabel_id=zeile["id"],
            benutzer_id=zeile["benutzer_id"],
            wort=zeile["wort"],
            uebersetzung=zeile["uebersetzung"],
            beispielsatz=zeile["beispielsatz"],
            status=zeile["status"],
            set_id=zeile["set_id"],
            set_name=zeile["set_name"],
        )

    def aktualisiere_vokabel(
        self,
        vokabel_id: int,
        neues_wort: str,
        neue_uebersetzung: str,
        neuer_beispielsatz: str | None,
        neues_set_id: int | None,
    ) -> None:
        """
        Aktualisiert die Daten einer Vokabel.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            UPDATE vokabel
            SET wort = ?,
                uebersetzung = ?,
                beispielsatz = ?,
                set_id = ?
            WHERE id = ?;
            """,
            (neues_wort, neue_uebersetzung, neuer_beispielsatz, neues_set_id, vokabel_id),
        )

        verbindung.commit()
        verbindung.close()

    def vokabel_loeschen(self, vokabel_id: int) -> None:
        """
        Löscht eine Vokabel endgültig.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            "DELETE FROM vokabel WHERE id = ?;",
            (vokabel_id,),
        )

        verbindung.commit()
        verbindung.close()

    def aktualisiere_status(self, vokabel_id: int, neuer_status: str) -> None:
        """
        Setzt den Lernstatus einer Vokabel (z. B. 'sicher' oder 'unsicher').
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            UPDATE vokabel
            SET status = ?
            WHERE id = ?;
            """,
            (neuer_status, vokabel_id),
        )

        verbindung.commit()
        verbindung.close()
