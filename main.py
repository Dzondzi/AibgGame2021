import json
from allLogic import *
import requests
import time


# Four=XX&mapName=mapa1

# http://best2.aibg.best:9080/admin/createGame?gameId=81&playerOne=1&playerTwo=2&playerThree=3&playerFour=4&mapName=mapa1

SERVER_IP = "best2.aibg.best:9080"
MY_ID = 1
GAME_ID = 88

POSITION = 1

NAPADAJ = 1
HODAJ = 2
KUPUJ_POTION = 3
KUPUJ_HULL = 4
KUPUJ_CANNONS = 5
HEAL = 6

def nadji_id(res):
    for i in range (1,5):
        if len(res[f'player{i}'])>0:
            return res[f'player{i}']["id"]

# x = requests.get(f'http://{SERVER_IP}/train?gameId={GAME_ID}&playerId={MY_ID}&position={POSITION}')
# res = x.json()


x = requests.get(f'http://{SERVER_IP}/game/play?playerId={MY_ID}&gameId={GAME_ID}')
res = x.json()

if res["success"] == False:
    print("GRESKA")
    exit()

id3 = nadji_id(res)

stanje = Stanje()
stanje.set_flag(res["currFlag"])
stanje.set_player(res[f"player{id3}"])
stanje.set_id(stanje.curr_player["id"])

stanje.dodaj_znacajne(res)

last_flag = sifrujPolje(res["currFlag"])

while(True):

    id_poteza, potez = stanje.heuristika4()
    
    if id_poteza == NAPADAJ:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action=atk-{potez}')).json()
    elif id_poteza == HODAJ:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action={potez}')).json()
    elif id_poteza == KUPUJ_POTION:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action=buy-POTION')).json()
    elif id_poteza == KUPUJ_HULL:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action=buy-HULL')).json()
    elif id_poteza == KUPUJ_CANNONS:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action=buy-CANNONS')).json()
    elif id_poteza == HEAL:
        res = (requests.get(f'http://{SERVER_IP}/doAction?playerId={MY_ID}&gameId={GAME_ID}&action=up')).json()
    else:
        print("NEKA GRESKA")

    #####
    if res["success"] == False:
        continue
    if res["winner"] is not None:
        print("Kraj partije")
        break
    #####
    trenutni_flag = sifrujPolje(res["currFlag"])
    if trenutni_flag != last_flag:
        last_flag = trenutni_flag
        stanje.set_flag(res["currFlag"])
    
    stanje.dodaj_znacajne(res)
    stanje.set_player(res[f"player{id3}"])
    stanje.proveri_protivnike(res)
    stanje.proveri_npc(res)
    

    
