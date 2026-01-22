import sys
import os
import time

# Adiciona o diretório pai ao path para importar messaging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging import rpc_server_setup

# Simulação de um banco de dados de músicas
CATALOGO_MUSICAS = {
    "1": {"titulo": "Bohemian Rhapsody", "artista": "Queen", "album": "A Night at the Opera", "ano": 1975},
    "2": {"titulo": "Stairway to Heaven", "artista": "Led Zeppelin", "album": "Led Zeppelin IV", "ano": 1971},
    "3": {"titulo": "Imagine", "artista": "John Lennon", "album": "Imagine", "ano": 1971},
    "4": {"titulo": "Smells Like Teen Spirit", "artista": "Nirvana", "album": "Nevermind", "ano": 1991},
    "5": {"titulo": "Like a Rolling Stone", "artista": "Bob Dylan", "album": "Highway 61 Revisited", "ano": 1965},
}

def handle_rpc_request(request_data):
    """
    Função que processa as requisições RPC para o serviço de catálogo.
    """
    acao = request_data.get("acao")
    
    if acao == "buscar_musica":
        musica_id = request_data.get("id")
        time.sleep(0.5) # Simula um processamento
        musica = CATALOGO_MUSICAS.get(musica_id)
        if musica:
            return {"status": "sucesso", "musica": musica}
        else:
            return {"status": "erro", "mensagem": f"Música com ID {musica_id} não encontrada."}
    
    elif acao == "listar_catalogo":
        time.sleep(1) # Simula um processamento mais longo
        return {"status": "sucesso", "catalogo": list(CATALOGO_MUSICAS.values())}
    
    else:
        return {"status": "erro", "mensagem": f"Ação desconhecida: {acao}"}

if __name__ == "__main__":
    try:
        # O nome da fila RPC será o nome do serviço
        rpc_server_setup("catalogo_rpc_queue", handle_rpc_request)
    except KeyboardInterrupt:
        print('Interrompido')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)