# main.py

from datenbank.datenbank_verbindung import initialisiere_datenbank
from services.benutzer_service import BenutzerService
from services.lern_service import LernService
from services.set_service import SetService


def zeige_hauptmenue():
    """
    Menü für nicht eingeloggte Benutzer.
    """
    print("\n=== Vocabulary Builder ===")
    print("1) Registrieren")
    print("2) Anmelden")
    print("0) Beenden")


def zeige_benutzermenue(benutzer_email: str):
    """
    Menü für eingeloggte Benutzer.
    """
    print(f"\n=== Willkommen, {benutzer_email}! ===")
    print("1) Neue Vokabel anlegen")
    print("2) Vokabeln verwalten")
    print("3) Sets verwalten")
    print("4) Lernen (Karteikarten)")
    print("5) Quiz (Multiple Choice)")
    print("0) Abmelden")

def set_auswahl_dialog(set_service: SetService, benutzer_id: int) -> int | None:
    """
    Hilfsfunktion:
    Lässt den Benutzer ein Set auswählen oder kein Set verwenden.
    Rückgabe: Set-ID oder None.
    """
    sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    if not sets:
        print("Es existieren noch keine Sets.")
        print("Du kannst später im Menü 'Sets verwalten' welche anlegen.")
        auswahl = input("Soll die Vokabel OHNE Set gespeichert werden? (j/n): ").strip().lower()
        if auswahl == "j":
            return None
        else:
            return None  # aktuell keine andere Möglichkeit
    else:
        print("\nVerfügbare Sets:")
        for s in sets:
            print(f"  {s.id}) {s.name}")
        print("  0) Kein Set")

        while True:
            eingabe = input("Bitte Set-ID wählen (oder 0 für kein Set): ").strip()
            if eingabe == "0":
                return None
            try:
                set_id = int(eingabe)
                # einfache Plausibilitätsprüfung: kommt die ID in der Liste vor?
                if any(s.id == set_id for s in sets):
                    return set_id
                else:
                    print("Diese Set-ID existiert nicht.")
            except ValueError:
                print("Bitte eine Zahl eingeben.")


def dialog_neue_vokabel(
    lern_service: LernService, set_service: SetService, benutzer_id: int
):
    """
    Fragt vom Benutzer die Daten für eine neue Vokabel ab.
    """
    print("\n--- Neue Vokabel anlegen ---")
    wort = input("Vokabel (Wort): ").strip()
    uebersetzung = input("Übersetzung: ").strip()
    beispielsatz = input("Beispielsatz (optional, Enter zum Überspringen): ").strip()
    if beispielsatz == "":
        beispielsatz = None

    set_id = set_auswahl_dialog(set_service, benutzer_id)

    lern_service.neue_vokabel_anlegen(
        benutzer_id=benutzer_id,
        wort=wort,
        uebersetzung=uebersetzung,
        beispielsatz=beispielsatz,
        set_id=set_id,
    )


