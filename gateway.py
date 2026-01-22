import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messaging import RpcClient, MessageBroker

class Gateway:
    """
    Middleware responsável por receber as requisições do cliente e encaminhá-las
    aos serviços distribuídos apropriados.
    """
    def __init__(self):
        self.rpc_client = RpcClient()
        self.broker = MessageBroker()

    def process_request(self, request):
       
        service = request.get("servico")
        acao = request.get("acao")
        
        print(f"\n[GATEWAY] Recebida requisição para Serviço: {service}, Ação: {acao}")

        if service == "catalogo":
            if acao == "buscar_musica" or acao == "listar_catalogo":
                response = self.rpc_client.call("catalogo_rpc_queue", request)
                return response
            else:
                return {"status": "erro", "mensagem": f"Ação RPC desconhecida para Catálogo: {acao}"}

        elif service == "playlist":
            if acao == "criar_playlist":
                self.broker.publish_async('music_events', 'playlist.criar', request)
                return {"status": "sucesso", "mensagem": f"Requisição de criação de playlist enviada para processamento assíncrono."}
            elif acao == "adicionar_musica":
                self.broker.publish_async('music_events', 'playlist.adicionar', request)
                return {"status": "sucesso", "mensagem": f"Requisição de adição de música enviada para processamento assíncrono."}
            else:
                return {"status": "erro", "mensagem": f"Ação assíncrona desconhecida para Playlist: {acao}"}

        elif service == "historico":
            if acao == "reproduzir_musica":
                self.broker.publish_async('music_events', 'reproducao.nova', request)
                return {"status": "sucesso", "mensagem": f"Evento de reprodução enviado para processamento assíncrono."}
            else:
                return {"status": "erro", "mensagem": f"Ação assíncrona desconhecida para Histórico: {acao}"}

        else:
            return {"status": "erro", "mensagem": f"Serviço desconhecido: {service}"}

    def close(self):
        """Fecha as conexões."""
        self.rpc_client.close()
        self.broker.close()

if __name__ == "__main__":
    print("O Gateway é uma classe utilitária neste exemplo e não um processo autônomo.")
    print("Ele será instanciado pelo client.py.")