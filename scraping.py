import pandas as pd

# Lendo o arquivo Excel
df = pd.read_excel("teste.xls")
df = df.drop(df.index[0:3])

df.columns = df.iloc[0]
df = df.iloc[1:]

nomes_completos = df['Nome Completo'].str.capitalize()
print(nomes_completos)

nomes_sociais = df['Nome Social'].str.capitalize()

faz_uso = df['Faz uso do nome social nos documentos oficiais?']
faz_uso = faz_uso.str.lower()

email = df['E-mail']
print(email)
for nome_social, faz_uso in zip(nomes_sociais, faz_uso):
    if faz_uso == 'sim':
        print(nome_social)