def dialog_vokabel_verwaltung(
    lern_service: LernService, set_service: SetService, benutzer_id: int
):
    """
    Listet Vokabeln auf und erlaubt Bearbeiten und Löschen.
    """
    print("\n--- Vokabelverwaltung ---")
    sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    print("Möchtest du alle Vokabeln sehen oder nur aus einem bestimmten Set?")
    print("1) Alle Vokabeln")
    if sets:
        print("2) Nur Vokabeln aus einem Set")
    auswahl = input("Auswahl: ").strip()

    ausgewaehltes_set_id = None
    if auswahl == "2" and sets:
        ausgewaehltes_set_id = set_auswahl_dialog(set_service, benutzer_id)

    vokabeln = lern_service.hole_alle_vokabeln(benutzer_id, ausgewaehltes_set_id)

    if not vokabeln:
        print("Keine Vokabeln gefunden.")
        return

    print("\nID | Wort -> Übersetzung | Status | Set")
    print("-----------------------------------------------")
    for v in vokabeln:
        set_text = v.set_name if v.set_name else "-"
        print(f"{v.id:3} | {v.wort} -> {v.uebersetzung} | {v.status} | {set_text}")

    print("\nWas möchtest du tun?")
    print("1) Vokabel bearbeiten")
    print("2) Vokabel löschen")
    print("0) Zurück")

    aktion = input("Auswahl: ").strip()

    if aktion == "0":
        return

    vokabel_id_text = input("Bitte Vokabel-ID eingeben: ").strip()
    try:
        vokabel_id = int(vokabel_id_text)
    except ValueError:
        print("Ungültige ID.")
        return

    if aktion == "1":
        # Bearbeiten
        wort_neu = input("Neues Wort (leer = unverändert): ").strip()
        uebersetzung_neu = input("Neue Übersetzung (leer = unverändert): ").strip()
        beispielsatz_neu = input(
            "Neuer Beispielsatz (leer = unverändert, '-' = löschen): "
        ).strip()

        # vorhandene Vokabel holen, um alte Werte zu kennen
        vorhandene_liste = [v for v in vokabeln if v.id == vokabel_id]
        if not vorhandene_liste:
            print("Vokabel mit dieser ID wurde nicht gefunden.")
            return
        vorhandene = vorhandene_liste[0]

        if wort_neu == "":
            wort_neu = vorhandene.wort
        if uebersetzung_neu == "":
            uebersetzung_neu = vorhandene.uebersetzung

        if beispielsatz_neu == "":
            beispielsatz_final = vorhandene.beispielsatz
        elif beispielsatz_neu == "-":
            beispielsatz_final = None
        else:
            beispielsatz_final = beispielsatz_neu

        print("Set-Auswahl für die Vokabel:")
        neues_set_id = set_auswahl_dialog(set_service, benutzer_id)

        lern_service.aktualisiere_vokabel(
            vokabel_id=vokabel_id,
            neues_wort=wort_neu,
            neue_uebersetzung=uebersetzung_neu,
            neuer_beispielsatz=beispielsatz_final,
            neues_set_id=neues_set_id,
        )

    elif aktion == "2":
        bestaetigung = input(
            "Bist du sicher, dass du die Vokabel löschen möchtest? (j/n): "
        ).strip().lower()
        if bestaetigung == "j":
            lern_service.loesche_vokabel(vokabel_id)
        else:
            print("Löschen abgebrochen.")
    else:
        print("Ungültige Auswahl.")


def dialog_sets_verwalten(set_service: SetService, benutzer_id: int):
    """
    Ermöglicht das Anlegen, Anzeigen, Bearbeiten und Löschen von Sets.
    """
    print("\n--- Sets verwalten ---")
    print("1) Neues Set anlegen")
    print("2) Alle Sets anzeigen")
    print("3) Set umbenennen")
    print("4) Set löschen")
    print("0) Zurück")

    auswahl = input("Auswahl: ").strip()

    if auswahl == "1":
        name = input("Name des neuen Sets: ").strip()
        set_service.set_anlegen(benutzer_id, name)

    elif auswahl == "2":
        sets = set_service.hole_sets_fuer_benutzer(benutzer_id)
        if not sets:
            print("Es wurden noch keine Sets angelegt.")
        else:
            print("\nVorhandene Sets:")
            for s in sets:
                print(f"- ID {s.id}: {s.name}")

    elif auswahl == "3":
        sets = set_service.hole_sets_fuer_benutzer(benutzer_id)
        if not sets:
            print("Keine Sets vorhanden.")
            return

        print("\nVorhandene Sets:")
        for s in sets:
            print(f"- ID {s.id}: {s.name}")

        set_id_text = input("Welche Set-ID möchtest du umbenennen?: ").strip()
        try:
            set_id = int(set_id_text)
        except ValueError:
            print("Ungültige ID.")
            return

        neuer_name = input("Neuer Name für das Set: ").strip()
        set_service.set_umbenennen(set_id, neuer_name)

    elif auswahl == "4":
        sets = set_service.hole_sets_fuer_benutzer(benutzer_id)
        if not sets:
            print("Keine Sets vorhanden.")
            return

        print("\nVorhandene Sets:")
        for s in sets:
            print(f"- ID {s.id}: {s.name}")

        set_id_text = input("Welche Set-ID möchtest du löschen?: ").strip()
        try:
            set_id = int(set_id_text)
        except ValueError:
            print("Ungültige ID.")
            return

        bestaetigung = input("Bist du sicher? (j/n): ").strip().lower()
        if bestaetigung != "j":
            print("Löschen abgebrochen.")
            return

        print("\nWas soll mit den Vokabeln im Set passieren?")
        print("1) Vokabeln behalten (Set-Zuordnung wird entfernt)")
        print("2) Löschen nur erlauben, wenn Set leer ist")
        print("3) Set löschen UND alle Vokabeln im Set löschen")
        wahl = input("Auswahl: ").strip()

        if wahl == "1":
            set_service.set_loeschen(set_id, modus="behalten")
        elif wahl == "2":
            set_service.set_loeschen(set_id, modus="nur_leer")
        elif wahl == "3":
            set_service.set_loeschen(set_id, modus="mit_vokabeln")
        else:
            print("Ungültige Auswahl.")

    elif auswahl == "0":
        return

    else:
        print("Ungültige Auswahl.")


