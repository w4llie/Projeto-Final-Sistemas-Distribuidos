import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging import MessageBroker

PLAYLISTS = {}

def handle_async_message(ch, method, properties, body):
    """
    Função que processa as mensagens assíncronas para o serviço de playlists.
    """
    try:
        message = json.loads(body.decode('utf-8'))
        acao = message.get("acao")
        
        if acao == "criar_playlist":
            user_id = message.get("user_id")
            playlist_name = message.get("nome")
            
            if user_id not in PLAYLISTS:
                PLAYLISTS[user_id] = []
            
            PLAYLISTS[user_id].append({"nome": playlist_name, "musicas": []})
            
            print(f" [✓] Playlist '{playlist_name}' criada para o usuário {user_id}. Playlists atuais: {PLAYLISTS.get(user_id)}")
            
        elif acao == "adicionar_musica":
            user_id = message.get("user_id")
            playlist_name = message.get("playlist")
            musica_id = message.get("musica_id")
            
            if user_id in PLAYLISTS:
                for playlist in PLAYLISTS[user_id]:
                    if playlist["nome"] == playlist_name:
                        playlist["musicas"].append(musica_id)
                        print(f" [✓] Música {musica_id} adicionada à playlist '{playlist_name}' do usuário {user_id}.")
                        print(f"     Conteúdo da playlist: {playlist['musicas']}")
                        return
            
            print(f" [!] Erro: Playlist '{playlist_name}' não encontrada para o usuário {user_id}.")
            
        else:
            print(f" [!] Ação assíncrona desconhecida: {acao}")
            
    except Exception as e:
        print(f" [!] Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    broker = None
    try:
        broker = MessageBroker()
        broker.consume_async(
            exchange_name='music_events', 
            routing_key='playlist.*', 
            callback=handle_async_message
        )
    except KeyboardInterrupt:
        print('Interrompido')
    finally:
        if broker:
            broker.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)