# services/lern_service.py

from datenbank.vokabel_repository import VokabelRepository


class LernService:
    """
    Logik für:
    - Vokabeln (CRUD)
    - Status setzen (sicher/unsicher)
    """

    def __init__(self):
        self.vokabel_repository = VokabelRepository()

    def neue_vokabel_anlegen(
        self,
        benutzer_id: int,
        wort: str,
        uebersetzung: str,
        beispielsatz: str | None,
        bemerkungen: str | None,
        set_id: int | None,
    ) -> None:
        if not wort or not uebersetzung:
            return

        self.vokabel_repository.vokabel_anlegen(
            benutzer_id=benutzer_id,
            wort=wort,
            uebersetzung=uebersetzung,
            beispielsatz=beispielsatz,
            bemerkungen=bemerkungen,
            set_id=set_id,
        )

    def hole_alle_vokabeln(self, benutzer_id: int, set_id: int | None = None):
        return self.vokabel_repository.hole_alle_vokabeln_fuer_benutzer(benutzer_id, set_id)

    def aktualisiere_vokabel(
        self,
        vokabel_id: int,
        neues_wort: str,
        neue_uebersetzung: str,
        neuer_beispielsatz: str | None,
        neue_bemerkungen: str | None,
        neues_set_id: int | None,
    ) -> None:
        self.vokabel_repository.aktualisiere_vokabel(
            vokabel_id=vokabel_id,
            neues_wort=neues_wort,
            neue_uebersetzung=neue_uebersetzung,
            neuer_beispielsatz=neuer_beispielsatz,
            neue_bemerkungen=neue_bemerkungen,
            neues_set_id=neues_set_id,
        )

    def loesche_vokabel(self, vokabel_id: int) -> None:
        self.vokabel_repository.vokabel_loeschen(vokabel_id)

    def setze_vokabel_status(self, vokabel_id: int, neuer_status: str) -> None:
        self.vokabel_repository.aktualisiere_status(vokabel_id, neuer_status)