def dialog_karteikarten(lern_service: LernService, set_service: SetService, benutzer_id: int):
    """
    Startet den Karteikartenmodus – wahlweise mit allen Vokabeln
    oder nur einem bestimmten Set.
    """
    print("\n--- Lernen (Karteikarten) ---")
    print("1) Alle Vokabeln üben")
    print("2) Nur Vokabeln aus einem Set üben")
    print("0) Zurück")

    auswahl = input("Auswahl: ").strip()

    if auswahl == "0":
        return

    set_id = None
    if auswahl == "2":
        set_id = set_auswahl_dialog(set_service, benutzer_id)

    lern_service.starte_karteikarten_modus(benutzer_id=benutzer_id, set_id=set_id)

def dialog_multiple_choice(lern_service: LernService, set_service: SetService, benutzer_id: int):
    print("\n--- Quiz (Multiple Choice) ---")
    print("1) Quiz starten (gemischt, max. 10 Fragen)")
    print("2) Quiz starten (nur aus einem Set, gemischt, max. 10 Fragen)")
    print("0) Zurück")

    auswahl = input("Auswahl: ").strip()
    if auswahl == "0":
        return

    set_id = None
    if auswahl == "2":
        set_id = set_auswahl_dialog(set_service, benutzer_id)

    # Start: gemischt, max 10
    lern_service.starte_multiple_choice_runde(
        benutzer_id=benutzer_id,
        set_id=set_id,
        max_fragen=10
    )

def hauptschleife():
    # Datenbank vorbereiten
    initialisiere_datenbank()

    benutzer_service = BenutzerService()
    lern_service = LernService()
    set_service = SetService()

    angemeldeter_benutzer = None

    while True:
        if angemeldeter_benutzer is None:
            # Nicht eingeloggt
            zeige_hauptmenue()
            auswahl = input("Auswahl: ").strip()

            if auswahl == "1":
                email = input("E-Mail: ").strip()
                passwort = input("Passwort: ").strip()
                benutzer_service.registriere_neuen_benutzer(email, passwort)

            elif auswahl == "2":
                email = input("E-Mail: ").strip()
                passwort = input("Passwort: ").strip()
                benutzer = benutzer_service.melde_benutzer_an(email, passwort)
                if benutzer:
                    angemeldeter_benutzer = benutzer

            elif auswahl == "0":
                print("Programm wird beendet. Tschüss!")
                break
            else:
                print("Ungültige Eingabe.")
        else:
            # Eingeloggt
            zeige_benutzermenue(benutzer_email=angemeldeter_benutzer.email)
            auswahl = input("Auswahl: ").strip()

            if auswahl == "1":
                dialog_neue_vokabel(
                    lern_service=lern_service,
                    set_service=set_service,
                    benutzer_id=angemeldeter_benutzer.id,
                )

            elif auswahl == "2":
                dialog_vokabel_verwaltung(
                    lern_service=lern_service,
                    set_service=set_service,
                    benutzer_id=angemeldeter_benutzer.id,
                )

            elif auswahl == "3":
                dialog_sets_verwalten(
                    set_service=set_service,
                    benutzer_id=angemeldeter_benutzer.id,
                )

            elif auswahl == "4":
                dialog_karteikarten(
                    lern_service=lern_service,
                    set_service=set_service,
                    benutzer_id=angemeldeter_benutzer.id,
                )

            elif auswahl == "5":
                dialog_multiple_choice(
                    lern_service, 
                    set_service, 
                    angemeldeter_benutzer.id,
                )

            elif auswahl == "0":
                print("Du wurdest abgemeldet.")
                angemeldeter_benutzer = None
            else:
                print("Ungültige Eingabe.")


if __name__ == "__main__":
    hauptschleife()
