# from api.utils import generate_random_name, create_unique_email
import os
import pandas as pd
import uuid
import random


def create_unique_email():
    return f'{uuid.uuid4()}@gmail.com'


def create_unique_username():
    return f'user_{uuid.uuid4().hex[:10]}'


def generate_random_name():
    names = ['João', 'José', 'Pedro', 'Paulo', 'Lucas', 'Mário', 'Luiz', 'Carlos', 'Ricardo', 'Roberto',
             'Maria', 'Ana', 'Clara', 'Lúcia', 'Luíza', 'Mariana', 'Carla', 'Rita', 'Rosa', 'Beatriz', 'Juliana', 'Júlia', 'Laura', 'Lara']
    last_names = ['Silva', 'Oliveira', 'Martins', 'Souza', 'Costa', 'Santos', 'Pereira', 'Almeida', 'Carvalho', 'Ferreira', 'Rodrigues', 'Gomes', 'Alves', 'Lima', 'Araújo', 'Melo', 'Barbosa', 'Ribeiro', 'Albuquerque', 'Marques', 'Vieira', 'Correia', 'Cavalcanti', 'Dias', 'Castro', 'Campos', 'Cardoso', 'Nunes', 'Peixoto', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos',
                  'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal', 'Guimarães', 'Barros', 'Freitas', 'Vasconcelos', 'Braga', 'Moraes', 'Moraes', 'Monteiro', 'Mendes', 'Leal']
    return f'{names[random.randint(0, len(names) - 1)]+" "+last_names[random.randint(0, len(last_names) - 1)]+" "+last_names[random.randint(0, len(last_names) - 1)]}'


""" Função para popular o arquivo excel de testes.
Nome completo, Nome social e email.
"""
data = {
    'Nome Completo': [generate_random_name() for _ in range(10)],
    'Nome Social': [generate_random_name() for _ in range(10)],
    'E-mail': [create_unique_email() for _ in range(10)]
}
df = pd.DataFrame(data)
df.to_csv('/usr/src/api/config/files_tests/excel/Exemplo.csv',
          index=False, columns=['Nome Completo', 'Nome Social', 'E-mail'], sep=',', encoding='utf-8')
df.to_excel(
    '/usr/src/api/config/files_tests/excel/Exemplo.xlsx', index=False, columns=['Nome Completo', 'Nome Social', 'E-mail'])
print('Arquivo excel populado com sucesso!')
