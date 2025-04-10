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
LARGEUR_MAP, HAUTEUR_MAP = 50, 50
TAILLE_PIXEL = 50

@dataclass
class MobsDefaultBySpecies:
    species: str
    base_hearts: int
    strength_attack: int
    loot: List[str]
    hostility: bool
    xp: int
    speed: float

@dataclass
class Entity:
    species: str
    id: int
    coords: Dict[str, int]
    hearts: int
    strength_attack: int
    loot: List[str]
    hostility: bool
    xp: int
    speed: float

    @classmethod
    def from_species(cls, species_data: MobsDefaultBySpecies, id: int, coords: Dict[str, int]):
        """Crée une entité à partir des données par défaut d'une espèce."""
        return cls(
            species=species_data.species,
            id=id,
            coords=coords,
            hearts=species_data.base_hearts,
            strength_attack=species_data.strength_attack,
            loot=species_data.loot,
            hostility=species_data.hostility,
            xp=species_data.xp,
            speed=species_data.speed,
        )

# Instances de MobsDefaultBySpecies
creeper = MobsDefaultBySpecies("creeper", 5, 5, ['gunpowder'], True, 5, 0.05)
zombie = MobsDefaultBySpecies("zombie", 5, 2, ['rotten_flesh'], True, 5, 0.05)
spider = MobsDefaultBySpecies("spider", 5, 2, ['ficelle', 'oeil_d_araignee'], True, 5, 0.05)
cochon = MobsDefaultBySpecies("cochon", 5, 5, ['pork'], False, 5, 0.05)
cheval = MobsDefaultBySpecies("cheval", 5, 5, ['cuir'], False, 5, 0.05)
mouton = MobsDefaultBySpecies("mouton", 5, 5, ['laine', 'mouton_cru'], False, 5, 0.05)
enderman = MobsDefaultBySpecies("enderman", 5, 5, ['enderpearl'], True, 5, 0.05)
vache = MobsDefaultBySpecies("vache", 5, 5, ['cuir'], False, 5, 0.05)

# Création des entités à partir des espèces par défaut
mobs = [
    Entity.from_species(creeper, id=0, coords={"x": 200, "y": 200}),
    Entity.from_species(zombie, id=1, coords={"x": 150, "y": 300}),
    Entity.from_species(spider, id=2, coords={"x": 100, "y": 400}),
]



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

chaine = input('>>>')
if chaine:
    hearts, x, y, inventaire, mobs, bouffe, vitesse, effects_potions, xp = eval(decompresser(chaine))

mangeable = {
    'pork': [5.0, 0],
    'cooked_pork': [10.0, 0],
    'mouton_cru': [5.0, 0],
    'cooked_mouton': [10.0, 0],
    'rotten_flesh': [5.0, 2]
}

poison = 0.0
drops = []
incassables = ['air', 'sortie', 'bordure', 'fleche', 'case', 'gris']
modify_bloc_to_item = {
    'verre2': 'inventaire_vide',
    'verre1': 'verre2'
}
if 'coeurs' in locals() and coeurs < 1: coeurs = 9
if not 'coeurs' in locals(): coeurs = 9
if not 'bouffe' in locals(): bouffe = 9
if not 'bouffe_totale' in locals(): bouffe_totale = 9
if not 'effects_potions' in locals(): effects_potions = {'poison': {'durée': 0.0}, 'fatigue': {'durée': 0.0}}
if not 'xp' in locals(): xp = 15
case_inventaire = 1
if not 'inventaire' in locals(): inventaire = ['inventaire_vide'] * 38 + ['bois'] *2
hearts = 20
FORCE_JOUEUR = 2
vitesse = 4
saut = 0
degats_de_chute = 0

from random import randint

