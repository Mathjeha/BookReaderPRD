import cv2
import numpy as np
import easyocr
from PIL import Image, ImageDraw, ImageFont

def get_texte_from_comic_bubble(img_cropped):
    # Convertir l'image PIL en tableau NumPy
    img_np = np.array(img_cropped)

    # Utiliser le tableau NumPy pour la détection de texte
    reader = easyocr.Reader(['fr'])
    result = reader.readtext(img_np)

    texte_complet = ""
    last_y = -1  # Dernière coordonnée y
    for i, detection in enumerate(result):
        text = detection[-2]  # Texte détecté
        bbox = detection[0]  # Boîte englobante (bbox)
        y = (bbox[0][1] + bbox[2][1]) / 2  # Coordonnée y du centre de la bbox
        if last_y != -1 and abs(last_y - y) > 10:  # Si la différence de coordonnées y est importante, ajouter un retour à la ligne
            texte_complet += "\n"
        if i > 0 and last_y != -1 and abs(last_y - y) <= 10:  # Ajouter un espace entre les mots de la même ligne
            texte_complet += " "
        texte_complet += text
        last_y = y
    return texte_complet.strip()  # Supprimer les espaces blancs supplémentaires en début et fin de texte


def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    if len(words)>0:
        current_line = words[0]

        for word in words[1:]:
            # Mesurer la largeur du texte actuel
            bbox = draw.textbbox((0, 0), current_line + ' ' + word, font=font)
            width = bbox[2] - bbox[0]

            # Si le texte dépasse la largeur maximale, ajouter la ligne actuelle à la liste des lignes et commencer une nouvelle ligne
            if width <= max_width:
                current_line += ' ' + word
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)  # Ajouter la dernière ligne

    return lines


def find_optimal_font_size(img_cropped, font_path, max_font_size):
    # Récupération du texte contenu dans la bulle avant le blanchiment
    text_in_bubble = get_texte_from_comic_bubble(img_cropped)

    # Créer une image PIL pour dessiner le texte
    img_pil = img_cropped.copy()
    draw = ImageDraw.Draw(img_pil)

    # Déterminer la taille de police optimale
    font_size = max_font_size
    font = ImageFont.truetype(font_path, font_size)
    text_width, text_height = draw.textsize(text_in_bubble, font=font)

    # Calculer la taille de police pour remplir toute la hauteur de l'image
    while text_height > img_cropped.size[1]:
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text_in_bubble, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    reduced_font_size = font_size - 4
    print(reduced_font_size)
    return reduced_font_size


def Change_font_page(image_path, xywh, new_image_path, font_path, font_color, background_color, max_font_size=30):
    # Chargement de l'image originale
    img_original = Image.open(image_path)

    # Déterminer la taille de police idéale à partir de la première bulle
    x, y, w, h = map(int, xywh[0].split('=')[1].split(','))
    img_cropped_first = img_original.crop((x, y, x+w, y+h))
    
    # Récupération du texte contenu dans la première bulle
    text_in_bubble_first = get_texte_from_comic_bubble(img_cropped_first)

    # Déterminer la taille de police optimale
    if text_in_bubble_first:
        optimal_font_size = find_optimal_font_size(img_cropped_first, font_path, max_font_size)
    else:
        optimal_font_size = 18 #Taille choisie arbitrairement qui fonctionne en règle générale sur la plus part des BD 

    print(optimal_font_size)

    for coords in xywh:
        # Séparation des coordonnées xywh
        x, y, w, h = map(int, coords.split('=')[1].split(','))

        # Superposition de l'image rognée sur l'image originale
        img_cropped = img_original.crop((x, y, x+w, y+h))

        # Récupération du texte contenu dans la bulle avant le blanchiment
        text_in_bubble = get_texte_from_comic_bubble(img_cropped)

        # Vérifier si du texte a été détecté
        if text_in_bubble:
            # Colorer l'image rognée
            draw = ImageDraw.Draw(img_cropped)
            draw.rectangle([(0, 0), (w, h)], fill=background_color)

            # Créer une image PIL pour dessiner le texte
            img_pil = Image.new('RGB', (w, h), color=background_color)
            draw = ImageDraw.Draw(img_pil)

            # Charger la police avec la taille optimale déterminée
            font = ImageFont.truetype(font_path, optimal_font_size)

            # Déterminer l'espacement entre les lignes
            line_spacing = optimal_font_size // 3  

            # Diviser le texte en lignes en fonction de la hauteur de l'image rognée et de l'espacement entre les lignes
            wrapped_text = wrap_text(text_in_bubble, font, w, draw)
            
            # Dessiner le texte sur l'image PIL avec l'espacement entre les lignes
            y_text = (h - optimal_font_size * len(wrapped_text) - line_spacing * (len(wrapped_text) - 1)) // 2  # Centrer le texte verticalement
            for line in wrapped_text:
                bbox = draw.textbbox((0, 0), line, font=font)
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                draw.text(((w - width) / 2, y_text), line, font=font, fill=font_color)
                y_text += height + line_spacing  # Ajouter l'espacement entre les lignes

            # Convertir l'image PIL en image numpy
            img_cropped_modified = np.array(img_pil)

            # Coller l'image rognée modifiée sur l'image d'origine à son emplacement initial
            img_original.paste(Image.fromarray(img_cropped_modified), (x, y))
        else:
            # Aucun texte détecté, laissez l'image inchangée ou ajoutez un message par défaut
            print("Aucun texte détecté dans la bulle. L'image reste inchangée.")

    # Enregistrement de la nouvelle image
    img_original.save(new_image_path)

    # Retourner le chemin vers la nouvelle image
    return new_image_path
