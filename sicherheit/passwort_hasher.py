# sicherheit/passwort_hasher.py

import hashlib


def hash_passwort(klartext_passwort: str) -> str:
    
    # Erzeugt aus einem Klartext-Passwort einen SHA256-Hash.
    # Hinweis: Für ein echtes Produktivsystem sollte ein Salt und z. B. bcrypt verwendet werden. 
    # Für das Studienprojekt reicht SHA256 aus.
   
    if klartext_passwort is None:
        raise ValueError("Passwort darf nicht None sein.")

    # Klartext in Bytes umwandeln
    passwort_bytes = klartext_passwort.encode("utf-8")

    # Hash berechnen
    hash_objekt = hashlib.sha256(passwort_bytes)
    passwort_hash = hash_objekt.hexdigest()

    return passwort_hash 

