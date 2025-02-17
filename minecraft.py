import pygame
from time import sleep
from random import *
import math
import zlib
import base64

# Initialisation de Pygame
pygame.init()

# Définition des constantes
LARGEUR_ECRAN = 1200
HAUTEUR_ECRAN = 600
LARGEUR_MAP = 50
HAUTEUR_MAP = 50
TAILLE_PIXEL = 50


drops_mobs = {
    'creeper': [['poudre_a_canon']],
    'zombie': [['rotten_flesh']],
    'spider': [['ficelle', 'oeil_d_araignee']],
    'cochon': [['pork']],
    'cheval': [['cuir', 'cuir']],
    'mouton': [['laine', 'laine', 'laine', 'mouton_cru']],
    'enderman': [['enderpearl']],
    'vache': [['cuir']]
}
mobs_hostiles = ['creeper', 'zombie', 'spider', 'enderman', 'mouton']
mobs = [
    {
      'name': 'creeper',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 5, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'zombie',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 2, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'spider',
      'x': 50,
      'y': 50,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 2, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'cochon',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 0, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'vache',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 0, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'cheval',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 50,
      'vie': 5,
      'force_attaque': 0, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'mouton',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 0, #en demis coeurs
      'degats_de_chute': 0
    },
    {
      'name': 'enderman',
      'x': 200,
      'y': 200,
      'tick': 5,
      'vie_totale': 5,
      'vie': 5,
      'force_attaque': 5, #en demis coeurs
      'degats_de_chute': 0
    }
]
mobs_to_xp = {
    'creeper': 5,
    'zombie': 5,
    'spider': 5,
    'cochon': 5,
    'cheval': 5,
    'mouton': 5,
    'enderman': 5,
    'vache': 5
}
mobs_to_speed = {
    'creeper': TAILLE_PIXEL / 20,
    'zombie': TAILLE_PIXEL / 20,
    'spider': TAILLE_PIXEL / 20,
    'cochon': TAILLE_PIXEL / 20,
    'cheval': TAILLE_PIXEL / 20,
    'mouton': TAILLE_PIXEL / 20,
    'enderman': TAILLE_PIXEL / 20,
    'vache': TAILLE_PIXEL / 20
}
def compresser(texte):
    # Compresser le texte en utilisant zlib
    donnees_compressees = zlib.compress(texte.encode('utf-8'))
    # Encoder les données compressées en Base64 pour garantir des caractÃ¨res imprimables
    donnees_base64 = base64.b64encode(donnees_compressees)
    # Convertir les données encodées en une chaÃ®ne de caractÃ¨res
    return donnees_base64.decode('utf-8')

def decompresser(texte_compresse):
    # Décoder le texte compressé de Base64
    donnees_base64 = base64.b64decode(texte_compresse.encode('utf-8'))
    # Décompresser les données en utilisant zlib
    donnees_decompressees = zlib.decompress(donnees_base64)
    # Convertir les données décompressées en une chaÃ®ne de caractÃ¨res
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
if not 'xp' in locals(): xp = 10
running = True
case_inventaire = 1
if not 'inventaire' in locals(): inventaire = ['inventaire_vide'] * 10
teleportation = False
if not 'portail' in locals(): portail = None
hearts = 9
FORCE_JOUEUR = 2
jour = True
vitesse = 4
sur_cheval = False
saut = 0
degats_de_chute = 0
blocs_amortisseurs = ['ficelle']

from random import randint

def modify_pos_mob(mobs, x, y, TAILLE_PIXEL):
    for mob in mobs:
        SPEED = mobs_to_speed[mob['name']]  # Vitesse constante du mob
        print(mob['name'], SPEED)
        
        # Convertir les coordonnées du joueur en unités de la grille
        player_x = x
        player_y = y
        
        if mob['name'] == 'enderman' and tick % mob['tick'] == 0:
            i = 0
            while i < 50:
                i += 1
                # Calculer la direction vers le joueur
                dx = player_x - mob['x']
                dy = player_y - mob['y']
                if abs(dx) < 3 * TAILLE_PIXEL and abs(dy) < 3 * TAILLE_PIXEL:
                    break
                testx, testy = randint(1, 40) * TAILLE_PIXEL, randint(1, 40) * TAILLE_PIXEL
                if not bloc_pos_joueur(testx + (TAILLE_PIXEL / 2), testy + (TAILLE_PIXEL / 2)) in incassables:
                    mob['x'] = testx
                    mob['y'] = testy
            
        # Calculer la direction vers le joueur
        dx = player_x - mob['x']
        dy = player_y - mob['y']
        
        centre_x = mob['x'] + (TAILLE_PIXEL / 2)
        centre_y = mob['y'] + (TAILLE_PIXEL / 2)
        est_araignee = mob['name'] == 'spider'
        
        # Déplacement horizontal
        if dx > 0 and (est_araignee or not bloc_pos_joueur(centre_x + SPEED, centre_y) in incassables):
            mob['x'] += SPEED
        elif dx < 0 and (est_araignee or not bloc_pos_joueur(centre_x - SPEED, centre_y) in incassables):
           mob['x'] -= SPEED
        
        # Déplacement vertical
        if dy > 0 and (est_araignee or not bloc_pos_joueur(centre_x, centre_y + SPEED) in incassables):
            mob['y'] += SPEED
        elif dy < 0 and (est_araignee or not bloc_pos_joueur(centre_x, centre_y - SPEED) in incassables):
            mob['y'] -= SPEED

    # Débogage : Afficher les valeurs intermédiaires
    #print(f"Player position: ({x}, {y})")
    #print(f"dx: {dx}, dy: {dy}")
    #print(f"New mob position: ({mob['x']}, {mob['y']})")
    #print(mobs)
    return mobs

