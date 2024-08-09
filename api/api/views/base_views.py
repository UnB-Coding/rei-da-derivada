from django.utils.deprecation import MiddlewareMixin
from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from ..models import Event, PlayerScore, Staff, SumulaImortal, SumulaClassificatoria, Player

EVENT_NOT_FOUND_ERROR_MESSAGE = "Evento não encontrado!"
EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id do evento não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"
SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id da sumula não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"


class BaseView(APIView):
    def get_object(self) -> Event:
        """ Verifica se o evento existe.
        Retorna o evento associado ao id fornecido ou uma exceção.
        - ValidationError: Se o id do evento não foi fornecido.
        - NotFound: Se o evento não foi encontrado.
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


class BaseSumulaView(BaseView):
    """Classe base para as views de sumula. Contém métodos comuns a todas as views de sumula."""

    def validate_request_data_dict(self, data):
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

    def validate_players_score(self, data):
        """Valida se os jogadores fornecidos na requisição estão no formato correto."""
        if 'players_score' not in data:
            return False

        for player_score in data['players_score']:
            if 'points' not in player_score or 'player' not in player_score:
                return False
            if 'id' not in player_score['player']:
                return False

        return True

    def validate_referees(self, data):
        """Valida se os árbitros fornecidos na requisição estão no formato correto."""
        if 'referees' not in data:
            return False

        for referee in data['referees']:
            if 'id' not in referee:
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

    def create_players_score(self, players: list, sumula: SumulaImortal | SumulaClassificatoria, event: Event,) -> None | ValidationError:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        for player in players:
            player_id = player.get('id')
            if player_id is None:
                continue
            player_obj = Player.objects.filter(id=player_id).first()
            if not player_obj:
                raise ValidationError(
                    f"Jogador {player.get('name')} não encontrado!")
            if sumula.__class__ == SumulaImortal:
                PlayerScore.objects.create(
                    player=player_obj, sumula_imortal=sumula, event=event)
            else:
                PlayerScore.objects.create(
                    player=player_obj, sumula_classificatoria=sumula, event=event)

    def add_referees(self, sumula: SumulaImortal | SumulaClassificatoria, event: Event, referees: list) -> None:
        """Adiciona um árbitro a uma sumula."""
        if referees == []:
            return
        for referee in referees:
            staff = Staff.objects.filter(id=referee['id'], event=event).first()
            if referee is not None:
                sumula.referee.add(staff)
        sumula.save()

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

    def update_sumula(self, sumula: SumulaImortal | SumulaClassificatoria, event: Event) -> None | ValidationError:
        """Atualiza uma sumula."""
        players_score = self.request.data['players_score']

        if not self.update_player_score(players_score):
            raise ValidationError("Dados de pontuação inválidos!")
        sumula.name = self.request.data['name']
        sumula.description = self.request.data['description']
        sumula.active = False
        sumula.save()

    def validate_if_staff_is_sumula_referee(self, sumula: SumulaClassificatoria | SumulaImortal, event: Event) -> Exception | Staff:
        staff = Staff.objects.filter(
            user=self.request.user, event=event).first()
        if not staff:
            raise ValidationError("Usuário não é um monitor do evento!")

        if not staff in sumula.referee.all():
            raise ValidationError("Usuário não é um árbitro da sumula!")
        return staff

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


# middleware.py


class DisableCSRFMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Desativar CSRF para POST, PUT, DELETE
        if request.method in ['POST', 'PUT', 'DELETE']:
            setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
