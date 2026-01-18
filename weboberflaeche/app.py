# weboberflaeche/app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
import os
print("AKTUELLER WORKDIR:", os.getcwd())


from datenbank.datenbank_verbindung import initialisiere_datenbank

from services.benutzer_service import BenutzerService
from services.lern_service import LernService
from services.set_service import SetService

# ✅ Streak-Service importieren
from services.lern_tag_service import LernTagService


app = Flask(__name__)
app.secret_key = "demo_schluessel_fuer_uni"

# ✅ Services erstellen
benutzer_service = BenutzerService()
lern_service = LernService()
set_service = SetService()


lern_tag_service = LernTagService()

# ✅ DB initialisieren
initialisiere_datenbank()


def ist_eingeloggt() -> bool:
    return session.get("benutzer_id") is not None


def login_erforderlich() -> bool:
    if not ist_eingeloggt():
        flash("Bitte zuerst anmelden.")
        return False
    return True


@app.route("/")
def start():
    if ist_eingeloggt():
        return redirect(url_for("dashboard"))
    return render_template("start.html")


@app.route("/registrieren", methods=["GET", "POST"])
def registrieren():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        passwort = request.form.get("passwort", "").strip()

        erfolgreich = benutzer_service.registriere_neuen_benutzer(email, passwort)
        if erfolgreich:
            flash("Registrierung erfolgreich. Bitte anmelden.")
            return redirect(url_for("anmelden"))
        flash("Registrierung fehlgeschlagen (E-Mail evtl. schon vergeben).")

    return render_template("registrieren.html")


@app.route("/anmelden", methods=["GET", "POST"])
def anmelden():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        passwort = request.form.get("passwort", "").strip()

        benutzer = benutzer_service.melde_benutzer_an(email, passwort)
        if benutzer:
            session["benutzer_id"] = benutzer.id
            session["benutzer_email"] = benutzer.email
            flash("Angemeldet.")
            return redirect(url_for("dashboard"))

        flash("Login fehlgeschlagen (E-Mail/Passwort prüfen).")

    return render_template("anmelden.html")


@app.route("/abmelden")
def abmelden():
    session.clear()
    flash("Abgemeldet.")
    return redirect(url_for("start"))


# -----------------------------
# Passwort vergessen (Reset)
# -----------------------------

@app.route("/passwort-vergessen", methods=["GET", "POST"])
def passwort_vergessen():
    """
    Studentische Lösung:
    - Nutzer gibt E-Mail ein
    - wir erzeugen Reset-Code und zeigen ihn an (statt Mail)
    """
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        code = benutzer_service.reset_code_erstellen(email)
        if code is None:
            flash("E-Mail nicht gefunden.")
            return redirect(url_for("passwort_vergessen"))

        # Code anzeigen (damit man testen kann)
        flash(f"Reset-Code (Demo): {code}")
        return redirect(url_for("passwort_zuruecksetzen", email=email))

    return render_template("passwort_vergessen.html")


@app.route("/passwort-zuruecksetzen", methods=["GET", "POST"])
def passwort_zuruecksetzen():
    email = request.args.get("email", "").strip()

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        code = request.form.get("code", "").strip()
        neues_passwort = request.form.get("neues_passwort", "").strip()

        ok = benutzer_service.passwort_zuruecksetzen(email, code, neues_passwort)
        if ok:
            flash("Passwort geändert. Bitte neu anmelden.")
            return redirect(url_for("anmelden"))

        flash("Reset fehlgeschlagen (Code/E-Mail prüfen).")
        return redirect(url_for("passwort_zuruecksetzen", email=email))

    return render_template("passwort_zuruecksetzen.html", email=email)


# -----------------------------
# Dashboard (inkl. Streak)
# -----------------------------

