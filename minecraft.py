import pygame
from time import sleep
from random import *
import math
import zlib
import base64
from dataclasses import dataclass
from typing import List, Dict
import json
import inspect
import os

# Initialisation de Pygame
pygame.init()

# Définition des constantes
LARGEUR_ECRAN = 1200
HAUTEUR_ECRAN = 600
LARGEUR_MAP, HAUTEUR_MAP = 10, 10
TAILLE_PIXEL = 50



class Entity:
    def __init__(self, species: str, id: int, coords: Dict[str, int], hearts: int, strength_attack: int, loot: List[str], hostility: bool, xp: int, speed: float):
        self.species = species
        self.id = id
        self.coords = coords
        self.hearts = hearts
        self.strength_attack = strength_attack
        self.loot = loot
        self.hostility = hostility
        self.xp = xp
        self.speed = speed
    

@dataclass
class Item:
    x: float
    y: float
    name: str


class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.xp = 0
        self.inventaire = ['inventaire_vide'] * 38 + ['bois'] *2
        self.effects_potions = {'poison': {'durée': 0.0}, 'fatigue': {'durée': 0.0}}
        self.life = 20
        self.bouffe = 20
        self.vitesse = TAILLE_PIXEL

    def move(self, direction):
        if not direction in ["droite", "gauche", "bas", "haut"]:
            raise ValueError(f"direction invalide ({direction}) dans Player.move")
        if direction == "droite":
            self.x += 1
        if direction == "gauche":
            self.x -= 1
        if direction == "bas":
            self.y += 1
        if direction == "haut":
            self.y -= 1
    
    def apply_effects(self):
        if self.effects_potions['poison']['durée'] > 0:
            self.life -= 1
            self.effects_potions['poison']['durée'] -= 0.1
        if self.effects_potions['fatigue']['durée'] > 0:
            self.vitesse = TAILLE_PIXEL // 2
            self.effects_potions['fatigue']['durée'] -= 0.1
    
    def is_dead(self):
        return self.life <= 0