def craft(valeur_recherchee):
    craft_table = {
        'bois-air-air air-air-air air-air-air': 'planche',
        'air-bois-air air-air-air air-air-air': 'planche',
        'air-air-bois air-air-air air-air-air': 'planche',
        'air-air-air bois-air-air air-air-air': 'planche',
        'air-air-air air-bois-air air-air-air': 'planche',
        'air-air-air air-air-bois air-air-air': 'planche',
        'air-air-air air-air-air bois-air-air': 'planche',
        'air-air-air air-air-air air-bois-air': 'planche',
        'air-air-air air-air-air air-air-bois': 'planche',
        'planche-planche-planche planche-air-planche planche-planche-planche': 'coffre',
        'planche-planche-air planche-planche-air air-air-air': 'etabli',
        'air-air-air planche-planche-air planche-planche-air': 'etabli',
        'air-air-air air-planche-planche air-planche-planche': 'etabli',
        'air-planche-planche air-planche-planche air-air-air': 'etabli',
        'pierre-pierre-pierre pierre-air-pierre-pierre-pierre-pierre': 'fourneau',
        'air-pepite_fer-air pepite_fer-air-air air-air-air': 'cisailles',
        'air-air-pepite_fer air-pepite_fer-air air-air-air': 'cisailles',
        'air-air-air air-pepite_fer-air pepite_fer-air-air': 'cisailles',
        'air-air-air air-air-pepite_fer air-pepite_fer-air': 'cisailles',
        'planche-air-air planche-air-air air-air-air': 'stick',
        'air-planche-air air-planche-air air-air-air': 'stick',
        'air-air-planche air-air-planche air-air-air': 'stick',
        'air-air-air planche-air-air planche-air-air': 'stick',
        'air-air-air air-planche-air air-planche-air': 'stick',
        'air-air-air air-air-planche air-air-planche': 'stick',
        'air-air-air laine-laine-laine planche-planche-planche': 'lit',
        'laine-laine-laine planche-planche-planche air-air-air': 'lit'
    }
    try:
        return craft_table[valeur_recherchee]
    except:
        pass
    return 'air'  # Retourne None si aucune correspondance n'est trouvée

def cuire(valeur_recherchee):
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
    return 'air'  # Retourne None si aucune correspondance n'est trouvée




def creer_map():
    # Initialisation de la carte avec des 'air'
    map = [['air' for _ in range(LARGEUR_MAP)] for __ in range(HAUTEUR_MAP)]
    
    # Ajout des bordures en haut et en bas
    map[0] = ['bordure' for _ in range(LARGEUR_MAP)]
    map[-1] = ['bordure' for _ in range(LARGEUR_MAP)]
    
    # Ajout des bordures Ã  gauche et Ã  droite
    for i in range(HAUTEUR_MAP):
        map[i][0] = 'bordure'
        map[i][-1] = 'bordure'
    
    # Ajout des bordures spécifiques
    for i in range(2, LARGEUR_MAP):
        map[-5][i] = 'bordure'
    
    # Etabli
    map[-4][5] = 'sortie'
    map[-4][6] = 'bordure'
    map[-3][6] = 'bordure'
    map[-2][6] = 'bordure'
    
    # Furnace
    map[-4][9] = 'sortie'
    map[-4][10] = 'bordure'
    map[-3][10] = 'bordure'
    map[-2][10] = 'bordure'
    
    # Coffre
    map[-4][11] = 'sortie'
    
    # Stuff de base
    map[1][1] = 'coffre'
    map[1][2] = 'etabli'
    map[1][3] = 'furnace_burned'
    
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
    
    print(map)
    return map

# Appel de la fonction
if not 'map' in locals():
    map = creer_map()



# Couleurs
CIEL_SOIR = (15, 5, 107)
CIEL = (0, 191, 255)
JOUEUR = (255, 140, 0)
INVENTAIRE = (169, 169, 169)
INVENTAIRE_VIDE = (169, 169, 169)
RED = (255, 0, 0)
GREEN = (0, 225, 0)
air_HAUTE = (0, 200, 0)
air = (0, 150, 0)