@app.route("/dashboard")
def dashboard():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    vokabeln = lern_service.hole_alle_vokabeln(benutzer_id)
    sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    # --- Fortschritt berechnen ---
    gesamt = len(vokabeln)
    anzahl_sicher = len([v for v in vokabeln if v.status == "sicher"])

    if gesamt == 0:
        fortschritt_prozent = 0
    else:
        fortschritt_prozent = round((anzahl_sicher / gesamt) * 100)

    return render_template(
    "dashboard.html",
    email=session.get("benutzer_email", ""),
    anzahl_vokabeln=gesamt,
    anzahl_sets=len(sets),
    fortschritt_prozent=fortschritt_prozent,
    anzahl_sicher=anzahl_sicher,
    gesamt_vokabeln=gesamt,
    sets=sets,  # ✅ DAS FEHLTE
)

# -----------------------------
# Sets
# -----------------------------

@app.route("/sets", methods=["GET", "POST"])
def sets():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session.get("benutzer_id")

    # ✅ Debug: Welche Benutzer-ID ist aktiv?
    print("BENUTZER_ID (Session):", benutzer_id)

    # Set anlegen
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            set_service.set_anlegen(benutzer_id, name)
            flash("Set angelegt.")
        else:
            flash("Set-Name darf nicht leer sein.")
        return redirect(url_for("sets"))

    # Sets laden
    alle_sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    # ✅ Debug: Was kommt wirklich aus der DB?
    print("SETS DEBUG:", [(getattr(s, "id", None), getattr(s, "name", None)) for s in alle_sets])

    return render_template("sets.html", sets=alle_sets)

@app.route("/sets/<int:set_id>/bearbeiten", methods=["GET", "POST"])
def set_bearbeiten(set_id: int):
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    alle_sets = set_service.hole_sets_fuer_benutzer(benutzer_id)
    ziel_set = next((s for s in alle_sets if s.id == set_id), None)

    if ziel_set is None:
        flash("Set nicht gefunden.")
        return redirect(url_for("sets"))

    if request.method == "POST":
        neuer_name = request.form.get("name", "").strip()
        if neuer_name:
            set_service.set_umbenennen(set_id, neuer_name)
            flash("Set umbenannt.")
            return redirect(url_for("sets"))
        flash("Name darf nicht leer sein.")

    return render_template("set_bearbeiten.html", set_obj=ziel_set)


@app.route("/sets/<int:set_id>/loeschen", methods=["POST"])
def set_loeschen(set_id: int):
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    modus = request.form.get("modus", "behalten")
    set_service.set_loeschen(set_id, modus=modus)
    flash("Löschvorgang ausgeführt.")
    return redirect(url_for("sets"))


# -----------------------------
# Vokabeln (CRUD + Filter)
# -----------------------------

@app.route("/vokabeln")
def vokabeln():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]

    set_filter = request.args.get("set_id", "").strip()
    set_id = None
    if set_filter:
        try:
            set_id = int(set_filter)
        except ValueError:
            set_id = None

    vokabel_liste = lern_service.hole_alle_vokabeln(benutzer_id, set_id=set_id)
    alle_sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    return render_template(
        "vokabeln.html",
        vokabeln=vokabel_liste,
        sets=alle_sets,
        aktuelles_set_id=set_id,
    )


@app.route("/vokabeln/neu", methods=["GET", "POST"])
def vokabel_neu():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    alle_sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    if request.method == "POST":
        wort = request.form.get("wort", "").strip()
        uebersetzung = request.form.get("uebersetzung", "").strip()
        beispielsatz = request.form.get("beispielsatz", "").strip()
        bemerkungen = request.form.get("bemerkungen", "").strip()
        set_id_text = request.form.get("set_id", "").strip()

        if beispielsatz == "":
            beispielsatz = None
        if bemerkungen == "":
            bemerkungen = None

        set_id = None
        if set_id_text:
            try:
                set_id = int(set_id_text)
            except ValueError:
                set_id = None

        lern_service.neue_vokabel_anlegen(
            benutzer_id=benutzer_id,
            wort=wort,
            uebersetzung=uebersetzung,
            beispielsatz=beispielsatz,
            bemerkungen=bemerkungen,
            set_id=set_id,
        )

        flash("Vokabel gespeichert.")
        return redirect(url_for("vokabeln"))

    return render_template("vokabel_neu.html", sets=alle_sets)


