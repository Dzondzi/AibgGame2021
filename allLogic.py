from copy import deepcopy
import random
import math
import time


directions = ["ne", "nw", "w", "e", "se", "sw"]
directionsMap = {
    "ne" : {"q" : 1, "r" : -1, "s": 0},
    "nw" : {"q" : 0, "r" : -1, "s": 1},
    "w" : {"q" : -1, "r" : 0, "s": 1},
    "e" : {"q" : 1, "r" : 0, "s": -1},
    "se" : {"q" : 0, "r" : 1, "s": -1},
    "sw" : {"q" : -1, "r" : 1, "s": 0},
}

def suprotanOd(polje:dict):
    polje2 = deepcopy(polje)
    polje2["q"] = -1 * polje["q"]
    polje2["r"] = -1 * polje["r"]
    polje2["s"] = -1 * polje["s"]
    return polje2


def pozicije_ogledalo(polje : dict):

    polje2 = deepcopy(polje)
    polje2["q"] = -1 * polje["q"]
    polje2["r"] = -1 * polje["r"]
    polje2["s"] = -1 * polje["s"]
    polje3 = deepcopy(polje)
    polje3["q"] = polje["s"]
    polje3["s"] = polje["q"]
    polje3["r"] = polje["r"]
    polje4 = deepcopy(polje3)
    polje4["q"] = -1 * polje3["q"]
    polje4["r"] = -1 * polje3["r"]
    polje4["s"] = -1 * polje3["s"]
    return [polje,polje2,polje3,polje4]

def sifrujPolje(polje:dict):
    return f"{polje['q']}_{polje['r']}_{polje['s']}"

def sifruj3(a,b,c):
    return f"{a}_{b}_{c}"

def jeUListi(lista, el):
    for e in lista:
        if e == el:
            return True
    return False
    


class Opponent:
    
    def __init__(self):
        self.id = -1
        self.polje = None
        self.last_seen = 10000
        self.umro = False
    
    def seen(self, polje):
        self.id = polje["id"]
        self.polje = polje
        self.last_seen = -1
    
    def nisi_video(self):
        self.last_seen += 1

    def get_polje(self):
        return self.polje
    
    def get_id(self):
        return self.id

    def last_seen(self):
        return self.last_seen

    def unistio(self):
        self.umro = True
        

