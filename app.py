import streamlit as st
import requests
import os

# Lê a chave da Riot a partir das variáveis de ambiente (configurada no Streamlit Secrets)
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# Endpoints corretos para cada tipo de dado
PLATFORM_ROUTING = "https://br1.api.riotgames.com"  # Para dados de invocador
MATCH_ROUTING = "https://americas.api.riotgames.com"  # Para partidas e PUUIDs

# Cabeçalho com a chave
HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

# Função para buscar o PUUID do jogador pelo nome de invocador
def get_puuid_by_riot_id(game_name):
    # Remover a tag # e manter apenas o nome de invocador
    game_name = game_name.replace('#', '')
    
    url = f"{PLATFORM_ROUTING}/lol/summoner/v5/summoners/by-name/{game_name}"

    try:
        response = requests.get(url, headers=HEADERS)
        
        # Exibe a resposta completa da API para depuração
        st.write("Resposta da API:", response.text)

        if response.status_code != 200:
            st.error(f"Erro ao buscar PUUID: {response.status_code}")
            return None
        
        # Se a resposta estiver OK, convertendo para JSON
        summoner_data = response.json()

        if not summoner_data:
            st.error("Resposta vazia recebida da API.")
            return None
        
        return summoner_data["puuid"]
    
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao fazer requisição: {e}")
        return None
    except ValueError as e:
        st.error(f"Erro ao processar a resposta JSON: {e}")
        st.error(f"Conteúdo da resposta: {response.text}")
        return None

# Função para buscar as partidas com base no PUUID
def get_match_ids_by_puuid(puuid, count=10):
    url = f"{MATCH_ROUTING}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        # Exibe a resposta completa da API para depuração
        st.write("Resposta da API:", response.text)

        if response.status_code != 200:
            st.error(f"Erro ao buscar partidas: {response.status_code}")
            return []
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao fazer a requisição: {e}")
        return []

# Função para buscar os detalhes de uma partida
def get_match_detail(match_id):
    url = f"{MATCH_ROUTING}/lol/match/v5/matches/{match_id}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        # Exibe a resposta completa da API para depuração
        st.write("Resposta da API:", response.text)

        if response.status_code != 200:
            st.error(f"Erro ao buscar detalhes da partida: {response.status_code}")
            return {}
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao fazer a requisição: {e}")
        return {}

# Função para exibir as partidas personalizadas
def display_custom_matches(puuid):
    match_ids = get_match_ids_by_puuid(puuid)
    if not match_ids:
        st.error("Nenhuma partida encontrada.")
        return
    
    st.write(f"**Partidas para PUUID: {puuid}**")
    
    for match_id in match_ids:
        match = get_match_detail(match_id)
        if match and match.get("info", {}).get("gameMode") == "CUSTOM":
            st.write(f"Match ID: {match_id}")
            st.json(match)  # Exibe detalhes da partida como JSON

# Interface do Streamlit
st.title("Riot Games - Custom Matches Viewer")

# Input do nome de invocador
game_name = st.text_input("Digite o nome do invocador:")

if game_name:
    st.write(f"Buscando partidas para: {game_name}")
    puuid = get_puuid_by_riot_id(game_name)
    
    if puuid:
        display_custom_matches(puuid)
