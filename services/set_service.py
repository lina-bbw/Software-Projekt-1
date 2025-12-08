# services/set_service.py

from typing import List
from datenbank.set_repository import SetRepository
from modelle.vokabel_set import VokabelSet


class SetService:
    
    # Bietet einfache Funktionen rund um Sets / Themen.
    

    def __init__(self):
        self.set_repository = SetRepository()

    def set_anlegen(self, benutzer_id: int, name: str) -> int:
        
        # Legt ein neues Set an und gibt dessen ID zurück.
        
        if not name:
            print("Set-Name darf nicht leer sein.")
            return -1

        set_id = self.set_repository.set_anlegen(benutzer_id, name)
        print(f"Set '{name}' wurde angelegt (ID: {set_id}).")
        return set_id

    def hole_sets_fuer_benutzer(self, benutzer_id: int) -> List[VokabelSet]:
        
        # Gibt alle Sets eines Benutzers zurück.
        
        return self.set_repository.hole_alle_sets_fuer_benutzer(benutzer_id)