class Stanje:

    def __init__(self):
        self.island_flegovi = []
        self.brojac = 0
        self.island_prodavnice = []
        self.vrtlog_flegovi = set()
        self.curr_flag = None
        self.id = None
        self.island_illegal = set()
        self.curr_player = None
        self.protivnici = [Opponent() for i in range(4)]
        self.npc1 = Opponent()
        self.npc2 = Opponent()

    def set_flag(self, flag):
        self.curr_flag = flag
        for el in pozicije_ogledalo(flag):
            if not jeUListi(self.island_flegovi, el):
                self.island_flegovi.append(el)
        
    def set_id(self,id):
        self.id = id

    def set_player(self,player):
        self.curr_player = player

    def dodaj_znacajne(self,res):
        for red in res["map"]["tiles"]:
            for polje in red:
                if len(polje) > 0 and polje["entity"] is not None and polje["entity"]["type"] == "WHIRLPOOL":
                    self.vrtlog_flegovi.add(sifrujPolje(polje)) 
                elif len(polje) > 0 and polje["tileType"] == "ISLAND":
                    self.island_illegal.add(sifrujPolje(polje))
                    if(polje["entity"]["type"] == "ISLANDFLAG"):
                        for el in pozicije_ogledalo(polje):
                            if not jeUListi(self.island_flegovi, el):
                                self.island_flegovi.append(el)
                    else:
                        for el in pozicije_ogledalo(polje):
                            if not jeUListi(self.island_prodavnice, el):
                                self.island_prodavnice.append(el)
                    

    def proveri_protivnike(self,res):
        for i in range(1,5):
            if(len(res[f'player{i}']) > 0):
                if(res[f'player{i}']["id"] == self.id):
                    continue
                for x in self.protivnici:
                    if x.get_id() == -1:
                        x.seen(res[f'player{i}'])
                        break
                    elif x.get_id() == res[f'player{i}']["id"]:
                        x.seen(res[f'player{i}'])
                        break


        for opp in self.protivnici:
            opp.nisi_video()
        
                
    def proveri_npc(self,res):
        if(len(res[f'npc1']) > 0):
            self.npc1.seen(res[f'npc1'])
        if(len(res[f'npc2']) > 0):
            self.npc2.seen(res[f'npc2'])
    
        self.npc1.nisi_video()
        self.npc2.nisi_video()

    def bezi(self,polje2:dict):
    
        najbolji=''
        najbolji_rez=-100
        for i in range(6):
        
            pomocno=deepcopy(self.curr_player)
        
            pomocno["q"]=pomocno["q"]+directionsMap[directions[i]]["q"]
            pomocno["s"]=pomocno["s"]+directionsMap[directions[i]]["s"]
            pomocno["r"]=pomocno["r"]+directionsMap[directions[i]]["r"]
        
            sifra=sifrujPolje(pomocno)
            if sifra not in self.island_illegal and sifra not in self.vrtlog_flegovi:
                trenutni=udaljenostPolja(pomocno,polje2)
                if trenutni>najbolji_rez:
                    najbolji_rez=trenutni
                    najbolji=directions[i]

        return najbolji

    def pridji(self,polje2:dict):
    
        najbolji=None
        najbolji_rez=500
        for i in range(6):
        
            pomocno=deepcopy(self.curr_player)
        
            pomocno["q"]=pomocno["q"]+directionsMap[directions[i]]["q"]
            pomocno["s"]=pomocno["s"]+directionsMap[directions[i]]["s"]
            pomocno["r"]=pomocno["r"]+directionsMap[directions[i]]["r"]
            
            sifra=sifrujPolje(pomocno)
            if sifra not in self.island_illegal and sifra not in self.vrtlog_flegovi:
                trenutni=udaljenostPolja(pomocno,polje2)

                if trenutni<najbolji_rez:
                    najbolji_rez=trenutni
                    najbolji=directions[i]
            
        return najbolji


    def bezi_od_najjaceg(self,pretnje):
        najjaci=None
        jacina=-1
        for x in pretnje:
            if x.polje["cannons"]+x.polje["health"]>jacina:
                jacina=x.polje["cannons"]+x.polje["health"]
                najjaci=x
        return self.bezi(najjaci)


    def isLegalMove(self, direction : dict):
        #granice mape
        if abs(self.curr_player["q"] + direction["q"]) > 14:
            return False 
        if abs(self.curr_player["r"] + direction["r"]) > 14:
            return False
        if abs(self.curr_player["s"] + direction["s"]) > 14:
            return False
        
        # island
        q = self.curr_player["q"] + direction["q"]
        r = self.curr_player["r"] + direction["r"]
        s = self.curr_player["s"] + direction["s"]
        sifra = sifruj3(q,r,s)
        
        if sifra in self.island_flegovi:
            return False
        if sifra in self.vrtlog_flegovi:
            return False
        
        return True
        
    def getLegalMoves(self):
        lista = []
        for direction in directions:
            if self.isLegalMove(directionsMap[direction]):
                lista.append(direction)
        
        return lista


    def get_next_move_random(self):
        return 2, random.choice(self.getLegalMoves())

    def udaljenostPolja(polje1, polje2):
        return max(abs(polje1["q"] - polje2["q"]), abs(polje1["r"] - polje2["r"]), abs(polje1["s"] - polje2["s"]))


    def jaciSam(self, protivnik : Opponent):
        x = self.curr_player["health"] / protivnik.polje["cannons"]
        y = protivnik.polje["health"] / self.curr_player["cannons"]
        x = math.ceil(x)
        y = math.ceil(y)
        return x > y


    def f_zelja_napad(self):
        zelja = 0
        for x in self.protivnici:
            if x.last_seen > 5000:
                continue
            if (x.last_seen <= 0 and x.polje["health"] > 0):
                print("JURIMO")
                print(x.polje["id"])
                if (self.jaciSam(x)):
                    print("NAPADAMO")
                    print(x.polje["id"])
                    return 99.5
        
        if (self.npc1.polje is not None and self.npc1.last_seen <= 0 and self.jaciSam(self.npc1)):
            if (self.npc1.polje["health"] > 0):
                return 94

        if (self.npc2.polje is not None and self.npc2.last_seen <= 0 and self.jaciSam(self.npc2)):
            if (self.npc2.polje["health"] > 0):
                return 94

        return 0

        
    def f_zelja_heal(self):
        zelja = 0
        if self.curr_player["maxHealth"] == 1000:
            zelja += 100
        else:
            return 0
        if self.curr_player["health"] == self.curr_player["maxHealth"]:
            return 0

        if self.curr_player["potNums"] == 0:
            return 0

        if 100 < self.curr_player["health"] <= 900:
            zelja = self.curr_player["health"]*(-14/900) + 94
        elif self.curr_player["health"] < 100:
            zelja = 94.5
        else:
            zelja = 75
        return zelja
        

    def f_zelja_istrazi(self):
        zelja = 100

        zelja *= ((udaljenostPolja(self.curr_flag, self.curr_player)) ** 2) / 150 
        return min(20, zelja)

    def f_zelja_bezi(self):
        zelja = 0

        for x in self.protivnici:
            if (x.last_seen <= 0):
                if not (self.jaciSam(x)):
                    return x.polje, 99.6
        
        if (self.npc1.last_seen <= 0 and not self.jaciSam(self.npc1)):
            return self.npc1.polje, 99.55

        if (self.npc2.last_seen <= 0 and not self.jaciSam(self.npc2)):
            return self.npc2.polje, 99.55

        return None, 0

    def f_zelja_unapredi_top(self):
        if (self.curr_player["money"] < 200):
            return 0
        elif (self.curr_player["money"] < 300 and self.curr_player["cannons"] == 150):
            return 0

        if (self.curr_player["cannons"] == 250):
            return 0

        zelja = 0
        #pare, prodavnica **protivnik
        mani = min(1000, self.curr_player["money"])
        zelja += (mani - 250)/750 * 30 + 40 
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is not None:
            udaljenost = udaljenostPolja(self.curr_player, najblizaProdavnica)
            zelja+=30/udaljenost

        return min(95, zelja)

        
    def f_zelja_unapredi_helt(self):
        if (self.curr_player["money"] < 300):
            return 0

        if (self.curr_player["maxHealth"] == 1000):
            return 0

        zelja = 0
        #pare, prodavnica **protivnik
        mani = min(1000, self.curr_player["money"])
        zelja += (mani - 250)/750 * 30 + 41 
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is not None:
            udaljenost = udaljenostPolja(self.curr_player, najblizaProdavnica)
            zelja+=30/udaljenost
        return min(95.5, zelja)

    #potion
    def f_zelja_kupi_hil(self):
        if self.curr_player["money"] < 150:
            return 0
        if self.curr_player["maxHealth"] != 1000:
            return 0
        if self.curr_player["potNums"] == 2:
            return 0
        if self.curr_player["cannons"] != 250:
            return 0
        
        zelja = 20
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is not None:
            udaljenost = udaljenostPolja(self.curr_player, najblizaProdavnica)
            zelja += 51/udaljenost
        if self.curr_player["money"] > 300:
            zelja += 21
            
        zelja *= (100/self.curr_player["health"])**2
        if self.curr_player["potNums"] == 0:
            zelja =(zelja + 100)/2
        return zelja

    def f_zelja_zastavica(self):
        zelja = 100 - ((udaljenostPolja(self.curr_flag, self.curr_player)) ** 1.5) 
        return min(98, zelja)
        
    def heuristika4(self):
        zelja_napad = self.f_zelja_napad()
        zelja_heal = self.f_zelja_heal()
        zelja_istrazi = self.f_zelja_istrazi()
        bezim_od, zelja_bezi = self.f_zelja_bezi()
        zelja_kupi_hil = self.f_zelja_kupi_hil()
        zelja_unapredi_top = self.f_zelja_unapredi_top()
        zelja_unapredi_helt = self.f_zelja_unapredi_helt()
        zelja_zastavica = self.f_zelja_zastavica()

        zelja = max(zelja_napad,zelja_kupi_hil, zelja_heal, zelja_istrazi, zelja_bezi, zelja_unapredi_top, zelja_unapredi_helt, zelja_zastavica)

        if zelja == zelja_napad:
            print("ZELJA NAPADNI")
            id, koga_napada = self.napadni()
            return id, koga_napada
        elif zelja == zelja_heal:
            print("ZELJA HEL")
            return 6, -1
        elif zelja == zelja_istrazi:
            print("ZELJA ISTRAZI")
            if(31 >= self.brojac > 15):
                self.brojac %= 30
                self.brojac += 1
                return self.zastavica()
            return self.istrazi()
        elif zelja == zelja_kupi_hil:
            print("ZELJA KUPI HIL")
            id, potez = self.kupi_hil()
            return id, potez
        elif zelja == zelja_bezi:
            print("ZELJA BJEZI")
            return 2, self.bezi(bezim_od)
        elif zelja == zelja_unapredi_top:
            print("ZELJA TOP")
            id, potez = self.unapredi_top()
            return id, potez
        elif zelja == zelja_unapredi_helt:
            print("ZELJA HELTUJ")
            id, potez = self.unapredi_helt()
            return id, potez
        elif zelja == zelja_zastavica:
            print("ZELJA ZASTAVICA")
            return self.zastavica()
        
    def napadni(self):
        for protivnik in self.protivnici:
            if protivnik.last_seen <= 0:
                if udaljenostPolja(protivnik.polje, self.curr_player) <= 2:
                    return 1, protivnik.id
                else:
                    return 2, self.pridji(protivnik.polje)
        if self.npc1.last_seen <= 0:
            if udaljenostPolja(self.npc1.polje, self.curr_player) <= 2:
                return 1, self.npc1.id
            else:
                return 2, self.pridji(self.npc1.polje)
        if self.npc2.last_seen <= 0:
            if udaljenostPolja(self.npc2.polje, self.curr_player) <= 2:
                return 1, self.npc2.id
            else:
                return 2, self.pridji(self.npc2.polje)

    def zastavica(self):
        return 2, self.pridji(self.curr_flag)


    def istrazi(self):
        return 2, self.pridji(suprotanOd(self.curr_flag))
        return self.get_next_move_random()


    def poredProdavnice(self):
        for prodavnica in self.island_prodavnice:
            # print(str(prodavnica))
            if udaljenostPolja(self.curr_player, prodavnica) == 1:
                return True
        return False

    def nadjiNajblizuProdavnicu(self):
        najmanje = 28
        ciljana = None
        for prodavnica in self.island_prodavnice:
            udaljenost = udaljenostPolja(self.curr_player, prodavnica)
            if udaljenost < najmanje:
                najmanje = udaljenost
                ciljana = prodavnica 
        return ciljana

    def kupi_hil(self):
        if self.poredProdavnice():
            return 3,-1
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is None:
            return self.get_next_move_random()
        potez = self.pridji(najblizaProdavnica)
        return 2, potez

    def unapredi_top(self):
        if self.poredProdavnice():
            return 5,-1
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is None:
            return self.get_next_move_random()
        potez = self.pridji(najblizaProdavnica)
        return 2, potez

    def unapredi_helt(self):
        if self.poredProdavnice():
            return 4,-1
        najblizaProdavnica = self.nadjiNajblizuProdavnicu()
        if najblizaProdavnica is None:
            return self.get_next_move_random()
        potez = self.pridji(najblizaProdavnica)
        return 2, potez


    
            
