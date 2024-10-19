from ..models import Event, PlayerScore, Staff, SumulaImortal, SumulaClassificatoria, Player
from ..serializers import PlayerScoreForRoundRobinSerializer
from io import StringIO
from django.db import transaction
# from django.db.models import BaseManager
import chardet
from django.utils.deprecation import MiddlewareMixin
from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
import logging

logger = logging.getLogger(__name__)

EVENT_NOT_FOUND_ERROR_MESSAGE = 'Evento não encontrado!'
EVENT_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id do evento não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"
SUMULA_ID_NOT_PROVIDED_ERROR_MESSAGE = "Id da sumula não fornecido!"
SUMULA_NOT_FOUND_ERROR_MESSAGE = "Sumula não encontrada!"


class BaseView(APIView):
    def get_event(self) -> Event:
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
            raise ValidationError(EVENT_NOT_FOUND_ERROR_MESSAGE)
        return event

    def treat_name_and_email_excel(self, name: str, email: str) -> tuple[str, str]:
        """Trata o nome e o email de um jogador para serem inseridos no banco de dados."""
        if name.__class__ != str or email.__class__ != str:
            raise ValidationError('Nome ou email inválidos!')
        name = name.strip().lower()
        email = email.strip().lower()
        for word in name.split():
            name = name.replace(word, word.capitalize())
        return name, email

    def treat_csv(self, file) -> tuple[StringIO, str]:
        """Trata um arquivo CSV para ser lido pelo pandas.
        Lidando com a codificação do arquivo e convertendo-o em um StringIO.
        """
        raw_data = file.read()
        detection = chardet.detect(raw_data)
        encoding = detection['encoding']
        file_data = raw_data.decode(encoding)
        # Converte a string em um StringIO, que pode ser lido pelo pandas
        csv_data = StringIO(file_data)
        return csv_data, encoding

    def get_delimiter(self, csv_data):
        first_line = csv_data.readline()
        csv_data.seek(0)  # Resetar o ponteiro para o início do arquivo
        if ';' in first_line:
            return ';'
        else:
            return ','


