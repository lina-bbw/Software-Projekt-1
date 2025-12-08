# datenbank/benutzer_repository.py

from typing import Optional
from datenbank.datenbank_verbindung import hole_datenbank_verbindung
from modelle.benutzer import Benutzer


class BenutzerRepository:
    
    # Kümmert sich um alle Datenbankzugriffe rund um den Benutzer.
    

    def registriere_benutzer(self, email: str, passwort_hash: str) -> bool:
        
        # Legt einen neuen Benutzer an.
        # Gibt True zurück, wenn das Anlegen geklappt hat,
        # ansonsten False (z. B. wenn die E-Mail schon existiert).
        
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        try:
            cursor.execute(
                
                # INSERT INTO benutzer (email, passwort_hash)
                # VALUES (?, ?);
                
                (email, passwort_hash),
            )
            verbindung.commit()
            return True
        except Exception as fehler:
            print("Fehler beim Registrieren:", fehler)
            return False
        finally:
            verbindung.close()

    def finde_benutzer_nach_email(self, email: str) -> Optional[Benutzer]:
        
        # Sucht einen Benutzer anhand seiner E-Mail-Adresse.
        # Gibt ein Benutzer-Objekt zurück oder None, wenn nichts gefunden wurde.
        
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            
            # SELECT id, email
            # FROM benutzer
            # WHERE email = ?;
            
            (email,),
        )

        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return None

        return Benutzer(benutzer_id=zeile["id"], email=zeile["email"])

    def hole_passwort_hash(self, email: str) -> Optional[str]:
       
        # Gibt den gespeicherten Passwort-Hash zur E-Mail zurück oder None, wenn kein Benutzer existiert.
        
        verbindung = hole_datenbank_verbindung()
        cursor = verbindung.cursor()

        cursor.execute(
            
            # SELECT passwort_hash
            # FROM benutzer
            # WHERE email = ?;
            
            (email,),
        )
        zeile = cursor.fetchone()
        verbindung.close()

        if zeile is None:
            return None

        return zeile["passwort_hash"]
