import sys
import os
import json
from datetime import datetime

# Adiciona o diretório pai ao path para importar messaging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging import MessageBroker

# Simulação de um banco de dados de histórico de reprodução
HISTORICO_REPRODUCAO = {}

def handle_async_message(ch, method, properties, body):
    """
    Função que processa as mensagens assíncronas para o serviço de histórico.
    """
    try:
        message = json.loads(body.decode('utf-8'))
        acao = message.get("acao")
        
        if acao == "reproduzir_musica":
            user_id = message.get("user_id")
            musica_id = message.get("musica_id")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if user_id not in HISTORICO_REPRODUCAO:
                HISTORICO_REPRODUCAO[user_id] = []
            
            HISTORICO_REPRODUCAO[user_id].append({
                "musica_id": musica_id, 
                "timestamp": timestamp
            })
            
            print(f" [✓] Usuário {user_id} reproduziu a música {musica_id} em {timestamp}.")
            print(f"     Histórico atual do usuário: {HISTORICO_REPRODUCAO.get(user_id)}")
            
        else:
            print(f" [!] Ação assíncrona desconhecida: {acao}")
            
    except Exception as e:
        print(f" [!] Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    broker = None
    try:
        broker = MessageBroker()
        # O serviço de histórico escuta em uma fila ligada ao 'music_events' exchange com a chave 'reproducao.*'
        broker.consume_async(
            exchange_name='music_events', 
            routing_key='reproducao.*', 
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