necessite = {
    'pierre': ['pioche', 'inventaire_vide'],
    'leaves': ['cisailles', 'inventaire_vide']
}

def inventory(map):
    result = []
    for n in [3, 2, 1]:
        row = [map[-2][n], map[-3][n], map[-4][n]]
        result.append(row)
    
    # Rotation de 90 degrés
    rotated = list(zip(*result[::-1]))
    return [rotated[-(i+1)] for i in range(0, len(rotated))]

image_cache = {}
def image(texte):
    # Charger l'image
    if texte not in image_cache:
        image_cache[texte] = pygame.image.load(fr"C:\Users\Killian\Desktop\minecraft\images\{texte}.jpg")
        image_cache[texte] = pygame.transform.scale(image_cache[texte], (TAILLE_PIXEL, TAILLE_PIXEL))
    # Redimensionner l'image Ã  la taille du bloc
    return image_cache[texte]

# Création de la fenÃªtre
ecran = pygame.display.set_mode((LARGEUR_ECRAN, HAUTEUR_ECRAN))
pygame.display.set_caption("Minecraft 1.0")
clock = pygame.time.Clock()

def verifier_collision(x, y):
    # Convertir les coordonnées en indices de la grille
    grid_x = round(x / TAILLE_PIXEL)
    grid_y = round(y / TAILLE_PIXEL)
    
    # Vérifier si les indices sont dans les limites de la carte
    if 0 <= grid_x < LARGEUR_MAP and 0 <= grid_y < HAUTEUR_MAP:
        return map[grid_y][grid_x] != 'bordure'
    return False

def bloc_pos_joueur(x, y):
    # Convertir les coordonnées en indices de la grille
    grid_x = int(x / TAILLE_PIXEL)
    grid_y = int(y / TAILLE_PIXEL)
    try:
        return map[grid_y][grid_x]
    except:
        print('error: return map[grid_y][grid_x]')
        return None

def modify(x, y, bloc):
    # Convertir les coordonnées en indices de la grille
    grid_x = int(x / TAILLE_PIXEL)
    grid_y = int(y / TAILLE_PIXEL)
    map[grid_y][grid_x] = bloc

# Fonction pour dessiner la barre de vie
def draw_health_bar(screen, x, y, health, max_health, width, height):
    ratio = health / max_health
    pygame.draw.rect(screen, RED, (x, y, width, height))
    pygame.draw.rect(screen, GREEN, (x, y, width * ratio, height))




def dessiner_map(decalage_x, decalage_y):
    for y in range(HAUTEUR_MAP):
        for x in range(LARGEUR_MAP):
            bloc_x = x * TAILLE_PIXEL - int(decalage_x)
            bloc_y = y * TAILLE_PIXEL - int(decalage_y)
            if -TAILLE_PIXEL <= bloc_x < LARGEUR_ECRAN and -TAILLE_PIXEL <= bloc_y < HAUTEUR_ECRAN:
                try:
                    if map[y][x] == 'air':
                        # Simplification des conditions pour les cases spéciales
                        special_cases = {
                            (5, HAUTEUR_MAP-4): 'gris', (5, HAUTEUR_MAP-3): 'case', (5, HAUTEUR_MAP-2): 'gris',
                            (4, HAUTEUR_MAP-4): 'gris', (4, HAUTEUR_MAP-3): 'fleche', (4, HAUTEUR_MAP-2): 'gris',
                            (3, HAUTEUR_MAP-4): 'case', (3, HAUTEUR_MAP-3): 'case', (3, HAUTEUR_MAP-2): 'case',
                            (2, HAUTEUR_MAP-4): 'case', (2, HAUTEUR_MAP-3): 'case', (2, HAUTEUR_MAP-2): 'case',
                            (1, HAUTEUR_MAP-4): 'case', (1, HAUTEUR_MAP-3): 'case', (1, HAUTEUR_MAP-2): 'case',
                            (9, HAUTEUR_MAP-3): 'case', (9, HAUTEUR_MAP-2): 'gris',
                            (8, HAUTEUR_MAP-2): 'gris', (8, HAUTEUR_MAP-3): 'fleche', (8, HAUTEUR_MAP-4): 'gris',
                            (7, HAUTEUR_MAP-2): 'gris', (7, HAUTEUR_MAP-3): 'case', (7, HAUTEUR_MAP-4): 'gris'
                        }
                        
                        if (x, y) in special_cases:
                            ecran.blit(image(special_cases[(x, y)]), (bloc_x, bloc_y))
                        elif x >= 7 and y >= HAUTEUR_MAP-4:
                            ecran.blit(image('case'), (bloc_x, bloc_y))
                        else:
                            # Alternance de couleurs pour l'air
                            color = air if (y+x) % 2 == 0 else air_HAUTE
                            pygame.draw.rect(ecran, color, (bloc_x, bloc_y, TAILLE_PIXEL, TAILLE_PIXEL))
                    else:
                        # Dessin des blocs non-air
                        pygame.draw.rect(ecran, eval(map[y][x].upper()), (bloc_x, bloc_y, TAILLE_PIXEL, TAILLE_PIXEL))
                except Exception as e:
                    print(f'Erreur dans dessiner_map: {e}')
                    ecran.blit(image(map[y][x]), (bloc_x, bloc_y))
    
    # Dessin des mobs
    for mob in mobs:
        x_mob = int(mob['x'] - decalage_x)
        y_mob = int(mob['y'] - decalage_y)
        image_mob = image(mob['name'])
        
        ecran.blit(image_mob, (x_mob, y_mob))
        
        # Dessin de la barre de vie
        bar_width = image_mob.get_width()
        bar_height = 10
        bar_x = x_mob
        bar_y = y_mob + image_mob.get_height() - 5
        
        draw_health_bar(ecran, bar_x, bar_y, mob['vie'], mob['vie_totale'], bar_width, bar_height)
    
    # Dessin des drops
    for drop in drops:
        x_drop = int(drop['x'] - decalage_x)
        y_drop = int(drop['y'] - decalage_y)
        ecran.blit(image(drop['name']), (x_drop, y_drop))




