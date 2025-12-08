# datenbank/set_repository.py

from typing import List, Optional
from datenbank.datenbank_verbindung import hole_datenbank_verbindung
from modelle.vokabel_set import VokabelSet


class SetRepository:
    """
    Verwaltet die Set-Datensätze in der Datenbank.
    """

    def set_anlegen(self, benutzer_id: int, name: str) -> int:
        """
        Legt ein neues Set an und gibt die ID des Sets zurück.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            INSERT INTO vokabel_set (benutzer_id, name)
            VALUES (?, ?);
            """,
            (benutzer_id, name),
        )

        verbindung.commit()
        set_id = cursor.lastrowid
        verbindung.close()
        return set_id

    def hole_alle_sets_fuer_benutzer(self, benutzer_id: int) -> List[VokabelSet]:
        """
        Lädt alle Sets eines Benutzers.
        """
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            """
            SELECT id, benutzer_id, name
            FROM vokabel_set
            WHERE benutzer_id = ?
            ORDER BY name;
            """,
            (benutzer_id,),
        )

        zeilen = cursor.fetchall()
        verbindung.close()

        sets: List[VokabelSet] = []
        for zeile in zeilen:
            sets.append(
                VokabelSet(
                    set_id=zeile["id"],
                    benutzer_id=zeile["benutzer_id"],
                    name=zeile["name"],
                )
            )
        return sets

    def hole_set_nach_id(self, set_id: int) -> Optional[VokabelSet]:
        
        # Sucht ein Set anhand seiner ID.
        
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            
            # SELECT id, benutzer_id, name
            # FROM vokabel_set
            # WHERE id = ?;
            
            (set_id,),
        )

        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return None

        return VokabelSet(
            set_id=zeile["id"],
            benutzer_id=zeile["benutzer_id"],
            name=zeile["name"],
        )
    