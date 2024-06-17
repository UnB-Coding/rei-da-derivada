from drf_yasg import openapi
from requests import status_codes

from requests import status_codes

sumula_imortal_api_put_schema = openapi.Schema(
    title='Sumula',
    type=openapi.TYPE_OBJECT,
    properties={
        'sumula': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID da sumula', example=1),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome da sumula', example='Sumula 1'),
                'referee': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        title='User',
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do usuário', example=1),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do usuário', example='João'),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Sobrenome do usuário', example='Silva'),
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
    },
    required=['sumula']
)

sumula_classicatoria_api_put_schema = openapi.Schema(
    title='Sumula',
    type=openapi.TYPE_OBJECT,
    properties={
        'sumula': openapi.Schema(
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
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do usuário', example=1),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do usuário', example='João'),
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
                            'points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Pontos do jogador', example=10),
                            'player': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                title='Player',
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID do jogador', example=1),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome completo do jogador', example='João Silva Jacinto '),
                                    'social_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome social do jogador', example='João Silva'),
                                    'is_imortal': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Jogador agora é imortal', example=True),
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
    },
    required=['sumula']
)


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
