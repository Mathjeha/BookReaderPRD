import json
import os
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont

def add_accessibility_banner(image_path, output_path):
    # Charger l'image
    img = Image.open(image_path)
    width, height = img.size
    
    # Définir la couleur et la taille de la bande verte
    banner_height = height // 6
    banner_color = (0, 128, 0)  # Vert
    banner_top = height - banner_height
    
    # Créer une nouvelle image avec la bande verte
    banner = Image.new('RGB', (width, banner_height), banner_color)
    img.paste(banner, (0, banner_top))
    
    # Ajouter du texte "Accessibilité" au centre de la bande verte
    draw = ImageDraw.Draw(img)
    font_size = 154  # Taille de la police
    font = ImageFont.truetype("arial.ttf", font_size)  # Charger une police TrueType avec la taille spécifiée
    
    # Mesurer la taille du texte "Accessibilité:"
    text_accessibility = "Accessibilité:"
    text_width_accessibility, text_height_accessibility = draw.textsize(text_accessibility, font=font)
    
    # Mesurer la taille du texte "Agrandissement"
    text_isolated_enlargement = "Agrandissement"
    text_width_isolated_enlargement, text_height_isolated_enlargement = draw.textsize(text_isolated_enlargement, font=font)
    
    # Calculer les positions horizontales pour centrer les textes
    text_position_accessibility = ((width - text_width_accessibility) // 2, height - banner_height + (banner_height - text_height_accessibility - text_height_isolated_enlargement) // 2)
    text_position_isolated_enlargement = ((width - text_width_isolated_enlargement) // 2, text_position_accessibility[1] + text_height_accessibility)
    
    # Dessiner les textes
    draw.text(text_position_accessibility, text_accessibility, fill=(255, 255, 255), font=font)
    draw.text(text_position_isolated_enlargement, text_isolated_enlargement, fill=(255, 255, 255), font=font)

    # Enregistrer l'image modifiée
    img.save(output_path)

def crop_and_overlay(image_path, xywh, new_image_path, zoom_factor):
    # Séparation des coordonnées xywh
    xywh = xywh.split('=')[1]
    x, y, w, h = map(int, xywh.split(','))
    
    # Chargement de l'image originale
    img_original = Image.open(image_path)
    
    # Rogner l'image originale pour la flouter
    img_blurred = img_original.copy()
    # Appliquer un filtre pour assombrir légèrement l'image de fond
    img_blurred = img_blurred.filter(ImageFilter.GaussianBlur(radius=10))
    img_blurred = ImageEnhance.Brightness(img_blurred).enhance(0.8)  # Diminuer la luminosité de 20%
    
    # Redimensionner l'image rognée avec le facteur de zoom
    cropped_width = int(w * zoom_factor)
    cropped_height = int(h * zoom_factor)

    # Vérifier si l'image rognée grossie dépasse les dimensions de l'image de fond
    if cropped_width > img_blurred.width:
        ratio = img_blurred.width / cropped_width
        cropped_width = img_blurred.width
        cropped_height = int(cropped_height * ratio)

    if cropped_height > img_blurred.height:
        ratio = img_blurred.height / cropped_height
        cropped_height = img_blurred.height
        cropped_width = int(cropped_width * ratio)
    
    img_cropped = img_original.crop((x, y, x+w, y+h))
    img_cropped = img_cropped.resize((cropped_width, cropped_height))
    
    # Calculer les coordonnées de la position où coller l'image rognée au centre de l'image de fond
    center_x = (img_blurred.width - cropped_width) // 2
    center_y = (img_blurred.height - cropped_height) // 2
    
    # Superposition de l'image rognée sur l'image floutée au centre de l'image de fond
    img_blurred.paste(img_cropped, (center_x, center_y))
    
    # Enregistrement de la nouvelle image superposée
    img_blurred.save(new_image_path)

    # Retourner le chemin de la nouvelle image et les dimensions de l'image rognée redimensionnée
    return new_image_path, cropped_width, cropped_height


def build_new_manifest(manifest, manifest_path_input):
    # Initialiser une liste pour maintenir l'ordre dans le readingOrder
    toc_order = []

    # Initialiser le readingOrder
    reading_order = []

    # récupération du chemin à la racine du dossier ou se trouve le fichier divina
    manifest_directory_path = os.path.dirname(os.path.abspath(manifest_path_input))
    manifest_directory_path_with_separator = os.path.join(manifest_directory_path, '')

    # Extraire le chemin du dossier contenant les images des pages
    image_folder_path = os.path.dirname(manifest["toc"][0]["href"])

    # Fonction récursive pour traiter les enfants de manière récursive
    def process_children(parent_item):
        for child in parent_item.get("children", []):
            # Vérifier si le titre de l'enfant contient "case", "Case", "vignette" ou "Vignette"
            if any(keyword.lower() in child["title"].lower() for keyword in ["case", "vignette"]):
                # Extraire le chemin de l'image parente sans les coordonnées de rognage
                parent_image_path_abs = os.path.join(manifest_directory_path, parent_item["href"].split('#')[0])
                parent_image_path_simp = parent_item["href"].split('#')[0]
                # Extraire les informations de rognage
                xywh = child["href"].split("#")[1]
                # Générer le nom de la nouvelle image
                new_image_path_simp = f"{parent_image_path_simp.split('.')[0]}_{child['title']}.jpg"
                # Générer le chemin d'enregistrement
                new_image_path_abs = os.path.join(manifest_directory_path, f"{parent_image_path_simp.split('.')[0]}_{child['title']}.jpg")
                # Rogner l'image et superposer, puis récupérer la largeur et la hauteur
                new_image_path_abs, width, height = crop_and_overlay(parent_image_path_abs, xywh, new_image_path_abs, zoom_factor=2)  # Changer le facteur de zoom comme souhaité
                # Mettre à jour le lien dans la section "children"
                child["href"] = new_image_path_simp
                # Ajouter la page rognée dans le readingOrder
                reading_order.append({
                    "href": new_image_path_simp,
                    "type": "image/jpeg",
                    "height": height,
                    "width": width,
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
            # Appel récursif pour traiter les enfants des enfants
            process_children(child)

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

def main(manifest_path_input, manifest_path_output):
    # Charger le fichier manifest.json
    with open(manifest_path_input, "r", encoding="utf-8") as file:
        manifest = json.load(file)

    reading_order, toc_order, image_folder_path = build_new_manifest(manifest, manifest_path_input)

    manifest["readingOrder"] = reading_order

    # Enregistrer les modifications dans le manifest.json sans l'encodage ASCII
    with open(manifest_path_output, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4, ensure_ascii=False)
    
    # on renvoie le chemin contenant les images modifié
    return image_folder_path

''' 
if __name__ == "__main__":

    manifest_path_input = "Fichiers_Tests/Input/manifestValide.json"
    manifest_path_output = "Fichiers_Tests/Input/manifestbon.json"
    main(manifest_path_input, manifest_path_output)
'''