from rest_framework import status, response
from django.contrib.contenttypes.models import ContentType
from rest_framework import status, response
from django.contrib.auth.models import Permission
import random


def handle_400_error(error_msg: str) -> response.Response:
    """ Função para lidar com erros 400."""
    return response.Response(
        {
            "errors": error_msg
        }, status.HTTP_400_BAD_REQUEST)


def get_content_type(model):
    """ Função para retornar o content type de um modelo."""
    return ContentType.objects.get_for_model(model)


def get_permissions(content_type):
    """ Função para retornar as permissões de um content type."""
    return Permission.objects.filter(content_type=content_type)


def generate_random_name():
    names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz', 'Carlos', 'Ricardo', 'Roberto',
             'Maria', 'Ana', 'Clara', 'Lúcia', 'Luíza', 'Mariana', 'Carla', 'Rita', 'Rosa', 'Beatriz', 'Juliana', 'Júlia', 'Laura', 'Lara']
    last_names = ['Silva', 'Oliveira', 'Martins', 'Souza', 'Costa', 'Santos', 'Pereira', 'Almeida', 'Carvalho', 'Ferreira', 'Rodrigues', 'Gomes', 'Alves', 'Lima', 'Araújo', 'Melo', 'Barbosa', 'Ribeiro', 'Albuquerque', 'Marques', 'Vieira', 'Correia', 'Cavalcanti', 'Dias', 'Castro', 'Campos', 'Cardoso', 'Nunes', 'Peixoto', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos',
                  'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal']
    return f'{names[random.randint(0, len(names) - 1)]+" "+last_names[random.randint(0, len(last_names) - 1)]+" "+last_names[random.randint(0, len(last_names) - 1)]}'