@app.route("/vokabeln/<int:vokabel_id>/bearbeiten", methods=["GET", "POST"])
def vokabel_bearbeiten(vokabel_id: int):
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    vokabeln_liste = lern_service.hole_alle_vokabeln(benutzer_id)
    vok = next((v for v in vokabeln_liste if v.id == vokabel_id), None)

    if vok is None:
        flash("Vokabel nicht gefunden.")
        return redirect(url_for("vokabeln"))

    alle_sets = set_service.hole_sets_fuer_benutzer(benutzer_id)

    if request.method == "POST":
        wort = request.form.get("wort", "").strip()
        uebersetzung = request.form.get("uebersetzung", "").strip()
        beispielsatz = request.form.get("beispielsatz", "").strip()
        bemerkungen = request.form.get("bemerkungen", "").strip()
        set_id_text = request.form.get("set_id", "").strip()

        if wort == "":
            wort = vok.wort
        if uebersetzung == "":
            uebersetzung = vok.uebersetzung

        # Beispielsatz: leer=unverändert, "-"=löschen
        if beispielsatz == "":
            beispielsatz = vok.beispielsatz
        elif beispielsatz == "-":
            beispielsatz = None

        # Bemerkungen: leer=unverändert, "-"=löschen
        if bemerkungen == "":
            bemerkungen = vok.bemerkungen
        elif bemerkungen == "-":
            bemerkungen = None

        # Set: "" unverändert, "0" kein Set, sonst ID
        neues_set_id = vok.set_id
        if set_id_text == "":
            neues_set_id = vok.set_id
        elif set_id_text == "0":
            neues_set_id = None
        else:
            try:
                neues_set_id = int(set_id_text)
            except ValueError:
                neues_set_id = vok.set_id

        lern_service.aktualisiere_vokabel(
            vokabel_id=vokabel_id,
            neues_wort=wort,
            neue_uebersetzung=uebersetzung,
            neuer_beispielsatz=beispielsatz,
            neue_bemerkungen=bemerkungen,
            neues_set_id=neues_set_id,
        )

        flash("Vokabel aktualisiert.")
        return redirect(url_for("vokabeln"))

    return render_template("vokabel_bearbeiten.html", vokabel=vok, sets=alle_sets)


@app.route("/vokabeln/<int:vokabel_id>/loeschen", methods=["POST"])
def vokabel_loeschen(vokabel_id: int):
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    lern_service.loesche_vokabel(vokabel_id)
    flash("Vokabel gelöscht.")
    return redirect(url_for("vokabeln"))


# -----------------------------
# Karteikarten (Üben + Streak)
# -----------------------------

