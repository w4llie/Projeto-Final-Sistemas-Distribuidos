# Sistema Distribuído de Streaming de Música

Este projeto simula a arquitetura de uma plataforma de streaming de música, como Spotify ou Deezer, utilizando um sistema distribuído baseado em serviços e comunicação assíncrona/síncrona via **RabbitMQ**.

O foco principal é demonstrar a comunicação entre processos e a organização dos serviços, conforme os requisitos de arquitetura distribuída.

## Arquitetura Proposta (Visão Geral)

O sistema é composto pelos seguintes componentes principais:

1.  **Cliente (`client.py`):** Simula as ações do usuário (e.g., buscar música, criar playlist).
2.  **Gateway (`gateway.py`):** Atua como *middleware*, sendo o ponto único de entrada. Recebe as requisições do cliente e as coordena, encaminhando-as para os serviços apropriados.
3.  **Serviços Distribuídos (`services/`):** Processos separados que implementam funcionalidades específicas:
    *   **Catálogo Musical (`catalogo_service.py`):** Gerencia a base de dados de músicas.
    *   **Playlists (`playlists_service.py`):** Gerencia a criação e modificação de playlists.
    *   **Histórico (`historico_service.py`):** Registra o histórico de reprodução dos usuários.
4.  **Broker de Mensagens (RabbitMQ):** Responsável pela comunicação indireta e assíncrona entre os componentes.

## Comunicação entre Componentes

O projeto demonstra três tipos de comunicação:

| Tipo de Comunicação | Exemplo de Uso | Protocolo/Mecanismo |
| :--- | :--- | :--- |
| **Invocação Remota (RPC)** | Cliente -> Gateway -> Catálogo | RabbitMQ (Fila de Requisição/Resposta) |
| **Comunicação Indireta (Assíncrona)** | Cliente -> Gateway -> Playlists | RabbitMQ (Exchange `topic`) |
| **Comunicação Indireta (Assíncrona)** | Cliente -> Gateway -> Histórico | RabbitMQ (Exchange `topic`) |

## Estrutura de Arquivos

```
.
├── client.py           # Cliente interativo
├── gateway.py          # Middleware/Gateway
├── messaging.py        # Módulo de utilidades para RabbitMQ (RPC e Assíncrono)
├── requirements.txt    # Dependências do Python
└── services/
    ├── catalogo_service.py  # Serviço de Catálogo (RPC)
    ├── playlists_service.py # Serviço de Playlists (Assíncrono)
    └── historico_service.py # Serviço de Histórico (Assíncrono)
```

## Instruções de Execução

### 1. Pré-requisitos

*   **Python 3.10+**
*   **RabbitMQ Server:** O servidor RabbitMQ deve estar em execução na máquina local (`localhost`).

### 2. Instalação de Dependências

Instale a biblioteca `pika` (utilizada para comunicação com RabbitMQ):

```bash
pip install -r requirements.txt
```

### 3. Inicialização dos Serviços

Cada serviço deve ser executado em um terminal separado:

**Terminal 1: Serviço de Catálogo (RPC)**
```bash
python3 services/catalogo_service.py
```

**Terminal 2: Serviço de Playlists (Assíncrono)**
```bash
python3 services/playlists_service.py
```

**Terminal 3: Serviço de Histórico (Assíncrono)**
```bash
python3 services/historico_service.py
```

### 4. Execução do Cliente

Após a inicialização dos serviços, execute o cliente em um quarto terminal:

**Terminal 4: Cliente**
```bash
python3 client.py
```

O cliente apresentará um menu interativo para simular as ações do usuário e demonstrar os diferentes tipos de comunicação.

## Fluxo Esperado do Sistema

### Exemplo de Fluxo RPC (Catálogo)

1.  O usuário no `client.py` escolhe **Catálogo Musical**.
2.  O `client.py` envia a requisição ao `gateway.py`.
3.  O `gateway.py` usa o `RpcClient` do `messaging.py` para enviar a requisição para a fila `catalogo_rpc_queue`.
4.  O `catalogo_service.py` recebe a requisição, processa e envia a resposta de volta.
5.  O `gateway.py` recebe a resposta e a retorna ao `client.py`.
6.  O `client.py` exibe o resultado (síncrono).

### Exemplo de Fluxo Assíncrono (Playlists/Histórico)

1.  O usuário no `client.py` escolhe **Playlists** e **Criar Nova Playlist**.
2.  O `client.py` envia a requisição ao `gateway.py`.
3.  O `gateway.py` usa o `MessageBroker` do `messaging.py` para publicar uma mensagem no *exchange* `music_events` com a chave de roteamento apropriada (e.g., `playlist.criar`).
4.  O `playlists_service.py` (que está escutando a chave `playlist.*`) recebe a mensagem, processa e imprime a confirmação no seu terminal.
5.  O `gateway.py` retorna imediatamente ao `client.py` uma mensagem de sucesso (o processamento real ocorre de forma assíncrona).

**Nota:** A comunicação entre o `client.py` e o `gateway.py` neste exemplo é simulada por chamadas de função direta para simplificar a execução em um único ambiente. Em um sistema real, o `gateway.py` seria um servidor (e.g., HTTP/gRPC) que o cliente acessaria via rede.