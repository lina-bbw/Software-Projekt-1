# services/lern_service.py
import random
from typing import List
from datenbank.vokabel_repository import VokabelRepository
from modelle.vokabel import Vokabel


class LernService:
    """
    Enthält Lernlogik für den Karteikartenmodus
    und einfache Hilfsfunktionen für Vokabeln.
    """

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
        """
        Legt eine neue Vokabel über das Repository an.
        """
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
        """
        Gibt alle Vokabeln eines Benutzers (optional gefiltert nach Set) zurück.
        """
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
        """
        Aktualisiert eine Vokabel.
        """
        self.vokabel_repository.aktualisiere_vokabel(
            vokabel_id=vokabel_id,
            neues_wort=neues_wort,
            neue_uebersetzung=neue_uebersetzung,
            neuer_beispielsatz=neuer_beispielsatz,
            neues_set_id=neues_set_id,
        )
        print("Vokabel wurde aktualisiert.")

    def loesche_vokabel(self, vokabel_id: int):
        """
        Löscht eine Vokabel.
        """
        self.vokabel_repository.vokabel_loeschen(vokabel_id)
        print("Vokabel wurde gelöscht.")

    def setze_vokabel_status(self, vokabel_id: int, neuer_status: str):
        """
        Setzt den Status einer Vokabel ('neu', 'unsicher', 'sicher').
        """
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
    
    def _baue_antwortoptionen(self, richtige_antwort: str, pool: list[str], anzahl_optionen: int = 4) -> list[str]:
        """
        Baut eine Liste aus Antwortoptionen:
        1 richtige + (anzahl_optionen-1) falsche aus dem Pool, ohne Duplikate.
        """
        # Pool ohne die richtige Antwort
        falscher_pool = [x for x in pool if x != richtige_antwort]

        # Falls zu wenige Daten vorhanden sind
        if len(falscher_pool) < anzahl_optionen - 1:
            # Wir geben dann weniger Optionen zurück (besser als Absturz)
            optionen = [richtige_antwort] + falscher_pool
            random.shuffle(optionen)
            return optionen

        falsche = random.sample(falscher_pool, anzahl_optionen - 1)
        optionen = [richtige_antwort] + falsche
        random.shuffle(optionen)
        return optionen

    def starte_multiple_choice_runde(self, benutzer_id: int, set_id: int | None = None, max_fragen: int = 10):
        """
        Multiple Choice Quizrunde:
        - pro Frage zufällig: Wort -> Übersetzung ODER Übersetzung -> Wort
        - 4 Antwortmöglichkeiten (1 richtig, 3 falsch)
        - max. 10 Fragen pro Runde (oder weniger, wenn weniger Vokabeln existieren)
        - 'q' beendet frühzeitig
        """

        vokabeln = self.hole_alle_vokabeln(benutzer_id, set_id)

        if len(vokabeln) < 4:
            print("Für Multiple Choice brauchst du mindestens 4 Vokabeln (damit 4 Optionen möglich sind).")
            return

        # Pools für falsche Antworten
        alle_uebersetzungen = self.vokabel_repository.hole_alle_uebersetzungen(benutzer_id, set_id)
        alle_woerter = self.vokabel_repository.hole_alle_woerter(benutzer_id, set_id)

        # Anzahl Fragen begrenzen
        random.shuffle(vokabeln)
        runden_vokabeln = vokabeln[: min(max_fragen, len(vokabeln))]

        print("\n--- Multiple Choice (gemischt) ---")
        print(f"Maximal {max_fragen} Fragen pro Runde. Eingabe 'q' beendet.\n")

        punkte = 0
        gesamt = 0

        for vokabel in runden_vokabeln:
            gesamt += 1

            # Richtung pro Frage zufällig wählen
            richtung = random.choice(["wort_zu_uebersetzung", "uebersetzung_zu_wort"])

            if richtung == "wort_zu_uebersetzung":
                frage_text = f"Wort: {vokabel.wort}"
                richtige = vokabel.uebersetzung
                optionen = self._baue_antwortoptionen(richtige, alle_uebersetzungen, 4)
            else:
                frage_text = f"Übersetzung: {vokabel.uebersetzung}"
                richtige = vokabel.wort
                optionen = self._baue_antwortoptionen(richtige, alle_woerter, 4)

            print(f"Frage {gesamt}/{len(runden_vokabeln)}")
            print(frage_text)
            for i, opt in enumerate(optionen, start=1):
                print(f"  {i}) {opt}")

            eingabe = input("Deine Antwort (1-4 oder q): ").strip().lower()
            if eingabe == "q":
                print("Runde beendet.\n")
                break

            try:
                index = int(eingabe) - 1
                if index < 0 or index >= len(optionen):
                    print("Ungültige Auswahl.\n")
                    continue
            except ValueError:
                print("Bitte eine Zahl eingeben.\n")
                continue

            ausgewaehlt = optionen[index]

            if ausgewaehlt == richtige:
                punkte += 1
                print("✅ Richtig!\n")
                self.setze_vokabel_status(vokabel.id, "sicher")
            else:
                print(f"❌ Falsch. Richtig wäre: {richtige}\n")
                self.setze_vokabel_status(vokabel.id, "unsicher")

        if gesamt > 0:
            print(f"Ergebnis: {punkte}/{gesamt} richtig.\n")
