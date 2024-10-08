from drf_yasg import openapi
from requests import status_codes

from requests import status_codes

sumula_imortal_api_put_schema = openapi.Schema(
    title='Sumula',
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula', example='Imortais 01'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descrição da sumula', example='Sala S4'),
        'referee': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                title='Staff',
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do staff', example=1),
                    'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do staff', example='João'),
                    'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Sobrenome do staff', example='Silva'),
                },
                required=['id']
            )
        ),
        'players_score': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                title='PlayerScore',
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto de pontuacao do jogador', example=1),
                    'points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontos do jogador', example=10),
                    'player': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        title='Player',
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                            'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                        },
                        required=['id']
                    ),
                },
                required=['points', 'player']
            )
        ),
    },
    required=['id', 'name', 'referee', 'players_score']
)

sumula_classicatoria_api_put_schema = openapi.Schema(
    title='Sumula',
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula', example='Chave A'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descrição da sumula', example='Sala S4'),
        'referee': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                title='Staff',
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do staff', example=1),
                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do staff', example='João'),
                },
                required=['id']
            )
        ),
        'players_score': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                title='PlayerScore',
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto de pontuacao do jogador', example=1),
                    'points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontos do jogador', example=10),
                    'player': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        title='Player',
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                            'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                            'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Se o jogador é imortal', example=True),
                        },
                        required=['id']
                    ),
                },
                required=['points', 'player']
            )
        ),
        'imortal_players': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
            type=openapi.TYPE_OBJECT, description='ID dos jogadores imortais', properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
            })),
    },
    required=['id', 'name', 'referee', 'players_score', 'imortal_players']
)

indivual_sumulas_response_schema = openapi.Schema(title='Sumula', type=openapi.TYPE_OBJECT, properties={
    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
    'active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Se a sumula está ativa', example=True),
    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula', example='Sumula 1'),
    'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descrição da sumula', example='Sala S4'),
    'referee': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Staff',
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do staff', example=1),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do staff', example='João'),
            },
            required=['id']
        )
    ),
    'players_score': openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            title='PlayerScore',
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do objeto de pontuacao do jogador', example=1),
                'points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontos do jogador', example=10),
                'rounds_number': openapi.Schema(type=openapi.TYPE_INTEGER, description='Numero do jogador durante a partida', example=1),
                'player': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title='Player',
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                        'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                        'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Se o jogador é imortal', example=True),
                    },
                    required=['id']
                ),
            },
            required=['points', 'player']
        )
    ),
    'rounds': openapi.Schema(
        title='Rodadas da partida',
        description='Lista de rodadas da partida',
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            title='Duplas da rodada',
            description='Lista de tuplas com as duplas da rodada',
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                title='Uma dupla da rodada',
                description='Tupla com as informações de uma dupla da rodada',
                type=openapi.TYPE_OBJECT,
                properties={
                    'player1': openapi.Schema(
                        title='Jogador 1',
                        type=openapi.TYPE_OBJECT,
                        description='Jogador 1 da dupla',
                        properties={
                            'id': openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description='ID do objeto Player_Score do jogador',
                                    example=1
                            ),
                            'rounds_number': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Numero do jogador durante a partida',
                                example=1
                            ),
                            'player': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description='Objeto Player do jogador',
                                properties={
                                    "id": openapi.Schema(
                                            type=openapi.TYPE_INTEGER,
                                            description='ID do jogador',
                                            example=1
                                    ),
                                    "full_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Nome completo do jogador',
                                        example='João Silva Jacinto '
                                    ),
                                    "social_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Nome social do jogador',
                                        example='João Silva'
                                    ),
                                },
                                required=['id', 'full_name',
                                          'social_name', 'is_imortal']
                            ),
                        },
                    ),
                    'player2': openapi.Schema(
                        title='Jogador 2',
                        type=openapi.TYPE_OBJECT, description='Jogador 2 da dupla',
                        properties={
                            'id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID do objeto Player_Score do jogador',
                                example=1
                            ),
                            'rounds_number': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Numero do jogador durante a partida',
                                example=2
                            ),
                            'player': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description='Objeto Player do jogador',
                                properties={
                                    "id": openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='ID do jogador',
                                        example=1
                                    ),
                                    "full_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Nome completo do jogador',
                                        example='João Silva Jacinto '
                                    ),
                                    "social_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description='Nome social do jogador',
                                        example='João Silva'
                                    ),
                                },
                            ),
                        },

                    )
                },
            ),
        ),
    ),

})

