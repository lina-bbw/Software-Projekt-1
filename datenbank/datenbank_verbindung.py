# datenbank/datenbank_verbindung.py

import sqlite3
from pathlib import Path

# Name der SQLite-Datenbank-Datei
DATENBANK_DATEI = "vocabulary_builder.db"


def hole_datenbank_verbindung() -> sqlite3.Connection:
    """
    Stellt eine Verbindung zur SQLite-Datenbank her.
    Wenn die Datei noch nicht existiert, wird sie automatisch angelegt.
    """
    datenbank_pfad = Path(DATENBANK_DATEI)
    verbindung = sqlite3.connect(datenbank_pfad)
    verbindung.row_factory = sqlite3.Row
    return verbindung


def initialisiere_datenbank():
    """
    Legt die benötigten Tabellen an, falls sie noch nicht existieren.
    Wenn bereits eine ältere Version der Tabelle 'vokabel' existiert,
    wird versucht, die Spalte 'set_id' nachträglich hinzuzufügen.
    """

    verbindung = hole_datenbank_verbindung()
    cursor = verbindung.cursor()

    # Tabelle für Benutzer
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            passwort_hash TEXT NOT NULL,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    # Tabelle für Sets / Themen
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vokabel_set (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            benutzer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (benutzer_id) REFERENCES benutzer(id)
        );
        """
    )

    # Tabelle für Vokabeln (neues Design inkl. set_id)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vokabel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            benutzer_id INTEGER NOT NULL,
            wort TEXT NOT NULL,
            uebersetzung TEXT NOT NULL,
            beispielsatz TEXT,
            status TEXT DEFAULT 'neu', -- neu | unsicher | sicher
            set_id INTEGER,
            erstellt_am TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (benutzer_id) REFERENCES benutzer(id),
            FOREIGN KEY (set_id) REFERENCES vokabel_set(id)
        );
        """
    )

    # Falls es eine alte
