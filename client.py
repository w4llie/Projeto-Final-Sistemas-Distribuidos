import sys
import os
import json

# Adiciona o diretório pai ao path para importar gateway
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gateway import Gateway

def menu_principal():
    """Exibe o menu principal e retorna a escolha do usuário."""
    print("\n--- Cliente de Streaming de Música ---")
    print("Escolha o serviço que deseja interagir:")
    print("1. Catálogo Musical (RPC - Síncrono)")
    print("2. Playlists (Assíncrono)")
    print("3. Histórico de Reprodução (Assíncrono)")
    print("0. Sair")
    
    escolha = input("Opção: ")
    return escolha

def menu_catalogo(gateway):
    """Menu para interagir com o serviço de Catálogo."""
    print("\n--- Catálogo Musical (RPC) ---")
    print("1. Listar Catálogo Completo")
    print("2. Buscar Música por ID")
    print("0. Voltar")
    
    escolha = input("Opção: ")
    
    if escolha == '1':
        request = {"servico": "catalogo", "acao": "listar_catalogo"}
        response = gateway.process_request(request)
        print("\n[RESPOSTA DO GATEWAY]")
        if response.get("status") == "sucesso":
            print(json.dumps(response.get("catalogo"), indent=4, ensure_ascii=False))
        else:
            print(f"Erro: {response.get('mensagem')}")
            
    elif escolha == '2':
        musica_id = input("Digite o ID da música (1 a 5): ")
        request = {"servico": "catalogo", "acao": "buscar_musica", "id": musica_id}
        response = gateway.process_request(request)
        print("\n[RESPOSTA DO GATEWAY]")
        if response.get("status") == "sucesso":
            print(json.dumps(response.get("musica"), indent=4, ensure_ascii=False))
        else:
            print(f"Erro: {response.get('mensagem')}")
            
    elif escolha == '0':
        return
    else:
        print("Opção inválida.")

def menu_playlist(gateway):
    """Menu para interagir com o serviço de Playlists."""
    print("\n--- Playlists (Assíncrono) ---")
    print("1. Criar Nova Playlist")
    print("2. Adicionar Música à Playlist")
    print("0. Voltar")
    
    escolha = input("Opção: ")
    
    if escolha == '1':
        user_id = input("Digite seu ID de usuário (ex: user1): ")
        playlist_name = input("Digite o nome da nova playlist: ")
        request = {
            "servico": "playlist", 
            "acao": "criar_playlist", 
            "user_id": user_id, 
            "nome": playlist_name
        }
        response = gateway.process_request(request)
        print("\n[RESPOSTA DO GATEWAY]")
        print(f"Status: {response.get('status')}. Mensagem: {response.get('mensagem')}")
        
    elif escolha == '2':
        user_id = input("Digite seu ID de usuário (ex: user1): ")
        playlist_name = input("Digite o nome da playlist: ")
        musica_id = input("Digite o ID da música a adicionar (1 a 5): ")
        request = {
            "servico": "playlist", 
            "acao": "adicionar_musica", 
            "user_id": user_id, 
            "playlist": playlist_name,
            "musica_id": musica_id
        }
        response = gateway.process_request(request)
        print("\n[RESPOSTA DO GATEWAY]")
        print(f"Status: {response.get('status')}. Mensagem: {response.get('mensagem')}")
        
    elif escolha == '0':
        return
    else:
        print("Opção inválida.")

def menu_historico(gateway):
    """Menu para interagir com o serviço de Histórico."""
    print("\n--- Histórico de Reprodução (Assíncrono) ---")
    print("1. Simular Reprodução de Música")
    print("0. Voltar")
    
    escolha = input("Opção: ")
    
    if escolha == '1':
        user_id = input("Digite seu ID de usuário (ex: user1): ")
        musica_id = input("Digite o ID da música reproduzida (1 a 5): ")
        request = {
            "servico": "historico", 
            "acao": "reproduzir_musica", 
            "user_id": user_id, 
            "musica_id": musica_id
        }
        response = gateway.process_request(request)
        print("\n[RESPOSTA DO GATEWAY]")
        print(f"Status: {response.get('status')}. Mensagem: {response.get('mensagem')}")
        
    elif escolha == '0':
        return
    else:
        print("Opção inválida.")

def main():
    gateway = Gateway()
    
    while True:
        escolha = menu_principal()
        
        if escolha == '1':
            menu_catalogo(gateway)
        elif escolha == '2':
            menu_playlist(gateway)
        elif escolha == '3':
            menu_historico(gateway)
        elif escolha == '0':
            print("Saindo do cliente...")
            break
        else:
            print("Opção inválida. Tente novamente.")
            
    gateway.close()

if __name__ == "__main__":
    main()