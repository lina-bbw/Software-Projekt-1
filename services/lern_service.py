# services/lern_service.py

from typing import List
from datenbank.vokabel_repository import VokabelRepository
from modelle.vokabel import Vokabel


class LernService:
    
    # Enthält Lernlogik für den Karteikartenmodus und einfache Hilfsfunktionen für Vokabeln.
    

    def __init__(self):
        self.vokabel_repository = VokabelRepository()

    def neue_vokabel_anlegen(
        self,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        set_id: int | None,
    ):
        
        # Legt eine neue Vokabel über das Repository an.
        
        if not wort or not uebersetzung:
            print("Wort und Übersetzung dürfen nicht leer sein.")
            return

        self.vokabel_repository.vokabel_anlegen(
            benutzer_id=benutzer_id,
            wort=wort,
            uebersetzung=uebersetzung,
            beispielsatz=beispielsatz,
            set_id=set_id,
        )
        print("Vokabel wurde gespeichert.")

    def hole_alle_vokabeln(
        self, benutzer_id: int, set_id: int | None = None
    ) -> List[Vokabel]:
        
        # Gibt alle Vokabeln eines Benutzers (optional gefiltert nach Set) zurück.
        
        return self.vokabel_repository.hole_alle_vokabeln_fuer_benutzer(
            benutzer_id, set_id
        )

    def aktualisiere_vokabel(
        self,
        vokabel_id: int,
        neues_wort: str,
        neue_uebersetzung: str,
        neuer_beispielsatz: str | None,
        neues_set_id: int | None,
    ):
        
        # Aktualisiert eine Vokabel.
        
        self.vokabel_repository.aktualisiere_vokabel(
            vokabel_id=vokabel_id,
            neues_wort=neues_wort,
            neue_uebersetzung=neue_uebersetzung,
            neuer_beispielsatz=neuer_beispielsatz,
            neues_set_id=neues_set_id,
        )
        print("Vokabel wurde aktualisiert.")

    def loesche_vokabel(self, vokabel_id: int):
        
        # Löscht eine Vokabel.
        
        self.vokabel_repository.vokabel_loeschen(vokabel_id)
        print("Vokabel wurde gelöscht.")

    def setze_vokabel_status(self, vokabel_id: int, neuer_status: str):
        
        # Setzt den Status einer Vokabel ('neu', 'unsicher', 'sicher').
        
        self.vokabel_repository.aktualisiere_status(vokabel_id, neuer_status)

    def starte_karteikarten_modus(
        self, benutzer_id: int, set_id: int | None = None
    ):
        """
        Karteikartenmodus zum Üben:
        - Zeigt Vokabeln (optional eines bestimmten Sets).
        - Erst nur das Wort.
        - Enter zum Umdrehen.
        - Danach 'j' = gewusst (Status 'sicher'),
          'n' = nicht gewusst (Status 'unsicher').
        """
        vokabeln = self.hole_alle_vokabeln(benutzer_id, set_id)

        if not vokabeln:
            print("Es sind noch keine Vokabeln vorhanden.")
            return

        print("\n--- Karteikartenmodus ---")
        if set_id is None:
            print("Es werden alle Vokabeln geübt.")
        else:
            print(f"Es werden nur Vokabeln aus Set-ID {set_id} geübt.")
        print("Eingabe 'q' beendet den Modus.\n")

        for vokabel in vokabeln:
            print(f"Vokabel: {vokabel.wort}")
            eingabe = input("Drücke Enter zum Aufdecken (oder 'q' zum Beenden): ")

            if eingabe.strip().lower() == "q":
                print("Karteikartenmodus beendet.\n")
                break

            print(f"Übersetzung: {vokabel.uebersetzung}")
            if vokabel.beispielsatz:
                print(f"Beispielsatz: {vokabel.beispielsatz}")

            antwort = input("Gewusst? (j = ja, n = nein): ").strip().lower()

            if antwort == "j":
                neuer_status = "sicher"
            elif antwort == "n":
                neuer_status = "unsicher"
            else:
                print("Eingabe nicht erkannt, Status bleibt unverändert.")
                continue

            self.setze_vokabel_status(vokabel_id=vokabel.id, neuer_status=neuer_status)
            print(f"Status wurde auf '{neuer_status}' gesetzt.\n")
