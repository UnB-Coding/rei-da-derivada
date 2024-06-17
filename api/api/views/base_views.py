from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from views_sumulas import EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE, EVENT_NOT_FOUND_ERROR_MESSAGE
from ..models import Event, PlayerScore, Sumula, Player


class BaseSumulaView(APIView):
    def create_players_score(self, players: list, sumula: Sumula, event: Event) -> None:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        for player in players:
            player_id = player.get('id')
            if player_id is None:
                continue
            player_obj = Player.objects.filter(id=player_id).first()
            if not player_obj:
                continue
            PlayerScore.objects.create(
                player=player_obj, sumula=sumula, event=event)

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
        """ Verifica se o evento existe e se o usuário tem permissão para acessá-lo.
        Retorna o evento associado ao id fornecido.
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