sumulas_response_schema = openapi.Schema(
    title='Sumulas', type=openapi.TYPE_OBJECT,
    properties={
        "sumulas_classificatoria": openapi.Schema(
            title='Sumula Classificatoria', type=openapi.TYPE_ARRAY,
            items=indivual_sumulas_response_schema
        ),
        "sumulas_imortal": openapi.Schema(
            type=openapi.TYPE_ARRAY, title='Sumula Imortal',
            items=indivual_sumulas_response_schema
        )
    }
)

sumulas_response_for_player_schema = openapi.Schema(
    title='Sumulas', type=openapi.TYPE_ARRAY,
    items=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula', example='Sumula 1'),
            'referee': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title='Staff',
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do staff', example=1),
                        'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do staff', example='João'),
                    },
                    required=['id']
                )
            ),
            'players_score': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    title='PlayerScore',
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'player': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            title='Player',
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                                'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                                'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Se o jogador é imortal', example=True),
                            },
                            required=['id']
                        ),
                    },
                    required=['player']
                )
            ),
            'rounds': openapi.Schema(
                title='Rodadas da partida',
                description='Lista de rodadas da partida',
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    title='Duplas da rodada',
                    description='Lista de tuplas com as duplas da rodada',
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        title='Uma dupla da rodada',
                        description='Tupla com as informações de uma dupla da rodada',
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'player1': openapi.Schema(
                                title='Jogador 1',
                                type=openapi.TYPE_OBJECT,
                                description='Jogador 1 da dupla',
                                properties={
                                    'id': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='ID do objeto Player_Score do jogador',
                                        example=1
                                    ),
                                    'points': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Pontos do jogador na sumula',
                                        example=10
                                    ),
                                    'rounds_number': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Numero do jogador durante a partida',
                                        example=5
                                    ),
                                    'player': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        description='Objeto Player do jogador',
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description='ID do jogador',
                                                example=1
                                            ),
                                            "full_name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='Nome completo do jogador',
                                                example='João Silva Jacinto '
                                            ),
                                            "social_name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='Nome social do jogador',
                                                example='João Silva'
                                            ),
                                            "is_imortal": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN,
                                                description='Se o jogador é imortal',
                                                example=True
                                            ),
                                        },
                                        required=['id', 'full_name',
                                                  'social_name', 'is_imortal']
                                    ),
                                },
                                required=['id', 'points',
                                          'rounds_number', 'player']
                            ),
                            'player2': openapi.Schema(
                                title='Jogador 2',
                                type=openapi.TYPE_OBJECT, description='Jogador 2 da dupla',
                                properties={
                                    'id': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='ID do objeto Player_Score do jogador',
                                        example=1
                                    ),
                                    'rounds_number': openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description='Numero do jogador durante a partida',
                                        example=2
                                    ),
                                    'player': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        description='Objeto Player do jogador',
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description='ID do jogador',
                                                example=1
                                            ),
                                            "full_name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='Nome completo do jogador',
                                                example='João Silva Jacinto '
                                            ),
                                            "social_name": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description='Nome social do jogador',
                                                example='João Silva'
                                            ),
                                        },
                                    ),
                                },

                            )

                        },
                        required=['player1']
                    ),
                ),
            ),

        }
    )
)

manual_parameter_event_id = [openapi.Parameter(
    'event_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Id do evento')]

array_of_sumulas_response_schema = openapi.Schema(
    title='Sumulas', type=openapi.TYPE_ARRAY, items=indivual_sumulas_response_schema)


class Errors():

    def __init__(self, erros: list[int]) -> None:
        self.erros = erros

    def get_schema(self) -> openapi.Schema:
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'errors': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Mensagem de erro'
                ),
            }
        )

    def add_error(self, swagger_erros: dict[openapi.Response], error: int, key_error: KeyError):
        check_error = str(error).startswith('4') or str(error).startswith('5')
        if check_error:
            message = status_codes._codes[error][0].upper()
            swagger_erros[error] = openapi.Response(message, self.get_schema())
        else:  # pragma: no cover
            raise key_error

    def retrieve_erros(self) -> dict[openapi.Response]:
        swagger_erros = dict()

        for error in self.erros:
            key_error = KeyError(f'Code {error} is not a valid HTTP error.')

            try:
                self.add_error(swagger_erros, error, key_error)
            except KeyError:  # pragma: no cover
                raise key_error

        return swagger_erros