@app.route("/karteikarten")
def karteikarten():
    # 1) Sicherheitscheck: Wenn nicht eingeloggt -> zur Anmeldung
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    # 2) Benutzer-ID aus der Session holen
    benutzer_id = session["benutzer_id"]

    # 3) Alle Vokabeln dieses Benutzers laden
    vokabeln_liste = lern_service.hole_alle_vokabeln(benutzer_id)

    # 4) Falls keine Vokabeln existieren -> zurück zum Dashboard
    if not vokabeln_liste:
        flash("Keine Vokabeln vorhanden.")
        return redirect(url_for("dashboard"))

    # 5) ID der zuletzt gezeigten Karte (damit nicht immer die gleiche kommt)
    letzte_id = session.get("letzte_karteikarte_id")

    # 6) Vokabeln nach Status aufteilen -> Priorität:
    #    1) neu
    #    2) unsicher
    #    3) sicher
    neue = [v for v in vokabeln_liste if v.status == "neu"]
    unsichere = [v for v in vokabeln_liste if v.status == "unsicher"]
    sichere = [v for v in vokabeln_liste if v.status == "sicher"]

    def waehle_ohne_wiederholung(liste, letzte_vokabel_id):
        """
        Wählt zufällig eine Vokabel aus einer Liste.
        Wenn möglich wird die zuletzt gezeigte Vokabel ausgeschlossen,
        damit nicht direkt hintereinander die gleiche Karte kommt.
        """
        if not liste:
            return None

        # Wenn nur 1 Element vorhanden ist, kann man nicht ausweichen
        if len(liste) == 1:
            return liste[0]

        # Versuche: letzte Karte rausfiltern
        gefiltert = [v for v in liste if v.id != letzte_vokabel_id]

        # Falls nach dem Filtern nichts übrig bleibt -> wieder komplette Liste nutzen
        if not gefiltert:
            gefiltert = liste

        return random.choice(gefiltert)

    # 7) Auswahl nach Priorität
    kandidat = waehle_ohne_wiederholung(neue, letzte_id)
    if kandidat is None:
        kandidat = waehle_ohne_wiederholung(unsichere, letzte_id)
    if kandidat is None:
        kandidat = waehle_ohne_wiederholung(sichere, letzte_id)

    # 8) Die aktuell gezeigte Vokabel-ID merken
    session["letzte_karteikarte_id"] = kandidat.id

    # 9) Karteikarten-Seite rendern
    return render_template("karteikarten.html", vokabel=kandidat)

@app.route("/karteikarten/bewerten", methods=["POST"])
def karteikarten_bewerten():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    vokabel_id = int(request.form.get("vokabel_id"))
    aktion = request.form.get("aktion")

    if aktion == "gewusst":
        lern_service.setze_vokabel_status(vokabel_id, "sicher")
    elif aktion == "nicht_gewusst":
        lern_service.setze_vokabel_status(vokabel_id, "unsicher")

    return redirect(url_for("karteikarten"))


# -----------------------------
# Quiz (MC, gemischt, max 10 + Streak + Ergebnis)
# -----------------------------

@app.route("/quiz")
def quiz_start():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))
    return render_template("quiz_start.html")


@app.route("/quiz/start", methods=["POST"])
def quiz_starten():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    vokabeln_liste = lern_service.hole_alle_vokabeln(benutzer_id)

    # Für MC brauchen wir min. 4 Vokabeln (wegen 4 Antwortoptionen)
    if len(vokabeln_liste) < 4:
        flash("Für das Quiz brauchst du mindestens 4 Vokabeln.")
        return redirect(url_for("quiz_start"))

    # Pools für falsche Antworten (für MC)
    session["quiz_woerter_pool"] = [v.wort for v in vokabeln_liste]
    session["quiz_uebersetzungen_pool"] = [v.uebersetzung for v in vokabeln_liste]

    steps = []

    # --- Fall A: >= 15 Vokabeln -> 5 MC + Matching(5 Paare) + 5 MC = max 15 Punkte ---
    if len(vokabeln_liste) >= 15:
        # Wir nehmen 15 unterschiedliche Vokabeln: 10 für MC + 5 für Matching
        auswahl_15 = random.sample(vokabeln_liste, 15)

        mc_vokabeln = auswahl_15[:10]      # 10 MC-Fragen
        match_vokabeln = auswahl_15[10:]   # 5 Paare fürs Matching (max 5 Punkte)

        # Reihenfolge: 5 MC
        for v in mc_vokabeln[:5]:
            steps.append({"typ": "mc", "vokabel_id": v.id})

        # 1x Matching dazwischen (mit genau diesen 5 Vokabeln)
        steps.append({"typ": "match", "vokabel_ids": [v.id for v in match_vokabeln]})

        # Danach nochmal 5 MC
        for v in mc_vokabeln[5:]:
            steps.append({"typ": "mc", "vokabel_id": v.id})

        # Max Punkte = 10 (MC) + 5 (Matching) = 15
        session["quiz_max_punkte"] = 15

    # --- Fall B: < 15 Vokabeln -> nur MC (bis max 15 Fragen, aber nicht mehr als vorhandene Vokabeln) ---
    else:
        # MC-Fragen = min(15, Anzahl vorhandene Vokabeln)
        # (damit nicht die gleiche Vokabel zweimal gefragt wird)
        anzahl_mc = min(15, len(vokabeln_liste))
        mc_vokabeln = random.sample(vokabeln_liste, anzahl_mc)

        for v in mc_vokabeln:
            steps.append({"typ": "mc", "vokabel_id": v.id})

        # Max Punkte = Anzahl MC-Fragen (weil kein Matching)
        session["quiz_max_punkte"] = anzahl_mc

    session["quiz_steps"] = steps
    session["quiz_step_index"] = 0
    session["quiz_punkte"] = 0

    return redirect(url_for("quiz_naechster_step"))