class GameMap:
    def __init__(self):
        self.world = []

    def generate(self):
        # Initialisation de la carte avec des 'air'
        self.world = [['air' for _ in range(LARGEUR_MAP)] for __ in range(HAUTEUR_MAP)]
        # Ajout des bordures
        for i in range(HAUTEUR_MAP):
            self.world[i][0] = 'bordure'
            self.world[i][-1] = 'bordure'
            self.world[0][i] = 'bordure'
            self.world[-1][i] = 'bordure'
        # Stuff de base
        self.world[1][1:4] = ['coffre', 'etabli', 'furnace']
        # Arbre
        def arbre(x, y):
            self.world[y+1][x] = 'bois'
            self.world[y][x] = 'bois'
            self.world[y-1][x] = 'bois'
            self.world[y-2][x] = 'bois'
            self.world[y-2][x-1] = 'leaves'
            self.world[y-2][x] = 'leaves'
            self.world[y-2][x+1] = 'leaves'
            self.world[y-3][x] = 'leaves'
        arbre(6, 5)

    # Permet d'accéder à la carte comme à une liste : game_map[y][x]
    def __getitem__(self, idx):
        return self.world[idx]
    
    def Afficher(self, decalage_x: float, decalage_y: float) -> None:
        for y in range(HAUTEUR_MAP):
            for x in range(LARGEUR_MAP):
                bloc_x = x * TAILLE_PIXEL - int(decalage_x) + (LARGEUR_ECRAN // 2)
                bloc_y = y * TAILLE_PIXEL - int(decalage_y) + (HAUTEUR_ECRAN // 2)
                if -TAILLE_PIXEL <= bloc_x < LARGEUR_ECRAN and -TAILLE_PIXEL <= bloc_y < HAUTEUR_ECRAN:
                    ecran.blit(image(self.world[y][x]), (bloc_x, bloc_y))

        
player = Player()

# Création des entités à partir des espèces par défaut
mobs = [
    Entity(species="zombie", id=0, coords={"x": 0, "y": 0}, hearts=10, strength_attack=1, loot=["rotten_flesh"], hostility=True, xp=10, speed=TAILLE_PIXEL),
]





CONSTANTES = {
    'max_life_en_demis_coeurs': 20,
    'max_bouffe_en_demis_bouffe': 20,
    'solides': ["bordure"],
    'nombre_lignes_inventaire': 3,
    'nombre_cases_hotbar': 10,
    'nombre_cases_inventaire': 27
}

def compresser(texte: str) -> str:
    # Compresser le texte en utilisant zlib
    donnees_compressees = zlib.compress(texte.encode('utf-8'))
    # Encoder les données compressées en Base64 pour garantir des caractères imprimables
    donnees_base64 = base64.b64encode(donnees_compressees)
    # Convertir les données encodées en une chaîne de caractères
    return donnees_base64.decode('utf-8')

def decompresser(texte_compresse: str) -> str:
    # Décoder le texte compressé de Base64
    donnees_base64 = base64.b64decode(texte_compresse.encode('utf-8'))
    # Décompresser les données en utilisant zlib
    donnees_decompressees = zlib.decompress(donnees_base64)
    # Convertir les données décompressées en une chaîne de caractères
    return donnees_decompressees.decode('utf-8')

mangeable = {
    'pork': [5.0, 0],
    'cooked_pork': [10.0, 0],
    'mouton_cru': [5.0, 0],
    'cooked_mouton': [10.0, 0],
    'rotten_flesh': [5.0, 2]
}

drops = []
modify_bloc_to_item = {
    'verre2': 'inventaire_vide',
    'verre1': 'verre2'
}
case_inventaire = 1


def modify_pos_mob(mobs: list, x: float, y: float, TAILLE_PIXEL: int, tick: int) -> list:
    for mob in mobs:
        SPEED = mob.speed  # Utilisation de la vitesse de l'instance du mob
        
        # Convertir les coordonnées du joueur en unités de la grille
        player_x, player_y = x, y
        
            
        # Calculer la direction vers le joueur
        dx = player_x - mob.coords['x']
        dy = player_y - mob.coords['y']
        
        centre_x = mob.coords['x'] + (TAILLE_PIXEL / 2)
        centre_y = mob.coords['y'] + (TAILLE_PIXEL / 2)
        
        # Déplacement horizontal
        if dx > 0 or not bloc_pos(centre_x + SPEED, centre_y) in CONSTANTES["solides"]:
            mob.coords['x'] += SPEED
        elif dx < 0 or not bloc_pos(centre_x - SPEED, centre_y) in CONSTANTES["solides"]:
           mob.coords['x'] -= SPEED
        
        # Déplacement vertical
        if dy > 0 or not bloc_pos(centre_x, centre_y + SPEED) in CONSTANTES["solides"]:
            mob.coords['y'] += SPEED
        elif dy < 0 or not bloc_pos(centre_x, centre_y - SPEED) in CONSTANTES["solides"]:
            mob.coords['y'] -= SPEED

        # Débogage : Afficher les valeurs intermédiaires
        #print(f"Player position: ({x}, {y})")
        #print(f"dx: {dx}, dy: {dy}")
        #print(f"New mob position: ({mob.coords['x']}, {mob.coords['y']})")
        #print(mob)
    return mobs



def craft(valeur_recherchee: list) -> str:
    craft_table = {
        
    }
    try:
        return craft_table[valeur_recherchee]
    except:
        pass
    return 'air'  # Retourne None si aucune correspondance n'est trouvée

def cuire(valeur_recherchee: str) -> str:
    furnace_table = {
        'bois': 'charcoal',
        'pork': 'cooked_pork',
        'mouton_cru': 'cooked_mouton',
        'sable': 'verre1'
    }
    try:
        return furnace_table [valeur_recherchee]
    except:
        pass
    return 'air'  # Retourne None si aucune correspondance n'est trouvée...

game_map = GameMap()
game_map.generate()
print(game_map.world)



# Couleurs
Couleurs = {
    "CIEL_SOIR": (15, 5, 107),
    "CIEL": (0, 191, 255),
    "JOUEUR": (255, 140, 0),
    "INVENTAIRE": (169, 169, 169),
    "INVENTAIRE_VIDE": (169, 169, 169),
    "RED": (255, 0, 0),
    "GREEN": (0, 225, 0),
    "AIR": (0, 150, 0),
    "GRIS_FONCE": (100, 100, 100),
    "GRIS_TRES_FONCE": (50, 50, 50)
}

necessite = {
    'pierre': ['pioche', 'inventaire_vide'],
    'leaves': ['cisailles', 'inventaire_vide']
}

image_cache = {}
def image(texte):
    # Charger l'image
    if texte not in image_cache:
        image_cache[texte] = pygame.image.load(fr"C:\Users\Rectorat\Downloads\minecraft-2d-master\minecraft-2d-master\images\{texte}.jpg")
        image_cache[texte] = pygame.transform.scale(image_cache[texte], (TAILLE_PIXEL, TAILLE_PIXEL))
    # Redimensionner l'image Ã  la taille du bloc
    return image_cache[texte]

# Création de la fenÃªtre
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption("Minecraft 1.0")
clock = pygame.time.Clock()

def verifier_collision(x: float, y: float) -> bool:
    # Convertir les coordonnées en indices de la grille
    grid_x = round(x / TAILLE_PIXEL)
    grid_y = round(y / TAILLE_PIXEL)
    
    # Vérifier si les indices sont dans les limites de la carte
    if 0 <= grid_x < LARGEUR_MAP and 0 <= grid_y < HAUTEUR_MAP:
        return not GameMap.world[grid_y][grid_x] in CONSTANTES["solides"]
    return False #à peut etre corriger?

def bloc_pos(x: float, y: float) -> str:
    grid_x = int(x // TAILLE_PIXEL)
    grid_y = int(y // TAILLE_PIXEL)
    try:
        return game_map[grid_y][grid_x]
    except:
        raise IndexError(f"error: return game_map[{grid_y}][{grid_x}] in bloc_pos()")

def modify(x: float, y: float, bloc: str) -> None:
    # Convertir les coordonnées en indices de la grille
    grid_x = int(x / TAILLE_PIXEL)
    grid_y = int(y / TAILLE_PIXEL)
    game_map[grid_y][grid_x] = bloc

# Fonction pour dessiner la barre de vie
def draw_health_bar(screen, x, y, health, max_health, width, height):
    ratio = health / max_health
    pygame.draw.rect(screen, Couleurs["RED"], (x, y, width, height))
    pygame.draw.rect(screen, Couleurs["GREEN"], (x, y, width * ratio, height))




def dessiner_mobs():
    # Dessin des mobs
    for mob in mobs:
        x_mob = int(mob.coords['x'] - player.x + (LARGEUR_ECRAN // 2))
        y_mob = int(mob.coords['y'] - player.y + (HAUTEUR_ECRAN // 2))
        image_mob = image(mob.species)
        
        ecran.blit(image_mob, (x_mob, y_mob))
        
        # Dessin de la barre de vie
        bar_width = image_mob.get_width()
        bar_height = 10
        bar_x = x_mob
        bar_y = y_mob + image_mob.get_height() - (bar_height//2)
        
        draw_health_bar(ecran, bar_x, bar_y, mob.hearts, (bar_height//2), bar_width, bar_height)
    

def dessiner_drops(drops: list) -> None:
    # Dessin des drops
    for drop in drops:
        x_drop = int(drop.x - decalage_x)
        y_drop = int(drop.y - decalage_y)
        ecran.blit(image(drop.name), (x_drop, y_drop))

def dessiner_hotbar(case_inventaire: list, inventaire: list) -> None:
    largeur_totale = CONSTANTES["nombre_cases_hotbar"] * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2
    
    for i in range(CONSTANTES["nombre_cases_hotbar"]):
        x = position_x_debut + (i * TAILLE_PIXEL)
        y = HAUTEUR_ECRAN - TAILLE_PIXEL
        
        # Dessiner la case de l'inventaire
        pygame.draw.rect(ecran, Couleurs["INVENTAIRE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
        ecran.blit(image(inventaire[i]), (x+2, y+2))
        
        # Dessiner la bordure autour de la case
        pygame.draw.rect(ecran, Couleurs["GRIS_FONCE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
        pygame.draw.rect(ecran, Couleurs["GRIS_TRES_FONCE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)
        
        # Mettre en évidence la case sélectionnée
        if i == case_inventaire - 1:
            pygame.draw.rect(ecran, (255, 255, 255), (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 2)

def dessiner_inventaire(inventaire: list) -> None:
    largeur_totale = (CONSTANTES["nombre_cases_inventaire"] // CONSTANTES["nombre_lignes_inventaire"]) * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2 - (TAILLE_PIXEL //2)
    
    for n in range(CONSTANTES["nombre_lignes_inventaire"]):
        for i in range(CONSTANTES["nombre_cases_hotbar"]):
            x = position_x_debut + (i * TAILLE_PIXEL)
            y = HAUTEUR_ECRAN - (TAILLE_PIXEL * (n + 2.5))
            
            # Dessiner la case de l'inventaire
            pygame.draw.rect(ecran, Couleurs["INVENTAIRE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
            try:
                # Si ce n'est pas possible, afficher l'image de l'objet
                ecran.blit(image(inventaire[n*CONSTANTES["nombre_cases_hotbar"] + i]), (x+2, y+2))
            except IndexError:
                # Case vide, ne rien faire
                pass
            
            # Dessiner la bordure autour de la case
            pygame.draw.rect(ecran, Couleurs["GRIS_TRES_FONCE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
            pygame.draw.rect(ecran, Couleurs["GRIS_FONCE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)

def afficher_xp(xp: int) -> None:
    niveau, xp_actuel = divmod(xp, 10)
    largeur_barre, epaisseur = 273, TAILLE_PIXEL / 4
    x, y = (LARGEUR_ECRAN - largeur_barre) // 2, HAUTEUR_ECRAN - TAILLE_PIXEL * 1.33
    rayon = epaisseur / 2

    # Affichage du niveau
    font = pygame.font.Font(None, 24)
    ecran.blit(font.render(f"{int(niveau)}", True, (80, 255, 80)), 
               (LARGEUR_ECRAN // 2, y - epaisseur - 10))

    # Création et dessin de la barre d'XP
    barre_surface = pygame.Surface((largeur_barre, epaisseur), pygame.SRCALPHA)
    pygame.draw.rect(barre_surface, (0, 0, 0), (0, 0, largeur_barre, epaisseur), border_radius=int(rayon))
    
    for i in range(int(largeur_barre * xp_actuel / 100)):
        if i % 2 == 0:
            pygame.draw.line(barre_surface, (80, 255, 80), (i, 0), (i, epaisseur))

    pygame.draw.rect(barre_surface, (0, 0, 0), (0, 0, largeur_barre, epaisseur), 1, border_radius=int(rayon))
    ecran.blit(barre_surface, (x, y))

def dessiner_coeurs(demis_coeurs: int) -> None:    
    largeur_totale = (CONSTANTES["max_life_en_demis_coeurs"]//2) * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2 - (TAILLE_PIXEL/2)
    y_coeur = HAUTEUR_ECRAN - 2 * TAILLE_PIXEL  # Juste au-dessus de l'inventaire
    
    # Tremblement si peu de vies (moins de 4 demis coeurs)
    if demis_coeurs <= 4:
        y_coeur += randint(-5, 5)
        position_x_debut += randint(-5, 5)
    
    if CONSTANTES["max_life_en_demis_coeurs"] % 2 != 0:
        raise ValueError("nombre de coeurs total doit etre divisible par 2 dans dessiner_coeurs()")
        
    for i in range(CONSTANTES["max_life_en_demis_coeurs"]//2):
        # Calcul de la position en x pour chaque cœur
        x_coeur = position_x_debut + (i * int(TAILLE_PIXEL / 2))
        
        # Détermine quelle image afficher en fonction des vies restantes
        if demis_coeurs >= (i + 1) * 2:  # Si le joueur a un cœur entier à cet emplacement
            image_a_afficher = image('heart')
        elif demis_coeurs == (i * 2) + 1:  # Si le joueur a un demi-cœur à cet emplacement
            image_a_afficher = image('demi_heart')
        else:  # Si le joueur n'a plus de vie à cet emplacement
            image_a_afficher = image('heart_vide')
                
        ecran.blit(pygame.transform.scale(image_a_afficher, (int(TAILLE_PIXEL/2), int(TAILLE_PIXEL/2))), (x_coeur, y_coeur))


def F3_panel():
    vars = ["player.x", "player.y"]
    
    # Calcule la taille dynamique de la police
    font_size = min(HAUTEUR_ECRAN // len(vars), LARGEUR_ECRAN // max(len(var) for var in vars))
    font = pygame.font.Font(None, font_size)
    
    y_offset = 0
    lines = []
    
    for element in vars:
        try:
            lines.append(f"{element}: {eval(element)}")
        except:
            raise NameError(f"Variable '{element}' non définie (tentative d'y acceder depuis F3_panel())")
    
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        ecran.blit(text_surface, (50, y_offset))
        y_offset += font_size


def F4_panel():
    # Capture les variables locales
    vars = globals()
    
    # Paramètre de longueur max par ligne
    MAX_CARACTERES_PAR_LIGNE = 100  # À ajuster selon vos besoins
    
    # Génère les lignes avec découpage automatique dans une compréhension de liste
    raw_lines = [
        f"{key}: {value}"
        for key, value in vars.items()
        if not callable(value) and not key.startswith("__")
    ]
    # Découpe chaque ligne trop longue en plusieurs sous-lignes
    lines = [
        raw_line[i:i+MAX_CARACTERES_PAR_LIGNE]
        for raw_line in raw_lines
        for i in range(0, len(raw_line), MAX_CARACTERES_PAR_LIGNE)
    ]
    
    # Calcul dynamique de la taille de police
    font_size = min(
        HAUTEUR_ECRAN // len(lines),
        LARGEUR_ECRAN // MAX_CARACTERES_PAR_LIGNE
    )
    font = pygame.font.Font(None, font_size)
    
    # Affichage avec gestion multi-lignes
    y_offset = 0
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        ecran.blit(text_surface, (50, y_offset))
        y_offset += font_size



def unit_test_variables_types() -> None:
    type_mapping = {
        "bool": bool,
        "int": int,
        "float": float,
        "str": str,
        "list": list,
        "dict": dict,
        "tuple": tuple,
    }

    dict_type_var = {
        "running": "bool"
    }

    for variable, type_str in dict_type_var.items():
        expected_type = type_mapping.get(type_str)
        if expected_type is None:
            raise TypeError(f"Type '{type_str}' is not recognized dans unit_test_variables_types()")

        var_value = locals().get(variable, globals().get(variable))
        if var_value is None:
            raise ValueError(f"Variable '{variable}' is not defined dans unit_test_variables_types()")

        if type(var_value) != expected_type:
            raise TypeError(f"Erreur du type de {variable} dans unit_test_variables_types() : expected {expected_type.__name__}, got {type(var_value).__name__}")



def track_variables(output_filename="variables.json"):
    """
    Inspecte toutes les variables globales et locales, détecte leur type, leur portée et leur valeur,
    et exporte ces informations dans un fichier JSON situé dans le même répertoire que le script.
    """
    # Obtenir le répertoire du script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_directory, output_filename)

    # Obtenir le cadre actuel (frame) pour inspecter les variables locales
    current_frame = inspect.currentframe()
    outer_frame = current_frame.f_back  # Récupère le cadre appelant

    # Dictionnaire pour stocker les informations des variables
    variables_info = {}

    def safe_serialize(value):
        """
        Tente de sérialiser une valeur pour JSON. Si ce n'est pas possible,
        retourne une représentation sous forme de chaîne.
        """
        try:
            json.dumps(value)  # Test si la valeur est sérialisable
            return value
        except (TypeError, OverflowError):
            return str(value)  # Convertit en chaîne si non sérialisable

    # Inspecter les variables locales
    local_vars = outer_frame.f_locals
    for name, value in local_vars.items():
        variables_info[name] = {
            "scope": "local",
            "type": type(value).__name__,
            "value": safe_serialize(value)
        }

    # Inspecter les variables globales
    global_vars = outer_frame.f_globals
    for name, value in global_vars.items():
        if name not in variables_info:  # Éviter d'écraser les locales si elles portent le même nom
            variables_info[name] = {
                "scope": "global",
                "type": type(value).__name__,
                "value": safe_serialize(value)
            }

    # Exporter les données dans un fichier JSON
    with open(output_path, "w") as json_file:
        json.dump(variables_info, json_file, indent=4)





# Boucle principale
running = True
tick = 0

while running:
    tick += 1
    
    if player.is_dead():
        running = False
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT:
                case_inventaire += 1
            if event.key == pygame.K_LEFT:
                case_inventaire -= 1
            if event.key == pygame.K_F3:
                F3_panel()
    case_inventaire = (case_inventaire - 1) % 10 + 1

    keys = pygame.key.get_pressed()
    
    # Déplacement du joueur
    if keys[pygame.K_q]:
        player.move("gauche")
    if keys[pygame.K_d]:
        player.move("droite")
    if keys[pygame.K_z]:
        player.move("haut")
    if keys[pygame.K_s]:
        player.move("bas")
        
    # print(bloc_pos(x + (TAILLE_PIXEL / 2), y + (TAILLE_PIXEL / 2)))


    # Logique du jeu
    ecran.fill(Couleurs["CIEL"])
    
    # Dessiner la GameMap.world
    game_map.Afficher(decalage_x = player.x, decalage_y = player.y)

    # Modification de la position des mobs
    mobs = modify_pos_mob(mobs, player.x, player.y, TAILLE_PIXEL, tick)
    
    # Dessiner les mobs
    dessiner_mobs()
    
    # Dessiner les drops
    dessiner_drops(drops)
    
    # Dessiner le joueur
    pygame.draw.rect(ecran, Couleurs["JOUEUR"], (LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2, TAILLE_PIXEL, TAILLE_PIXEL))
    
    # Dessiner l'inventaire
    dessiner_hotbar(case_inventaire, player.inventaire)
    dessiner_inventaire(player.inventaire)
    
    # Dessiner les coeurs
    dessiner_coeurs(player.life)
    
    # Dessiner la barre d'XP
    afficher_xp(player.xp)
    

    # Afficher le panel F3
    if keys[pygame.K_F3]:
        F3_panel()

    # Afficher le panel F4
    if keys[pygame.K_F4]:
        F4_panel()

    # Mise à jour de l'écran
    pygame.display.flip()
    
    # Verification des types de variables
    unit_test_variables_types()

    # exportation des infos importantes sur les variables
    track_variables()
    
    # Contrôle de la fréquence d'images
    clock.tick(60)


font = pygame.font.Font(None, 36)
ecran.blit((lambda s: (s.fill((50, 50, 50, 150)), s)[1])(pygame.Surface(ecran.get_size(), pygame.SRCALPHA)), (0, 0)) # Fond gris legerement transparent

# Rendu et positionnement du texte "You died!!!"
texte_died = font.render('You died!!!', True, (255, 0, 0))
rect_died = texte_died.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2 - 20))
ecran.blit(texte_died, rect_died)

# Rendu et positionnement du texte "Appuyez sur espace"
texte_espace = font.render('Appuyez sur espace', True, (255, 255, 255))
rect_espace = texte_espace.get_rect(center=(LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2 + 20))
ecran.blit(texte_espace, rect_espace)

pygame.display.flip()

running = True
# Boucle principale de fin
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            running = False
    sleep(0.1)
print()
# Quitter Pygame proprement
pygame.quit()
input("vous pouvez fermer la fenetre")