class BaseSumulaView(BaseView):
    """Classe base para as views de sumula. Contém métodos comuns a todas as views de sumula."""

    def round_robin_tournament(self, n: int, players_score: list[PlayerScore]) -> list[list[dict[dict]]] | Exception:
        """Gera os pares de jogadores para um torneio com n-1 rodadas.
        Todos os jogadores jogam com todos os outros jogadores em formato de duplas"""

        if len(players_score) != n:
            raise Exception(
                "Número de jogadores não corresponde ao número fornecido!")

        if n % 2 != 0:
            players_score.append(None)
            n += 1

        ordem = {
            4: [
                [(1, 2), (3, 4)],
                [(1, 3), (2, 4)],
                [(1, 4), (2, 3)]
            ],
            6: [
                [(1, 2), (3, 4), (5, 6)],
                [(1, 3), (2, 5), (4, 6)],
                [(1, 4), (2, 3), (5, 6)],
                [(1, 5), (2, 4), (3, 6)],
                [(1, 6), (2, 5), (3, 4)]
            ],
            8: [
                [(1, 2), (3, 4), (5, 6), (7, 8)],
                [(1, 3), (2, 4), (5, 7), (6, 8)],
                [(1, 4), (2, 3), (5, 8), (6, 7)],
                [(1, 5), (2, 6), (3, 7), (4, 8)],
                [(1, 6), (2, 5), (3, 8), (4, 7)],
                [(1, 7), (2, 8), (3, 5), (4, 6)],
                [(1, 8), (2, 7), (3, 6), (4, 5)]
            ]
        }

        if n not in ordem:
            raise Exception(
                "Número de jogadores insuficiente para formar duplas!")

        # Mapear os jogadores para os seus respectivos números
        player_map = {i + 1: players_score[i] for i in range(n)}

        # Gerar os pares de jogadores conforme a ordem predefinida
        numbered_rounds = []
        # print('length players_score', len(players_score))
        for round_pairs in ordem[n]:
            numbered_round = []
            for p1, p2 in round_pairs:
                player1 = player_map[p1]
                player2 = player_map[p2] if p2 <= len(players_score) else None
                # print(f"p1: {p1} p2: {p2}")
                # print(f"player1: {player1} player2: {player2}")
                if player1 is not None and player1.rounds_number == 0:
                    player1.rounds_number = p1
                    player1.save()
                if player2 is not None and player2.rounds_number == 0:
                    player2.rounds_number = p2
                    player2.save()
                numbered_round.append((player1, player2))
            numbered_rounds.append(numbered_round)

        # Caso o número de jogadores seja ímpar (5 ou 7), garantir que um jogador jogue sozinho a cada rodada
        # if n % 2 != 0:
        #     print("Jogador sozinho NUMERO IMPAR")
        #     for i, round in enumerate(numbered_rounds):
        #         for j, pair in enumerate(round):
        #             if pair[1] is None:
        #                 player1 = pair[0]
        #                 player1.rounds_number = ordem[n][i][j][0]
        #                 numbered_rounds[i][j] = (player1, None)

        # Serializar os dados corretamente
        serialized_rounds = []
        for round in numbered_rounds:
            serialized_round = []
            for pair in round:
                serialized_pair = {
                    'player1': PlayerScoreForRoundRobinSerializer(pair[0]).data if pair[0] else None,
                    'player2': PlayerScoreForRoundRobinSerializer(pair[1]).data if pair[1] else None
                }
                serialized_round.append(serialized_pair)
            serialized_rounds.append(serialized_round)
        # k = 1
        # for round in serialized_rounds:
        #     print(f"Rodada {k}")
        #     for pair in round:
        #         if pair['player2'] is None:
        #             print(
        #                 f"{pair['player1']['player']['full_name']} {pair['player1']['rounds_number']} E {pair['player2']} ")
        #         else:
        #             print(
        #                 f"{pair['player1']['player']['full_name']} {pair['player1']['rounds_number']} E {pair['player2']['rounds_number']} {pair['player2']['player']['full_name']}")
        #     k += 1

        return serialized_rounds

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

    def get_sumulas(self, event: Event, active: bool = None) -> tuple[SumulaClassificatoria, SumulaImortal]:
        """Retorna as sumulas de um evento de acordo com o parâmetro active."""
        if active is None:
            sumula_imortal = SumulaImortal.objects.filter(
                event=event).order_by('name')
            sumula_classificatoria = SumulaClassificatoria.objects.filter(
                event=event).order_by('name')
        else:
            sumula_imortal = SumulaImortal.objects.filter(
                event=event, active=active).order_by('name')
            sumula_classificatoria = SumulaClassificatoria.objects.filter(
                event=event, active=active).order_by('name')
        return sumula_imortal, sumula_classificatoria

    def create_players_score(self, players: list, sumula: SumulaImortal | SumulaClassificatoria, event: Event,) -> list[PlayerScore] | ValidationError:
        """Cria uma lista de PlayerScore associados a uma sumula."""
        players_score = []
        try:
            with transaction.atomic():
                for player in players:
                    player_id = player.get('id')
                    if player_id is None:
                        continue
                    player_obj = Player.objects.select_for_update().filter(id=player_id).first()
                    if not player_obj:
                        raise ValidationError(
                            f"Jogador {player.get('name')} não encontrado!")
                    if sumula.__class__ == SumulaImortal:
                        players_score.append(PlayerScore.objects.create(
                            player=player_obj, sumula_imortal=sumula, event=event))
                    else:
                        players_score.append(PlayerScore.objects.create(
                            player=player_obj, sumula_classificatoria=sumula, event=event))
                logger.info(
                    f"{len(players_score)} PlayerScores criados para a sumula {sumula.id}")
            return players_score
        except Exception as e:
            logger.error(
                f"Erro ao criar PlayerScores para a sumula {sumula.id}: {e}")
            raise ValidationError("Erro ao criar PlayerScores!")

    def add_referees(self, sumula: SumulaImortal | SumulaClassificatoria, event: Event, referees: list) -> None:
        """Adiciona um árbitro a uma sumula."""
        if referees == []:
            return
        for referee in referees:
            id = referee.get('id')
            if id is None:
                continue
            staff = Staff.objects.filter(id=id, event=event).first()
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

        if 'imortal_players' in self.request.data:
            players = self.request.data['imortal_players']
            for player in players:
                player_id = player.get('id')
                if player_id is None:
                    continue
                player_obj = Player.objects.filter(id=player_id).first()
                if not player_obj:
                    raise ValidationError("Jogador não encontrado!")
                player_obj.is_imortal = True
                player_obj.save()

        sumula.description = self.request.data['description']
        sumula.active = False
        if sumula.__class__ != SumulaImortal:
            sumula.name = self.request.data['name']
        sumula.save()

    def validate_if_staff_is_sumula_referee(self, sumula: SumulaClassificatoria | SumulaImortal, event: Event) -> Exception | Staff:
        staff = Staff.objects.filter(
            user=self.request.user, event=event).first()
        if not staff:
            raise ValidationError("Usuário não é um monitor do evento!")

        if not staff in sumula.referee.all():
            raise ValidationError("Usuário não é um árbitro da sumula!")
        return staff
# middleware.py


# class DisableCSRFMiddleware(MiddlewareMixin):
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Desativar CSRF para POST, PUT, DELETE
#         if request.method in ['POST', 'PUT', 'DELETE']:
#             setattr(request, '_dont_enforce_csrf_checks', True)
#         response = self.get_response(request)
#         return response