def _optionen_bauen(richtige_antwort: str, pool: list[str], anzahl: int = 4) -> list[str]:
    pool_falsch = [x for x in pool if x != richtige_antwort]
    if len(pool_falsch) < anzahl - 1:
        optionen = [richtige_antwort] + pool_falsch
        random.shuffle(optionen)
        return optionen
    falsche = random.sample(pool_falsch, anzahl - 1)
    optionen = [richtige_antwort] + falsche
    random.shuffle(optionen)
    return optionen


@app.route("/quiz/frage", methods=["GET", "POST"])
def quiz_frage():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    steps = session.get("quiz_steps", [])
    index = session.get("quiz_step_index", 0)
    punkte = session.get("quiz_punkte", 0)

    if not steps or index >= len(steps):
        return redirect(url_for("quiz_naechster_step"))

    step = steps[index]
    if step.get("typ") != "mc":
        return redirect(url_for("quiz_naechster_step"))

    vokabel_id = step.get("vokabel_id")
    vokabeln_liste = lern_service.hole_alle_vokabeln(benutzer_id)
    vok = next((v for v in vokabeln_liste if v.id == vokabel_id), None)
    if vok is None:
        session["quiz_step_index"] = index + 1
        return redirect(url_for("quiz_naechster_step"))

    # POST: Antwort prüfen
    if request.method == "POST":
        richtige = session.get("quiz_richtige")
        gewaehlte = request.form.get("antwort", "")

        if richtige is not None and gewaehlte == richtige:
            session["quiz_punkte"] = punkte + 1
            lern_service.setze_vokabel_status(vok.id, "sicher")
        else:
            lern_service.setze_vokabel_status(vok.id, "unsicher")

        session["quiz_step_index"] = index + 1
        return redirect(url_for("quiz_naechster_step"))

    # GET: Frage generieren (gemischt Wort/Übersetzung)
    richtung = random.choice(["wort_zu_uebersetzung", "uebersetzung_zu_wort"])

    if richtung == "wort_zu_uebersetzung":
        frage = f"Wort: {vok.wort}"
        richtige = vok.uebersetzung
        optionen = _optionen_bauen(richtige, session.get("quiz_uebersetzungen_pool", []), 4)
    else:
        frage = f"Übersetzung: {vok.uebersetzung}"
        richtige = vok.wort
        optionen = _optionen_bauen(richtige, session.get("quiz_woerter_pool", []), 4)

    session["quiz_richtige"] = richtige

    # Anzeige: Nummer nur für MC-Fragen
    mc_nummer = len([s for s in steps[:index+1] if s.get("typ") == "mc"])
    mc_gesamt = len([s for s in steps if s.get("typ") == "mc"])

    return render_template("quiz_frage.html", frage=frage, optionen=optionen, nummer=mc_nummer, gesamt=mc_gesamt)


