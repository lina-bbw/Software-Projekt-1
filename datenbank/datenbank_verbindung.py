# datenbank/datenbank_verbindung.py

import sqlite3
import os

# ✅ DB-Pfad immer stabil (egal wie du startest)
BASIS_ORDNER = os.path.dirname(os.path.abspath(__file__))
DB_PFAD = os.path.join(BASIS_ORDNER, "..", "vocabulary_builder.db")


def hole_datenbank_verbindung():
    """
    Öffnet die SQLite-Datenbank.
    Debug-Ausgabe zeigt, welche DB wirklich genutzt wird.
    """
    print("DB-PFAD (Flask nutzt):", os.path.abspath(DB_PFAD))
    verbindung = sqlite3.connect(DB_PFAD)
    verbindung.row_factory = sqlite3.Row
    return verbindung


def initialisiere_datenbank():
    """
    Legt Tabellen an, falls sie noch nicht existieren.
    """
    verbindung = hole_datenbank_verbindung()
    cursor = verbindung.cursor()

    # Benutzer
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS benutzer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        passwort_hash TEXT NOT NULL
    );
    """)

    # Sets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vokabel_set (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        benutzer_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (benutzer_id) REFERENCES benutzer(id)
    );
    """)

    # Vokabeln
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vokabel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        benutzer_id INTEGER NOT NULL,
        wort TEXT NOT NULL,
        uebersetzung TEXT NOT NULL,
        beispielsatz TEXT,
        status TEXT NOT NULL DEFAULT 'neu',
        set_id INTEGER,
        FOREIGN KEY (benutzer_id) REFERENCES benutzer(id),
        FOREIGN KEY (set_id) REFERENCES vokabel_set(id)
    );
    """)

    verbindung.commit()
    verbindung.close()
