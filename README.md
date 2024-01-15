# rei-da-derivada
### 💻 Ambiente

Para configurar o ambiente, você pode rodar o seguinte script:

```bash
make config
```

### 📁 Dependências do projeto

Para instalar as dependências do projeto, você pode rodar os seguintes comando:

```bash
# Crie um ambiente virtual Python
python3 -m venv api/env

# Ative o ambiente virtual
source api/env/bin/activate

# Instale os pacotes do Python e Node
make install
```

### 💾 Execução

Para executar o projeto, você pode rodar o seguinte comando:

```bash
docker compose up
```

#### Observações do Docker

```bash
# Se você quiser rodar em segundo plano
docker compose up -d

# Se alterações foram feitas no Dockerfile ou no docker-compose.yml
docker compose up --build

# Se for necessário deletar os volumes
docker compose down -v
```
