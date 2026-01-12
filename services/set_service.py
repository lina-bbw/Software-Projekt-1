# services/set_service.py

from typing import List
from datenbank.set_repository import SetRepository
from modelle.vokabel_set import VokabelSet


class SetService:
    """
    Bietet einfache Funktionen rund um Sets / Themen.
    """

    def __init__(self):
        self.set_repository = SetRepository()

    def set_anlegen(self, benutzer_id: int, name: str) -> int:
        """
        Legt ein neues Set an und gibt dessen ID zurück.
        """
        if not name:
            print("Set-Name darf nicht leer sein.")
            return -1

        set_id = self.set_repository.set_anlegen(benutzer_id, name)
        print(f"Set '{name}' wurde angelegt (ID: {set_id}).")
        return set_id

    def hole_sets_fuer_benutzer(self, benutzer_id: int) -> List[VokabelSet]:
        """
        Gibt alle Sets eines Benutzers zurück.
        """
        return self.set_repository.hole_alle_sets_fuer_benutzer(benutzer_id)

    def set_umbenennen(self, set_id: int, neuer_name: str) -> None:
        """
        Benennt ein Set um.
        """
        if not neuer_name:
            print("Neuer Name darf nicht leer sein.")
            return
        self.set_repository.set_umbenennen(set_id, neuer_name)
        print("Set wurde umbenannt.")

    def set_loeschen(self, set_id: int, modus: str) -> None:
        """
        Löscht ein Set in einem von drei Modi:

        modus = "behalten":
            Vokabeln bleiben erhalten, set_id wird auf NULL gesetzt.
        modus = "nur_leer":
            Set wird nur gelöscht, wenn keine Vokabeln drin sind.
        modus = "mit_vokabeln":
            Set wird gelöscht UND alle Vokabeln im Set werden gelöscht.
        """
        hat_vokabeln = self.set_repository.set_hat_vokabeln(set_id)

        if modus == "nur_leer":
            if hat_vokabeln:
                print("Set kann nicht gelöscht werden, weil noch Vokabeln enthalten sind.")
                return
            self.set_repository.set_loeschen(set_id)
            print("Set wurde gelöscht.")
            return

        if modus == "behalten":
            if hat_vokabeln:
                self.set_repository.vokabeln_set_entfernen(set_id)
            self.set_repository.set_loeschen(set_id)
            print("Set wurde gelöscht. Vokabeln wurden behalten (ohne Set).")
            return

        if modus == "mit_vokabeln":
            if hat_vokabeln:
                self.set_repository.vokabeln_im_set_loeschen(set_id)
            self.set_repository.set_loeschen(set_id)
            print("Set wurde gelöscht. Alle Vokabeln im Set wurden ebenfalls gelöscht.")
            return

        print("Unbekannter Löschmodus.")
