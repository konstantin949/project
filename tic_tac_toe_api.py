import time

import requests
import json
from settings import URL


def connect_second_player(game_id):
    resp = requests.post(f'{URL}api/connect_second_player', data={'game_id': game_id})
    return json.loads(resp.text)['player_key']


def create_game(n, d):
    resp = requests.post(f'{URL}api/create_game', data={'size_of_board': n, 'length_of_win_comb': d})
    data = json.loads(resp.text)
    game_id = data['game_id']
    player_key = data['player_key']
    return game_id, player_key


def make_move(game_id, player_key, board):
    resp = requests.post(f'{URL}api/make_move',
                         data={'game_id': game_id, 'player_key': player_key, 'board': board})
    return resp.text


def waiting_move(game_id, player_key):
    resp = None
    for i in range(100):
        try:
            resp = requests.post(f'{URL}api/can_i_move',
                                 data={'game_id': game_id, 'player_key': player_key})
            break
        except requests.exceptions.ReadTimeout:
            pass

    data = json.loads(resp.text)
    board = data.get('board')
    winner = data.get('winner')

    if board and winner:
        return board, winner


def connected_second_player(game_id, player_key):
    resp = None
    time.sleep(1)
    for i in range(100):
        try:
            resp = requests.post(f'{URL}api/connected_second_player',
                                 data={'game_id': game_id, 'player_key': player_key})
            break
        except requests.exceptions.ReadTimeout:
            pass

    if resp is not None and resp.text == 'connected':
        return True
    else:
        return False


def get_list_of_games():
    resp = requests.get(f'{URL}api/get_list_of_games')
    list_of_games = json.loads(resp.text)
    return list_of_games