@app.route("/quiz/naechster-step")
def quiz_naechster_step():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    steps = session.get("quiz_steps", [])
    index = session.get("quiz_step_index", 0)

    # ✅ Ende des Quiz -> Auswertung
    if not steps or index >= len(steps):
        punkte = session.get("quiz_punkte", 0)
        max_punkte = session.get("quiz_max_punkte", 0)

        if max_punkte <= 0:
            flash("Keine Runde aktiv.")
            return redirect(url_for("quiz_start"))

        prozent = round((punkte / max_punkte) * 100, 1)
        flash(f"Richtig: {punkte}/{max_punkte} ({prozent}%)")

        # Session aufräumen
        for key in [
            "quiz_steps", "quiz_step_index", "quiz_punkte",
            "quiz_woerter_pool", "quiz_uebersetzungen_pool",
            "quiz_richtige",
            "match_loesung", "match_woerter", "match_uebersetzungen",
            "quiz_max_punkte"
        ]:
            session.pop(key, None)

        return redirect(url_for("dashboard"))

    # ✅ Ansonsten: Nächsten Step anzeigen
    aktueller = steps[index]

    if aktueller.get("typ") == "mc":
        return redirect(url_for("quiz_frage"))
    else:
        return redirect(url_for("quiz_match"))

@app.route("/quiz/match", methods=["GET", "POST"])
def quiz_match():
    if not login_erforderlich():
        return redirect(url_for("anmelden"))

    benutzer_id = session["benutzer_id"]
    steps = session.get("quiz_steps", [])
    index = session.get("quiz_step_index", 0)

    if not steps or index >= len(steps):
        return redirect(url_for("quiz_naechster_step"))

    step = steps[index]
    if step.get("typ") != "match":
        return redirect(url_for("quiz_naechster_step"))

    vokabel_ids = step.get("vokabel_ids", [])

    # Sicherheitscheck
    if len(vokabel_ids) != 5:
        session["quiz_step_index"] = index + 1
        return redirect(url_for("quiz_naechster_step"))

    vokabeln_liste = lern_service.hole_alle_vokabeln(benutzer_id)
    id_zu_vokabel = {v.id: v for v in vokabeln_liste}

    ausgewaehlt = [id_zu_vokabel.get(v_id) for v_id in vokabel_ids]
    ausgewaehlt = [v for v in ausgewaehlt if v is not None]

    # Falls IDs nicht gefunden werden -> Step skippen
    if len(ausgewaehlt) != 5:
        session["quiz_step_index"] = index + 1
        return redirect(url_for("quiz_naechster_step"))

    # GET: Matching anzeigen
    if request.method == "GET":
        loesung = {v.wort: v.uebersetzung for v in ausgewaehlt}

        woerter = [v.wort for v in ausgewaehlt]
        uebersetzungen = [v.uebersetzung for v in ausgewaehlt]
        random.shuffle(uebersetzungen)

        session["match_loesung"] = loesung
        session["match_woerter"] = woerter
        session["match_uebersetzungen"] = uebersetzungen

        return render_template("quiz_match.html", woerter=woerter, uebersetzungen=uebersetzungen)

     # POST: prüfen -> 1 Punkt pro richtiges Paar
    loesung = session.get("match_loesung", {})   # z.B. {"Hund":"dog", ...}
    woerter = session.get("match_woerter", [])   # linke Liste (Reihenfolge)
    uebersetzungen = session.get("match_uebersetzungen", [])  # rechte Liste (Reihenfolge)

    punkte = session.get("quiz_punkte", 0)

    paare_json = request.form.get("paare_json", "[]")
    try:
        paare = json.loads(paare_json)  # [{l:0, r:3}, ...]
    except Exception:
        paare = []

    richtige_in_dieser_runde = 0

    # Wir prüfen jedes Paar:
    # linksIndex -> Wort, rechtsIndex -> Übersetzung
    # korrekt, wenn loesung[wort] == uebersetzung
    for p in paare:
        try:
            l_index = int(p.get("l"))
            r_index = int(p.get("r"))
        except Exception:
            continue

        if l_index < 0 or l_index >= len(woerter):
            continue
        if r_index < 0 or r_index >= len(uebersetzungen):
            continue

        wort = woerter[l_index]
        gewaehlte_uebersetzung = uebersetzungen[r_index]

        if wort in loesung and loesung[wort] == gewaehlte_uebersetzung:
            richtige_in_dieser_runde += 1

    # 1 Punkt pro richtiges Paar (max. 5)
    session["quiz_punkte"] = punkte + richtige_in_dieser_runde

    # Step weiter
    session["quiz_step_index"] = index + 1

    # Aufräumen
    session.pop("match_loesung", None)
    session.pop("match_woerter", None)
    session.pop("match_uebersetzungen", None)

    return redirect(url_for("quiz_naechster_step"))

    # POST: prüfen
    loesung = session.get("match_loesung", {})
    woerter = session.get("match_woerter", [])
    punkte = session.get("quiz_punkte", 0)

    richtige_in_dieser_runde = 0

    for i, wort in enumerate(woerter):
        ausgewaehlt = request.form.get(f"match_{i}", "")
        if wort in loesung and ausgewaehlt == loesung[wort]:
            richtige_in_dieser_runde += 1

    # Punkte hinzufügen (einfach: +1 pro richtiges Paar)
    session["quiz_punkte"] = punkte + richtige_in_dieser_runde

    # Step weiter
    session["quiz_step_index"] = session.get("quiz_step_index", 0) + 1

    # match session aufräumen
    session.pop("match_loesung", None)
    session.pop("match_woerter", None)
    session.pop("match_uebersetzungen", None)

    return redirect(url_for("quiz_naechster_step"))

    # ---------------------------
    # POST: Antwort auswerten
    # ---------------------------
    if request.method == "POST":
        richtige = session.get("quiz_richtige")
        gewaehlte = request.form.get("antwort", "")

        if richtige is not None and gewaehlte == richtige:
            session["quiz_punkte"] = punkte + 1
            lern_service.setze_vokabel_status(vok.id, "sicher")
        else:
            lern_service.setze_vokabel_status(vok.id, "unsicher")

        # ✅ Streak: heute wurde geübt
        lern_tag_service.uebung_heute_markieren(benutzer_id)

        session["quiz_index"] = index + 1
        return redirect(url_for("quiz_frage"))

    # ---------------------------
    # GET: Frage generieren
    # ---------------------------
    richtung = random.choice(["wort_zu_uebersetzung", "uebersetzung_zu_wort"])

    def optionen_bauen(richtige_antwort: str, pool: list[str], anzahl: int = 4) -> list[str]:
        pool_falsch = [x for x in pool if x != richtige_antwort]

        if len(pool_falsch) < anzahl - 1:
            optionen = [richtige_antwort] + pool_falsch
            random.shuffle(optionen)
            return optionen

        falsche = random.sample(pool_falsch, anzahl - 1)
        optionen = [richtige_antwort] + falsche
        random.shuffle(optionen)
        return optionen

    if richtung == "wort_zu_uebersetzung":
        frage = f"Wort: {vok.wort}"
        richtige = vok.uebersetzung
        pool = session.get("quiz_uebersetzungen_pool", [])
        optionen = optionen_bauen(richtige, pool, 4)
    else:
        frage = f"Übersetzung: {vok.uebersetzung}"
        richtige = vok.wort
        pool = session.get("quiz_woerter_pool", [])
        optionen = optionen_bauen(richtige, pool, 4)

    session["quiz_richtige"] = richtige

    return render_template(
        "quiz_frage.html",
        frage=frage,
        optionen=optionen,
        nummer=index + 1,
        gesamt=len(ids),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)