def modify_pos_mob(mobs: list, x: float, y: float, TAILLE_PIXEL: int, tick: int) -> list:
    for mob in mobs:
        SPEED = mob.speed  # Utilisation de la vitesse de l'instance du mob
        
        # Convertir les coordonnées du joueur en unités de la grille
        player_x, player_y = x, y
        
        if mob.species == 'enderman' and tick % 60 == 0:
            i = 0
            while i < 50:
                i += 1
                # Calculer la direction vers le joueur
                dx = player_x - mob.coords['x']
                dy = player_y - mob.coords['y']
                if abs(dx) < 3 * TAILLE_PIXEL and abs(dy) < 3 * TAILLE_PIXEL:
                    break
                testx, testy = randint(1, 40) * TAILLE_PIXEL, randint(1, 40) * TAILLE_PIXEL
                if not bloc_pos(testx + (TAILLE_PIXEL / 2), testy + (TAILLE_PIXEL / 2)) in incassables:
                    mob.coords['x'] = testx
                    mob.coords['y'] = testy
            
        # Calculer la direction vers le joueur
        dx = player_x - mob.coords['x']
        dy = player_y - mob.coords['y']
        
        centre_x = mob.coords['x'] + (TAILLE_PIXEL / 2)
        centre_y = mob.coords['y'] + (TAILLE_PIXEL / 2)
        est_araignee = mob.species == 'spider'
        
        # Déplacement horizontal
        if dx > 0 and (est_araignee or not bloc_pos(centre_x + SPEED, centre_y) in incassables):
            mob.coords['x'] += SPEED
        elif dx < 0 and (est_araignee or not bloc_pos(centre_x - SPEED, centre_y) in incassables):
           mob.coords['x'] -= SPEED
        
        # Déplacement vertical
        if dy > 0 and (est_araignee or not bloc_pos(centre_x, centre_y + SPEED) in incassables):
            mob.coords['y'] += SPEED
        elif dy < 0 and (est_araignee or not bloc_pos(centre_x, centre_y - SPEED) in incassables):
            mob.coords['y'] -= SPEED

        # Débogage : Afficher les valeurs intermédiaires
        #print(f"Player position: ({x}, {y})")
        #print(f"dx: {dx}, dy: {dy}")
        #print(f"New mob position: ({mob.coords['x']}, {mob.coords['y']})")
        #print(mob)
    return mobs

def creer_map():
    # Initialisation de la carte avec des 'air'
    map = [['air' for _ in range(LARGEUR_MAP)] for __ in range(HAUTEUR_MAP)]
    
    # Ajout des bordures
    for i in range(HAUTEUR_MAP):
        map[i][0] = 'bordure'
        map[i][-1] = 'bordure'
        map[0][i] = 'bordure'
        map[-1][i] = 'bordure'
        
    
    # Stuff de base
    map[1][1:3] = 'coffre', 'etabli', 'furnace_burned'
    
    # Arbre
    def arbre(x, y):
        map[y+1][x] = 'bois'
        map[y][x] = 'bois'
        map[y-1][x] = 'bois'
        map[y-2][x] = 'bois'
        map[y-2][x-1] = 'leaves'
        map[y-2][x] = 'leaves'
        map[y-2][x+1] = 'leaves'
        map[y-3][x] = 'leaves'
    
    arbre(6, 5)
    arbre(7, 5)
    arbre(14, 20)
    arbre(15, 20)
    arbre(9, 25)
    arbre(10, 25)
    
    return map

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

# Appel de la fonction
if not 'map' in locals():
    map = creer_map()



