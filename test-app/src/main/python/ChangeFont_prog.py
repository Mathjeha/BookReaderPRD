import json
import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import ChangeFont

def add_accessibility_banner(image_path, output_path):
    # Charger l'image
    img = Image.open(image_path)
    width, height = img.size
    
    # Définir la couleur et la taille de la bande verte
    banner_height = height // 6
    banner_color = (0, 0, 255) # Bleu
    banner_top = height - banner_height
    
    # Créer une nouvelle image avec la bande verte
    banner = Image.new('RGB', (width, banner_height), banner_color)
    img.paste(banner, (0, banner_top))
    
    # Ajouter du texte "Personnalisation" au centre de la bande verte
    draw = ImageDraw.Draw(img)
    font_size = 154  # Taille de la police
    font = ImageFont.truetype("arial.ttf", font_size)  # Charger une police TrueType avec la taille spécifiée
    
    # Mesurer la taille du texte "Personnalisation:"
    text_accessibility = "Personnalisation:"
    text_bbox_accessibility = draw.textbbox((0, 0), text_accessibility, font=font)
    text_width_accessibility = text_bbox_accessibility[2] - text_bbox_accessibility[0]
    text_height_accessibility = text_bbox_accessibility[3] - text_bbox_accessibility[1]
    
    # Mesurer la taille du texte "Police d'écriture"
    text_isolated_enlargement = "Police d'écriture"
    text_bbox_isolated_enlargement = draw.textbbox((0, 0), text_isolated_enlargement, font=font)
    text_width_isolated_enlargement = text_bbox_isolated_enlargement[2] - text_bbox_isolated_enlargement[0]
    text_height_isolated_enlargement = text_bbox_isolated_enlargement[3] - text_bbox_isolated_enlargement[1]
    
    # Calculer les positions horizontales pour centrer les textes
    text_position_accessibility = ((width - text_width_accessibility) // 2, height - banner_height + (banner_height - text_height_accessibility - text_height_isolated_enlargement) // 2)
    text_position_isolated_enlargement = ((width - text_width_isolated_enlargement) // 2, text_position_accessibility[1] + text_height_accessibility)
    
    # Dessiner les textes
    draw.text(text_position_accessibility, text_accessibility, fill=(255, 255, 255), font=font)
    draw.text(text_position_isolated_enlargement, text_isolated_enlargement, fill=(255, 255, 255), font=font)

    # Enregistrer l'image modifiée
    img.save(output_path)

def get_font_filename(font_choice_ID):
    if font_choice_ID == "Arial":
        font_choice = "arial.ttf"
    elif font_choice_ID == "Helvetica":
        font_choice = "helvetica.ttf"
    elif font_choice_ID == "Calibri":
        font_choice = "calibri.ttf"
    elif font_choice_ID == "Verdana":
        font_choice = "verdana.ttf"
    elif font_choice_ID == "Tahoma":
        font_choice = "tahoma.ttf"
    elif font_choice_ID == "Open Sans":
        font_choice = "opensans.ttf"
    elif font_choice_ID == "Luciole":
        font_choice = "Luciole-Regular.ttf"
    else:
        # Par défaut, utiliser Arial
        font_choice = "arial.ttf"
    return font_choice

def get_font_color(font_colorID):
    if font_colorID == "blue":
        font_color = (0, 0, 255)
    elif font_colorID == "yellow":
        font_color = (255, 255, 0)
    elif font_colorID == "red":
        font_color = (255, 0, 0)
    elif font_colorID == "green":
        font_color = (0, 128, 0)
    elif font_colorID == "purple":
        font_color = (128, 0, 128)
    elif font_colorID == "orange":
        font_color = (255, 165, 0)
    elif font_colorID == "pink":
        font_color = (255, 192, 203)
    elif font_colorID == "turquoise":
        font_color = (64, 224, 208)
    elif font_colorID == "brown":
        font_color = (165, 42, 42)
    elif font_colorID == "cyan":
        font_color = (0, 255, 255)
    elif font_colorID == "magenta":
        font_color = (255, 0, 255)
    elif font_colorID == "gold":
        font_color = (255, 215, 0)
    elif font_colorID == "silver":
        font_color = (192, 192, 192)
    elif font_colorID == "maroon":
        font_color = (128, 0, 0)
    elif font_colorID == "navy":
        font_color = (0, 0, 128)
    elif font_colorID == "black":
        font_color = (0, 0, 0)
    elif font_colorID == "white":
        font_color = (255, 255, 255)
    else:
        # Par défaut, utiliser noir
        font_color = (0, 0, 0)
    return font_color

def get_background_color(background_colorID):
    if background_colorID == "blue":
        background_color = (0, 0, 255)
    elif background_colorID == "yellow":
        background_color = (255, 255, 0)
    elif background_colorID == "red":
        background_color = (255, 0, 0)
    elif background_colorID == "green":
        background_color = (0, 128, 0)
    elif background_colorID == "purple":
        background_color = (128, 0, 128)
    elif background_colorID == "orange":
        background_color = (255, 165, 0)
    elif background_colorID == "pink":
        background_color = (255, 192, 203)
    elif background_colorID == "turquoise":
        background_color = (64, 224, 208)
    elif background_colorID == "brown":
        background_color = (165, 42, 42)
    elif background_colorID == "cyan":
        background_color = (0, 255, 255)
    elif background_colorID == "magenta":
        background_color = (255, 0, 255)
    elif background_colorID == "gold":
        background_color = (255, 215, 0)
    elif background_colorID == "silver":
        background_color = (192, 192, 192)
    elif background_colorID == "maroon":
        background_color = (128, 0, 0)
    elif background_colorID == "navy":
        background_color = (0, 0, 128)
    elif background_colorID == "black":
        background_color = (0, 0, 0)
    elif background_colorID == "white":
        background_color = (255, 255, 255)
    else:
        # Par défaut, utiliser blanc
        background_color = (255, 255, 255)
    return background_color

def build_new_manifest(manifest, manifest_path_input, font_choice_ID, font_colorID, background_colorID):
    
    # Récupération de la police d'écriture
    font_choice = get_font_filename(font_choice_ID)
    # Récupération de la couleur d'écriture
    font_color = get_font_color(font_colorID)
    # Récupération de la couleur de fond de la bulle
    background_color = get_background_color(background_colorID)

    # Initialiser une liste pour maintenir l'ordre dans le readingOrder
    toc_order = []

    # Initialiser le readingOrder
    reading_order = []

    # récupération du chemin à la racine du dossier ou se trouve le fichier divina
    manifest_directory_path = os.path.dirname(os.path.abspath(manifest_path_input))
    manifest_directory_path_with_separator = os.path.join(manifest_directory_path, '')

    # Extraire le chemin du dossier contenant les images des pages
    image_folder_path = os.path.dirname(manifest["toc"][0]["href"])

    def process_children(parent_item):
        # Extraire le chemin de l'image parente
        parent_image_path_abs = os.path.join(manifest_directory_path, parent_item["href"].split('#')[0])
        parent_image_path_simp = parent_item["href"].split('#')[0]

        xywh_list = []  # Liste pour stocker les bounding boxes

        for child in parent_item.get("children", []):
            # Vérifier si le titre de l'enfant contient "bulle" ou "bubble"
            if "bulle" in child["title"].lower() or "bubble" in child["title"].lower():
                # Ajouter les bounding boxes à la liste xywh
                xywh_list.append(child["href"].split("#")[1])

            # Si l'enfant a des enfants, utilisez récursivement process_children
            if "children" in child:
                process_children(child)

        # Si la liste xywh n'est pas vide, procéder à la modification de l'image
        if xywh_list:
            # CHanger la police des bulles dans la page parente
            ChangeFont.Change_font_page(parent_image_path_abs, xywh_list, parent_image_path_abs, font_choice, font_color, background_color)

    # Parcourir la section "toc"
    for item in manifest["toc"]:
        # Ajouter l'élément à la liste d'ordre du toc
        toc_order.append(item["href"])
        # Vérifier si l'élément a des enfants
        if "children" in item:
            # Vérifier si l'élément contient "rel": "cover"
            if item["title"].lower() == "cover":
                # Appliquer add_accessibility_banner à l'image de la couverture
                cover_image_path = os.path.join(manifest_directory_path, item["href"])
                add_accessibility_banner(cover_image_path, cover_image_path)  # Met à jour directement l'image de couverture
                # Utiliser l'image de la couverture mise à jour dans le readingOrder
                reading_order.append({
                    "rel": "cover",
                    "href": item["href"],
                    "type": "image/jpeg",
                    # Remplacer par les dimensions réelles de l'image simple si elles sont disponibles
                    "height": 2501,
                    "width": 1958,
                    "transitions": {
                        "forward": {
                            "type": "slide-in",
                            "direction": "rtl",
                            "duration": 500
                        },
                        "backward": {
                            "type": "slide-out",
                            "direction": "ltr",
                            "duration": 500
                        }
                    }
                })
            else:
                # Ajouter la page parente dans le readingOrder avant de traiter les enfants
                reading_order.append({
                    "href": item["href"],
                    "type": "image/jpeg",
                    "height": 2501,
                    "width": 1958,
                    "transitions": {
                        "forward": {
                            "type": "slide-in",
                            "direction": "rtl",
                            "duration": 500
                        },
                        "backward": {
                            "type": "slide-out",
                            "direction": "ltr",
                            "duration": 500
                        }
                    }
                })
            process_children(item)
        else:
            # Si l'élément n'a pas d'enfants, l'ajouter directement au readingOrder
            # Vérifier si l'élément contient "rel": "cover"
            if item["title"].lower() == "cover":
                # Appliquer add_accessibility_banner à l'image de la couverture
                cover_image_path = os.path.join(manifest_directory_path, item["href"])
                add_accessibility_banner(cover_image_path, cover_image_path)  # Met à jour directement l'image de couverture
                # Utiliser l'image de la couverture mise à jour dans le readingOrder
                reading_order.append({
                    "rel": "cover",
                    "href": item["href"],
                    "type": "image/jpeg",
                    # Remplacer par les dimensions réelles de l'image simple si elles sont disponibles
                    "height": 2501,
                    "width": 1958,
                    "transitions": {
                        "forward": {
                            "type": "slide-in",
                            "direction": "rtl",
                            "duration": 500
                        },
                        "backward": {
                            "type": "slide-out",
                            "direction": "ltr",
                            "duration": 500
                        }
                    }
                })
            else: 
                reading_order.append({
                    "href": item["href"],
                    "type": "image/jpeg",
                    "height": 2501,
                    "width": 1958,
                    "transitions": {
                        "forward": {
                            "type": "slide-in",
                            "direction": "rtl",
                            "duration": 500
                        },
                        "backward": {
                            "type": "slide-out",
                            "direction": "ltr",
                            "duration": 500
                        }
                    }
                })

    return reading_order, toc_order, image_folder_path

def main(manifest_path_input, manifest_path_output, font_choice_ID, font_colorID, background_colorID):
    # Charger le fichier manifest.json
    with open(manifest_path_input, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    reading_order, toc_order, image_folder_path = build_new_manifest(manifest, manifest_path_input, font_choice_ID, font_colorID, background_colorID)

    manifest["readingOrder"] = reading_order

    # Enregistrer les modifications dans le manifest.json sans l'encodage ASCII
    with open(manifest_path_output, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4, ensure_ascii=False)

    return image_folder_path

 
if __name__ == "__main__":
    manifest_path_input = "test_main/divina_valide_copie/manifest.json"
    manifest_path_output = "test_main/divina_valide_copie/manifestbon.json"
    font_choice_ID = "Arial"
    font_colorID = "green"
    background_colorID = "blue"
    main(manifest_path_input, manifest_path_output, font_choice_ID, font_colorID, background_colorID)
