# sicherheit/passwort_hasher.py

import hashlib


class PasswortHasher:
    """
    Einfache Hash-Klasse für Passwörter (Uni-/Projekt-Niveau).
    - Speichert nur Hash, nie Klartext
    - Nutzt SHA-256 (hashlib)

    Hinweis: In echten Produktivsystemen würde man zusätzlich Salt + bcrypt/argon2 nutzen.
    """

    @staticmethod
    def erstelle_hash(passwort: str) -> str:
        """
        Erzeugt einen SHA-256 Hash aus dem Passwort.
        """
        passwort_bytes = passwort.encode("utf-8")
        return hashlib.sha256(passwort_bytes).hexdigest()

    @staticmethod
    def pruefe_passwort(passwort_klartext: str, gespeicherter_hash: str) -> bool:
        """
        Prüft, ob das Klartext-Passwort (nach Hashing) dem gespeicherten Hash entspricht.
        """
        return PasswortHasher.erstelle_hash(passwort_klartext) == gespeicherter_hash