# Couleurs
Couleurs = {
    "CIEL_SOIR": (15, 5, 107),
    "CIEL": (0, 191, 255),
    "JOUEUR": (255, 140, 0),
    "INVENTAIRE": (169, 169, 169),
    "INVENTAIRE_VIDE": (169, 169, 169),
    "RED": (255, 0, 0),
    "GREEN": (0, 225, 0),
    "AIR": (0, 150, 0)
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
        return map[grid_y][grid_x] != 'bordure'
    return False

def bloc_pos(x: float, y: float) -> str:
    # Convertir les coordonnées en indices de la grille
    grid_x = int(x // TAILLE_PIXEL)
    grid_y = int(y // TAILLE_PIXEL)
    try:
        return map[grid_y][grid_x]
    except:
        raise IndexError(f"error: return map[{grid_y}][{grid_x}] in bloc_pos()")

def modify(x: float, y: float, bloc: str) -> None:
    # Convertir les coordonnées en indices de la grille
    grid_x = int(x / TAILLE_PIXEL)
    grid_y = int(y / TAILLE_PIXEL)
    map[grid_y][grid_x] = bloc

# Fonction pour dessiner la barre de vie
def draw_health_bar(screen, x, y, health, max_health, width, height):
    ratio = health / max_health
    pygame.draw.rect(screen, Couleurs["RED"], (x, y, width, height))
    pygame.draw.rect(screen, Couleurs["GREEN"], (x, y, width * ratio, height))




def dessiner_map(decalage_x: float, decalage_y: float) -> None:
    for y in range(HAUTEUR_MAP):
        for x in range(LARGEUR_MAP):
            bloc_x = x * TAILLE_PIXEL - int(decalage_x)
            bloc_y = y * TAILLE_PIXEL - int(decalage_y)
            if -TAILLE_PIXEL <= bloc_x < LARGEUR_ECRAN and -TAILLE_PIXEL <= bloc_y < HAUTEUR_ECRAN:
                ecran.blit(image(map[y][x]), (bloc_x, bloc_y))

def dessiner_mobs():
    # Dessin des mobs
    for mob in mobs:
        x_mob = int(mob.coords['x'] - decalage_x)
        y_mob = int(mob.coords['y'] - decalage_y)
        image_mob = image(mob.species)
        
        ecran.blit(image_mob, (x_mob, y_mob))
        
        # Dessin de la barre de vie
        bar_width = image_mob.get_width()
        bar_height = 10
        bar_x = x_mob
        bar_y = y_mob + image_mob.get_height() - 5
        
        draw_health_bar(ecran, bar_x, bar_y, mob.hearts, 5, bar_width, bar_height)
    

def dessiner_drops(drops: list) -> None:
    # Dessin des drops
    for drop in drops:
        x_drop = int(drop['x'] - decalage_x)
        y_drop = int(drop['y'] - decalage_y)
        ecran.blit(image(drop['name']), (x_drop, y_drop))

def dessiner_hotbar(case_inventaire: list, inventaire: list) -> None:
    nombre_cases = 10
    largeur_totale = nombre_cases * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2
    couleur_bordure = (100, 100, 100)  # Gris très foncé
    couleur_bordure2 = (50, 50, 50)  # Gris encore plus foncé
    
    for i in range(nombre_cases):
        x = position_x_debut + (i * TAILLE_PIXEL)
        y = HAUTEUR_ECRAN - TAILLE_PIXEL
        
        # Dessiner la case de l'inventaire
        pygame.draw.rect(ecran, Couleurs["INVENTAIRE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
        ecran.blit(image(inventaire[i]), (x+2, y+2))
        
        # Dessiner la bordure autour de la case
        pygame.draw.rect(ecran, couleur_bordure2, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
        pygame.draw.rect(ecran, couleur_bordure, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)
        
        # Mettre en évidence la case sélectionnée
        if i == case_inventaire - 1:
            pygame.draw.rect(ecran, (255, 255, 255), (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 2)

def dessiner_inventaire(case_inventaire: list, inventaire: list) -> None:
    nombre_cases = 10
    largeur_totale = nombre_cases * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2
    couleur_bordure = (100, 100, 100)  # Gris très foncé
    couleur_bordure2 = (50, 50, 50)  # Gris encore plus foncé
    
    for n in range(3):
        for i in range(nombre_cases):
            x = position_x_debut + (i * TAILLE_PIXEL)
            y = HAUTEUR_ECRAN - (TAILLE_PIXEL * (n + 2.5))
            
            # Dessiner la case de l'inventaire
            pygame.draw.rect(ecran, Couleurs["INVENTAIRE"], (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
            try:
                # Si ce n'est pas possible, afficher l'image de l'objet
                ecran.blit(image(inventaire[i + nombre_cases + n*nombre_cases]), (x+2, y+2))
            except IndexError:
                # Case vide, ne rien faire
                pass
            
            # Dessiner la bordure autour de la case
            pygame.draw.rect(ecran, couleur_bordure2, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
            pygame.draw.rect(ecran, couleur_bordure, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)

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

def dessiner_coeurs(nombre_demis_coeurs: int, nombre_cases_inventaire: int, vies: int) -> None:    
    largeur_totale = nombre_cases_inventaire * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2 - (TAILLE_PIXEL/2)
    y_coeur = HAUTEUR_ECRAN - 2 * TAILLE_PIXEL  # Juste au-dessus de l'inventaire
    
    # Tremblement si peu de vies (moins de 4 demis coeurs)
    if vies <= 4:
        y_coeur += randint(-5, 5)
        position_x_debut += randint(-5, 5)
    
    
    if nombre_demis_coeurs % 2 != 0:
        raise ValueError("nombre de coeurs total doit etre divisible par 2 dans dessiner_coeurs()")
    
    for i in range(nombre_demis_coeurs // 2):
        # Calcul de la position en x pour chaque cœur
        x_coeur = position_x_debut + (i * int(TAILLE_PIXEL / 2))
        
        # Détermine quelle image afficher en fonction des vies restantes
        if vies >= (i + 1) * 2:  # Si le joueur a un cœur entier à cet emplacement
            image_a_afficher = image('heart')
        elif vies == (i * 2) + 1:  # Si le joueur a un demi-cœur à cet emplacement
            image_a_afficher = image('demi_heart')
        else:  # Si le joueur n'a plus de vie à cet emplacement
            image_a_afficher = image('heart_vide')
                
        ecran.blit(pygame.transform.scale(image_a_afficher, (int(TAILLE_PIXEL/2), int(TAILLE_PIXEL/2))), (x_coeur, y_coeur))

def F3_panel():
    vars = ["x", "y"]
    
    # Calcule la taille dynamique de la police
    font_size = (HAUTEUR_ECRAN // len(vars))
    font = pygame.font.Font(None, font_size)
    
    y_offset = 0
    lines = []
    
    for element in vars:
        # Vérification sécurisée de l'existence de la variable
        if element in globals():
            lines.append(f"{element}: {globals()[element]}")
        else:
            raise NameError(f"Variable '{element}' non définie (tentative d'y acceder depuis F3_panel())")
    
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        ecran.blit(text_surface, (50, y_offset))
        y_offset += font_size


def F4_panel():
    # Capture les variables locales
    vars = globals()
    
    # Convertit le dictionnaire en une chaîne formatée
    var_str = "\n".join([f"{key}: {value}" for key, value in vars.items() if not callable(value) and not key.startswith("__")])
    
    # Divise le texte en lignes
    lines = var_str.split('\n')
    
    # Calcule la taille dynamique de la police en fonction du nombre de lignes
    font_size = (HAUTEUR_ECRAN // len(lines))
    font = pygame.font.Font(None, font_size)
    
    # Position initiale pour dessiner le texte
    y_offset = 0
    
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        ecran.blit(text_surface, (50, y_offset))
        y_offset += font_size  # Pas d'interligne, chaque ligne est directement sous la précédente



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
x, y = 0, 0
decalage_x, decalage_y = -x, -y
running = True
tick = 0

while running:
    tick += 1
    
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
    if case_inventaire > 10:
        case_inventaire = 1
    if case_inventaire < 1:
        case_inventaire = 10
    keys = pygame.key.get_pressed()
    
    # Déplacement du joueur
    if keys[pygame.K_q]:
        x -= 1
        decalage_x -= 1
    if keys[pygame.K_d]:
        x += 1
        decalage_x += 1
        
    # print(bloc_pos(x + (TAILLE_PIXEL / 2), y + (TAILLE_PIXEL / 2)))


    # Logique du jeu
    ecran.fill(Couleurs["CIEL"])
    
    # Dessiner la map
    dessiner_map(decalage_x, decalage_y)

    # Modification de la position des mobs
    mobs = modify_pos_mob(mobs, x, y, TAILLE_PIXEL, tick)
    
    # Dessiner les mobs
    dessiner_mobs()
    
    # Dessiner les drops
    dessiner_drops(drops)
    
    # Dessiner le joueur
    pygame.draw.rect(ecran, Couleurs["JOUEUR"], (LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2, TAILLE_PIXEL, TAILLE_PIXEL))
    
    # Dessiner l'inventaire
    dessiner_hotbar(case_inventaire, inventaire)
    dessiner_inventaire(case_inventaire, inventaire)
    
    # Dessiner les coeurs
    dessiner_coeurs(20, 10, hearts)
    
    # Dessiner la barre d'XP
    afficher_xp(xp)
    

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
print(compresser(f'[{hearts}, {x}, {y}, {inventaire}, {mobs}, {bouffe}, {vitesse}, {effects_potions}, {xp}]'))
# Quitter Pygame proprement
pygame.quit()
input("vous pouvez fermer la fenetre")
