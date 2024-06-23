from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from ..models import Event, PlayerScore, SumulaImortal, SumulaClassificatoria, Player

EVENT_NOT_FOUND_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id do evento não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"
SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id da sumula não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"


class BaseSumulaView(APIView):
    """Classe base para as views de sumula. Contém métodos comuns a todas as views de sumula."""

    def validate_request_data(self, data):
        """Valida se os dados fornecidos na requisição estão no formato correto."""
        return data and isinstance(data, dict)

    def validate_players(self, data):
        """Valida se os jogadores fornecidos na requisição estão no formato correto."""
        if 'players' not in data:
            return False

        for player in data['players']:
            if 'id' not in player:
                return False

        return True

    def get_sumulas(self, event: Event, active: bool = None) -> tuple[list[SumulaImortal], list[SumulaClassificatoria]]:
        """Retorna as sumulas de um evento de acordo com o parâmetro active."""
        if active is None:
            sumula_imortal = SumulaImortal.objects.filter(
                event=event)
            sumula_classificatoria = SumulaClassificatoria.objects.filter(
                event=event)
        else:
            sumula_imortal = SumulaImortal.objects.filter(
                event=event, active=active)
            sumula_classificatoria = SumulaClassificatoria.objects.filter(
                event=event, active=active)
        return sumula_imortal, sumula_classificatoria

    def create_players_score(self, players: list, sumula: SumulaImortal | SumulaClassificatoria, event: Event,) -> None:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        for player in players:
            player_id = player.get('id')
            if player_id is None:
                continue
            player_obj = Player.objects.filter(id=player_id).first()
            if not player_obj:
                continue
            if sumula.__class__ == SumulaImortal:
                PlayerScore.objects.create(
                    player=player_obj, sumula_imortal=sumula, event=event)
            else:
                PlayerScore.objects.create(
                    player=player_obj, sumula_classificatoria=sumula, event=event)

    # def add_referee(self, sumula: Sumula, referees: list) -> None:
    #     """Adiciona um árbitro a uma sumula."""
    #     for referee in referees:
    #         user = User.objects.filter(id=referee['id']).first()
    #         if not user:
    #             continue
    #         sumula.referee.add(user)
    # Necessario refatorar com outra rota

    def update_player_score(self, players_score: list[dict]) -> bool:
        """Atualiza a pontuação de um jogador."""
        for player_score in players_score:
            player_score_id = player_score.get('id')
            if player_score_id is None:
                return False
            player_score_obj = PlayerScore.objects.filter(
                id=player_score_id).first()
            if not player_score_obj:
                return False
            player_score_obj.points = player_score['points']
            player_score_obj.save()
        return True

    def get_object(self) -> Event:
        """ Verifica se o evento existe.
        Retorna o evento associado ao id fornecido ou uma exceção.
        """
        if 'event_id' not in self.request.query_params:
            raise ValidationError(EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE)
        event_id = self.request.query_params.get('event_id')
        if not event_id:
            raise ValidationError(EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE)
        event = Event.objects.filter(id=event_id).first()
        if not event:
            raise NotFound(EVENT_NOT_FOUND_ERROR_MESSAGE)
        return event
