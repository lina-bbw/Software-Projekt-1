import hashlib

# Diese Funktion erstellt einen SHA256-Hash aus einem Passwort
# Für ein Studentenprojekt ist das ok (produktiv würde man z.B. bcrypt + Salt nutzen)
def hash_passwort(passwort_klartext: str) -> str:
    if passwort_klartext is None:
        raise ValueError("Passwort darf nicht None sein.")

    passwort_bytes = passwort_klartext.encode("utf-8")
    hash_objekt = hashlib.sha256(passwort_bytes)
    return hash_objekt.hexdigest()