def dessiner_hotbar(case_inventaire, inventaire):
    nombre_cases = 10
    largeur_totale = nombre_cases * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2
    couleur_bordure = (100, 100, 100)  # Gris très foncé
    couleur_bordure2 = (50, 50, 50)  # Gris encore plus foncé
    
    for i in range(nombre_cases):
        x = position_x_debut + (i * TAILLE_PIXEL)
        y = HAUTEUR_ECRAN - TAILLE_PIXEL
        
        # Dessiner la case de l'inventaire
        pygame.draw.rect(ecran, INVENTAIRE, (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
        try:
            # Essayer de dessiner un rectangle coloré pour l'objet
            pygame.draw.rect(ecran, eval(inventaire[i].upper()), (x+2, y+2, TAILLE_PIXEL-4, TAILLE_PIXEL-4))
        except:
            # Si ce n'est pas possible, afficher l'image de l'objet
            ecran.blit(image(inventaire[i]), (x+2, y+2))
        
        # Dessiner la bordure autour de la case
        pygame.draw.rect(ecran, couleur_bordure2, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
        pygame.draw.rect(ecran, couleur_bordure, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)
        
        # Mettre en évidence la case sélectionnée
        if i == case_inventaire - 1:
            pygame.draw.rect(ecran, (255, 255, 255), (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 2)

def dessiner_inventaire(case_inventaire, inventaire):
    nombre_cases = 10
    largeur_totale = nombre_cases * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2
    couleur_bordure = (100, 100, 100)  # Gris très foncé
    couleur_bordure2 = (50, 50, 50)  # Gris encore plus foncé
    
    for n in range(3):
        for i in range(nombre_cases):
            x = position_x_debut + (i * TAILLE_PIXEL)
            y = HAUTEUR_ECRAN - (TAILLE_PIXEL * (n + 1))
            
            # Dessiner la case de l'inventaire
            pygame.draw.rect(ecran, INVENTAIRE, (x, y, TAILLE_PIXEL, TAILLE_PIXEL))
            try:
                # Essayer de dessiner un rectangle coloré pour l'objet
                pygame.draw.rect(ecran, eval(inventaire[i + n*10].upper()), (x+2, y+2, TAILLE_PIXEL-4, TAILLE_PIXEL-4))
            except IndexError:
                # Case vide, ne rien faire
                pass
            except:
                # Si ce n'est pas possible, afficher l'image de l'objet
                ecran.blit(image(inventaire[i + n*10]), (x+2, y+2))
            
            # Dessiner la bordure autour de la case
            pygame.draw.rect(ecran, couleur_bordure2, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 3)
            pygame.draw.rect(ecran, couleur_bordure, (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 1)
            
            # Mettre en évidence la case sélectionnée
            if i + n*10 == case_inventaire - 1:
                pygame.draw.rect(ecran, (255, 255, 255), (x, y, TAILLE_PIXEL, TAILLE_PIXEL), 2)



def afficher_xp(xp):
    niveau, xp_actuel = divmod(xp, 10)
    largeur_barre = 182 * 1.5
    epaisseur = TAILLE_PIXEL / 4
    x = (LARGEUR_ECRAN - largeur_barre) // 2
    y = HAUTEUR_ECRAN - TAILLE_PIXEL * 1.33
    rayon = epaisseur / 2  # Rayon pour arrondir les coins

    # Affichage du niveau
    font = pygame.font.Font(None, 24)
    texte = font.render(f"{int(niveau)}", True, (80, 255, 80))
    ecran.blit(texte, texte.get_rect(center=(LARGEUR_ECRAN // 2, y - epaisseur - 10)))

    # Création d'une surface pour la barre d'XP
    barre_surface = pygame.Surface((largeur_barre, epaisseur), pygame.SRCALPHA)
    
    # Dessin du fond noir avec coins arrondis
    pygame.draw.rect(barre_surface, (0, 0, 0), (0, 0, largeur_barre, epaisseur), border_radius=int(rayon))
    
    # Dessin des traits verts
    for i in range(int(largeur_barre * xp_actuel / 100)):
        if i % 2 == 0:
            pygame.draw.line(barre_surface, (80, 255, 80), (i, 0), (i, epaisseur))
    
    # Application d'un masque pour garder les coins arrondis
    mask_surface = pygame.Surface((largeur_barre, epaisseur), pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255), (0, 0, largeur_barre, epaisseur), border_radius=int(rayon))
    barre_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    # Dessin du contour noir
    pygame.draw.rect(barre_surface, (0, 0, 0), (0, 0, largeur_barre, epaisseur), 1, border_radius=int(rayon))
    
    # Affichage de la barre d'XP sur l'écran
    ecran.blit(barre_surface, (x, y))

def dessiner_coeurs(nombre_coeurs, nombre_cases_inventaire, vies):
    # Charger l'image du cÅ“ur
    image_heart = image('heart')
    image_demi_heart = image('demi_heart')
    image_heart_vide = image('heart_vide')
    
    largeur_totale = nombre_cases_inventaire * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) // 2 - (TAILLE_PIXEL/2)
    if vies <= 2:
        position_x_debut += randint(-5, 5)
    y_coeur = HAUTEUR_ECRAN - 2 * TAILLE_PIXEL  # Juste au-dessus de l'inventaire
    if vies <= 2:
        y_coeur += randint(-5, 5)
    
    coeurs_pleins = int(vies)
    demi_coeur = vies % 1 > 0
    coeurs_vides = nombre_coeurs - coeurs_pleins - (1 if demi_coeur else 0)
    
    for i in range(nombre_coeurs):
        x_coeur = position_x_debut + (i * int(TAILLE_PIXEL/2))
        if i < coeurs_pleins:
            image_a_afficher = image_heart
        elif i == coeurs_pleins and demi_coeur:
            image_a_afficher = image_demi_heart
        else:
            image_a_afficher = image_heart_vide
        
        ecran.blit(pygame.transform.scale(image_a_afficher, (int(TAILLE_PIXEL/2), int(TAILLE_PIXEL/2))), (x_coeur, y_coeur))


def dessiner_faim(nombre_bouffe, nombre_cases_inventaire, bouffe, poisonned):
    # Charger l'image du bouffe
    image_bouffe = image('bouffe')
    image_demi_bouffe = image('demi_bouffe')
    image_bouffe_vide = image('bouffe_vide')
    
    largeur_totale = nombre_cases_inventaire * TAILLE_PIXEL
    position_x_debut = (LARGEUR_ECRAN - largeur_totale) + TAILLE_PIXEL * 1.5
    if bouffe <= 0:
        position_x_debut += randint(-5, 5)
    y_bouffe = HAUTEUR_ECRAN - 2 * TAILLE_PIXEL  # Juste au-dessus de l'inventaire
    if bouffe <= 0:
        y_bouffe += randint(-5, 5)
    
    bouffe_pleins = int(bouffe)
    demi_bouffe = bouffe % 1 > 0
    bouffe_vides = nombre_bouffe - bouffe_pleins - (1 if demi_bouffe else 0)
    
    for i in range(nombre_bouffe):
        x_bouffe = position_x_debut - (i * int(TAILLE_PIXEL/2))
        if i < bouffe_pleins:
            image_a_afficher = image_bouffe
        elif i == bouffe_pleins and demi_bouffe:
            image_a_afficher = image_demi_bouffe
        else:
            image_a_afficher = image_bouffe_vide
        
        ecran.blit(pygame.transform.scale(image_a_afficher, (int(TAILLE_PIXEL/2), int(TAILLE_PIXEL/2))), (x_bouffe, y_bouffe))
        if poisonned:
            # Ajout de la teinte rouge semi-transparente
            overlay = pygame.Surface((int(TAILLE_PIXEL/2), int(TAILLE_PIXEL/2)), pygame.SRCALPHA)
            overlay.fill((0, 64, 0, 64))  # Rouge avec alpha 64 (25% opaque)
            ecran.blit(overlay, (x_bouffe, y_bouffe), special_flags=pygame.BLEND_RGBA_ADD)

def attaque_speciale(mob):
    global map
    if mob['name'] == 'creeper':
        for n in [-1, 0, 1]:
            for o in [-1, 0, 1]:
                if not bloc_pos_joueur(mob['x'] + (n * TAILLE_PIXEL), mob['y'] + (o * TAILLE_PIXEL)) in ['bordure']:
                    modify(int(mob['x'] + (n * TAILLE_PIXEL)), int(mob['y'] + (o * TAILLE_PIXEL)), 'air')
        for i, _mob in enumerate(mobs):
            if abs(_mob['x'] - mob['x']) <= TAILLE_PIXEL * 2 and abs(_mob['y'] - mob['y']) <= TAILLE_PIXEL * 2:
                del mobs[i]

def afficher_effets(msg, duree, i, icone):
    font = pygame.font.Font(None, 24)
    texte_effet = font.render(msg, True, (255, 255, 255))
    texte_duree = font.render(duree, True, (170, 170, 170))
    
    largeur = max(texte_effet.get_width(), texte_duree.get_width()) + icone.get_width() + 20
    hauteur = max(40, icone.get_height() + 10)
    
    x = LARGEUR_ECRAN - largeur - 5
    y = i * (hauteur + 5) + 5
    rect = pygame.Rect(x, y, largeur, hauteur)
    
    # Dessiner le bouton
    pygame.draw.rect(ecran, (10, 10, 10), rect.inflate(4, 4))
    pygame.draw.rect(ecran, (60, 60, 60), rect)
    pygame.draw.line(ecran, (100, 100, 100), rect.topleft, rect.topright)
    pygame.draw.line(ecran, (100, 100, 100), rect.topleft, rect.bottomleft)
    pygame.draw.line(ecran, (40, 40, 40), rect.bottomleft, rect.bottomright)
    pygame.draw.line(ecran, (40, 40, 40), rect.topright, rect.bottomright)
    
    # Afficher l'icÃ´ne et le texte
    ecran.blit(icone, (rect.left + 5, rect.centery - icone.get_height() // 2))
    ecran.blit(texte_effet, (rect.left + icone.get_width() + 10, rect.top + 5))
    ecran.blit(texte_duree, (rect.left + icone.get_width() + 10, rect.bottom - texte_duree.get_height() - 5))


def afficher_overlay_texte(screen, texte, font_size=24, color=(255, 255, 255), bg_color=(0, 0, 0, 128)):
    font = pygame.font.Font(None, font_size)
    lines = texte.split('\n')
    overlay_surface = pygame.Surface((LARGEUR_ECRAN, HAUTEUR_ECRAN), pygame.SRCALPHA)
    overlay_surface.fill(bg_color)
    
    y_offset = 50  # Début du texte
    for line in lines:
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(LARGEUR_ECRAN// 2, y_offset))
        overlay_surface.blit(text_surface, text_rect)
        y_offset += font_size + font_size // 2  # Espacement entre les lignes

    screen.blit(overlay_surface, (0, 0))



def actions_e():
    global x, y, portail, teleportation, tick, bouffe
    if bloc_actuel == 'lit':
        tick = 0
        bouffe = 15
    elif bloc_actuel == 'etabli':
        portail = (x, y)
        x, y = (1) * TAILLE_PIXEL, (LARGEUR_MAP - 2) * TAILLE_PIXEL
        teleportation = True
    elif bloc_actuel == 'sortie' and portail:
        x, y = portail
        teleportation = True
    elif bloc_actuel == 'coffre':
        portail = (x, y)
        x, y = (11) * TAILLE_PIXEL, (LARGEUR_MAP - 2) * TAILLE_PIXEL
        teleportation = True
    elif bloc_actuel == 'furnace_burned':
        portail = (x, y)
        x, y = (7) * TAILLE_PIXEL, (LARGEUR_MAP - 2) * TAILLE_PIXEL
        teleportation = True

def calcul_degats_de_chute(degats_de_chute):
    return int((degats_de_chute - 2) / 100)

def overlay_nuit():
    # Ajout de la teinte grise semi-transparente
    overlay = pygame.Surface([LARGEUR_ECRAN, HAUTEUR_ECRAN], pygame.SRCALPHA)
    overlay.fill((CIEL_SOIR[0], CIEL_SOIR[1], CIEL_SOIR[2], 128))  # gris avec alpha 128 (50% opaque)
    # Blitter l'overlay sur l'écran
    ecran.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

# Position initiale du joueur
if not 'x' in locals() and not 'y' in locals():
    x, y = (5 * TAILLE_PIXEL), (5 * TAILLE_PIXEL)
    #x, y = (LARGEUR_MAP * TAILLE_PIXEL) // 2, (HAUTEUR_MAP * TAILLE_PIXEL) // 2


tick = 0
while running:
    tick += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                case_inventaire = event.key - pygame.K_0
            elif event.key == pygame.K_0:
                case_inventaire = 10
    
    keys = pygame.key.get_pressed()
    nouvelle_x, nouvelle_y = x, y
    
    if not teleportation:
        if keys[pygame.K_LEFT]: nouvelle_x -= vitesse
        if keys[pygame.K_RIGHT]: nouvelle_x += vitesse
        if keys[pygame.K_DOWN]: nouvelle_y += vitesse
        
        # Sauter et tomber
        if bloc_pos_joueur(nouvelle_x, nouvelle_y + TAILLE_PIXEL) == 'air':
            if saut == 0:
                nouvelle_y += vitesse  # Si le joueur n'est pas sur un bloc et ne saute pas, tomber
                degats_de_chute += 1
            else:
                nouvelle_y -= vitesse  # Continuer Ã  monter si le saut est en cours
                saut -= 1
        else:
            if degats_de_chute > 2 and not bloc_pos_joueur(nouvelle_x, nouvelle_y + TAILLE_PIXEL) in blocs_amortisseurs:
                coeurs -= calcul_degats_de_chute(degats_de_chute) # Appliquer les dégÃ¢ts de chute
            degats_de_chute = 0
        
            if keys[pygame.K_UP] and saut == 0:
                saut = 3 * int(TAILLE_PIXEL / vitesse)  # Initialiser le saut

        if saut > 0:
            nouvelle_y -= vitesse  # Monter si le saut est en cours
            saut -= 1
        
        
        # Vérifier les collisions avant de mettre Ã  jour la position
        if verifier_collision(nouvelle_x, y):
            x = nouvelle_x
        if verifier_collision(x, nouvelle_y):
            y = nouvelle_y

        # Assurer que le joueur reste dans les limites de la carte
        x = max(TAILLE_PIXEL, min(x, (LARGEUR_MAP - 2) * TAILLE_PIXEL))
        y = max(TAILLE_PIXEL, min(y, (HAUTEUR_MAP - 2) * TAILLE_PIXEL))

        bloc_actuel = bloc_pos_joueur(x, y)
        if keys[pygame.K_SPACE] and bloc_actuel not in incassables:
            if bloc_actuel not in necessite:
                if bloc_actuel in modify_bloc_to_item: bloc_actuel = modify_bloc_to_item[bloc_actuel]
                for i, case in enumerate(inventaire):
                    if case == 'inventaire_vide':
                        inventaire[i] = bloc_actuel
                        modify(x, y, 'air')
                        if [int(x / TAILLE_PIXEL), int(y / TAILLE_PIXEL)] == [5,HAUTEUR_MAP-3]:
                           map[-2][3] = 'air'
                           map[-3][3] = 'air'
                           map[-4][3] = 'air'
                           map[-2][2] = 'air'
                           map[-3][2] = 'air'
                           map[-4][2] = 'air'
                           map[-2][1] = 'air'
                           map[-3][1] = 'air'
                           map[-4][1] = 'air'
                        if [int(x / TAILLE_PIXEL), int(y / TAILLE_PIXEL)] == [9, HAUTEUR_MAP-3]:
                           map[-3][7] = 'air'
                        break
            elif inventaire[case_inventaire-1] == necessite[bloc_actuel][0]:
                for i, case in enumerate(inventaire):
                    if case == 'inventaire_vide':
                        inventaire[i] = bloc_actuel
                        modify(x, y, 'air')
                        break
            else:
                for i, case in enumerate(inventaire):
                    if case == 'inventaire_vide':
                        inventaire[i] = necessite[bloc_actuel][1]
                        modify(x, y, 'air')
                        break
        if keys[pygame.K_a] and inventaire[case_inventaire-1] != 'inventaire_vide' and bloc_actuel == 'air':
            modify(x, y, inventaire[case_inventaire-1])
            inventaire[case_inventaire-1] = 'inventaire_vide'
        if keys[pygame.K_f] and inventaire[case_inventaire-1] in mangeable:
            bouffe += mangeable[inventaire[case_inventaire-1]][0]
            try:
                if randint(1, mangeable[inventaire[case_inventaire-1]][1]) == 1:
                    effects_potions['poison']['durée'] = 5.0
            except:
                pass
            inventaire[case_inventaire-1] = 'inventaire_vide'

        if keys[pygame.K_e]:
            actions_e()
    else:
        # Sortir de l'état de téléportation lorsque la touche est relÃ¢chée
        teleportation = keys[pygame.K_e]
    map[-3][5] = craft(' '.join(['-'.join(key) for key in inventory(map)]))
    map[-3][9] = cuire(map[-3][7])
    mobs = modify_pos_mob(mobs, x, y, TAILLE_PIXEL)# Parcourt la liste des mobs avec leur index
    for i, mob in enumerate(mobs):
        if bloc_pos_joueur(mob['x'], mob['y'] + TAILLE_PIXEL) == 'air':
            mob['y'] += vitesse
            mob['degats_de_chute'] += 1
        else:
            mob['vie'] -= calcul_degats_de_chute(mob['degats_de_chute'])
            mob['degats_de_chute'] = 0
        if mob['name'] in ['zombie'] and jour: mob['vie'] -= 0.1
        if keys[pygame.K_RETURN] and abs(x - mob['x']) <= TAILLE_PIXEL and abs(y - mob['y']) <= TAILLE_PIXEL and tick % 5 == 0:
            mob['vie'] -= FORCE_JOUEUR
        if keys[pygame.K_e] and mob['name'] == 'cheval' and abs(x - mob['x']) <= TAILLE_PIXEL and abs(y - mob['y']) <= TAILLE_PIXEL:
            if sur_cheval:
                sur_cheval = False
                vitesse /= 5
            else:
                sur_cheval = True
                vitesse *= 5
        if sur_cheval and mob['name'] == 'cheval':
            mob['x'], mob['y'] = x, y
        if mob['vie'] <= 0:
            xp += mobs_to_xp[mob['name']]
            for drop in choice(drops_mobs[mob['name']]):
                drops.append({'x': mob['x'], 'y': mob['y'], 'name': drop})
            del mobs[i]
        # Vérifie si les coordonnées correspondent et si le tick est un multiple de la valeur spécifiée
        if int(x) == int(mob['x']) and int(y) == int(mob['y']) and tick % mob['tick'] == 0:
            coeurs -= mob['force_attaque']  # Réduit la vie du joueur
            attaque_speciale(mob)
            # Si le mob est un creeper, le supprime de la liste
            if mob['name'] == 'creeper':
                del mobs[i]
        #print(int(mob['x'] / TAILLE_PIXEL), int(mob['y'] / TAILLE_PIXEL))
        #print(map[int(mob['x'] / TAILLE_PIXEL)][int(mob['y'] / TAILLE_PIXEL)])
    for i_drop, drop in enumerate(drops):
        if keys[pygame.K_SPACE] and abs(x - drop['x']) <= TAILLE_PIXEL and abs(y - drop['y']) <= TAILLE_PIXEL:
            for i, case in enumerate(inventaire):
                if case == 'inventaire_vide':
                    inventaire[i] = drop['name']
                    del drops[i_drop]
                    break

    if jour:
        ecran.fill(CIEL)
    else:
        ecran.fill(CIEL_SOIR)
    
    dessiner_map(x - LARGEUR_ECRAN // 2, y - HAUTEUR_ECRAN // 2)
    dessiner_coeurs(hearts, 9, coeurs)
    dessiner_faim(bouffe_totale, 9, bouffe, effects_potions['poison']['durée'] > 0.1)
    dessiner_hotbar(case_inventaire, inventaire)
    dessiner_inventaire(case_inventaire, inventaire)
    afficher_xp(xp)
    pygame.draw.rect(ecran, JOUEUR, (LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2, TAILLE_PIXEL, TAILLE_PIXEL / 2))
    pygame.draw.rect(ecran, CIEL, (LARGEUR_ECRAN // 2, HAUTEUR_ECRAN // 2 + TAILLE_PIXEL / 2, TAILLE_PIXEL, TAILLE_PIXEL / 2))
    for i, (key, element) in enumerate(effects_potions.items()):
        if element['durée'] > 5.0:
            effects_potions[key]['durée'] = 5.0
        if not element['durée'] <= 0.0:
            effects_potions[key]['durée'] -= 0.01
            afficher_effets(key, f'{int(element['durée']*10)/10} tick', i, image(key))

    if not jour:
        overlay_nuit()
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F3:
            afficher_overlay_texte(ecran, '\n'.join(f"{type(valeur).__name__} {nom}: {repr(valeur)}" for nom, valeur in locals().items() if not nom.startswith('__') and not callable(valeur)), font_size = 20)



    pygame.display.flip()
    clock.tick(60)
    running = coeurs > 0
    if any(keys) and tick % 50 == 0:
        bouffe -= 0.5
    if bouffe < 0.0:
        coeurs -= abs(bouffe)
        bouffe = 0
    if bouffe >= 9.0:
        coeurs += 2
        bouffe -= 1
    if effects_potions['poison']['durée'] > 0.0:
        coeurs -= 0.025
    if effects_potions['fatigue']['durée'] > 0.0:
        vitesse = 2.5
    coeurs = min(coeurs, 9.0)
    if bouffe <= 2.0:
        effects_potions['fatigue']['durée'] = 2.0
    if tick % 100 == 0:
        mobs.append({
            'name': 'zombie',
            'x': 5 * TAILLE_PIXEL,
            'y': 5 * TAILLE_PIXEL,
            'tick': 5,
            'vie_totale': 5,
            'vie': 5,
            'force_attaque': 2,  # en demis coeurs
            'degats_de_chute': 0
        })
    jour = tick % 2000 <= 1000 #cycle jour/nuit
    


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

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            running = False
    sleep(0.1)
print()
print(compresser(f'[{hearts}, {x}, {y}, {inventaire}, {mobs}, {bouffe}, {vitesse}, {effects_potions}, {xp}]'))
# Quitter Pygame proprement
pygame.quit()
while True: input("vous pouvez fermer la fenetre")