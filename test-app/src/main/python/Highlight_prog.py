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
    
    # Mesurer la taille du texte "Surbrillance"
    text_isolated_enlargement = "Surbrillance"
    text_width_isolated_enlargement, text_height_isolated_enlargement = draw.textsize(text_isolated_enlargement, font=font)
    
    # Calculer les positions horizontales pour centrer les textes
    text_position_accessibility = ((width - text_width_accessibility) // 2, height - banner_height + (banner_height - text_height_accessibility - text_height_isolated_enlargement) // 2)
    text_position_isolated_enlargement = ((width - text_width_isolated_enlargement) // 2, text_position_accessibility[1] + text_height_accessibility)
    
    # Dessiner les textes
    draw.text(text_position_accessibility, text_accessibility, fill=(255, 255, 255), font=font)
    draw.text(text_position_isolated_enlargement, text_isolated_enlargement, fill=(255, 255, 255), font=font)

    # Enregistrer l'image modifiée
    img.save(output_path)


def Highligh_page(image_path, xywh, new_image_path):
    # Séparation des coordonnées xywh
    xywh = xywh.split('=')[1]
    x, y, w, h = map(int, xywh.split(','))
    
    # Chargement de l'image originale
    img_original = Image.open(image_path)
    
    # Rogner l'image originale pour la flouter
    img_blurred = img_original.copy()
    img_blurred = img_blurred.filter(ImageFilter.GaussianBlur(radius=7))
    img_blurred = ImageEnhance.Brightness(img_blurred).enhance(0.6)  # Diminuer la luminosité de 20%
    
    # Créer un objet ImageDraw pour dessiner sur l'image
    draw = ImageDraw.Draw(img_blurred)
    
    # Dessiner un rectangle autour de la zone rognée pour mettre en surbrillance les contours
    draw.rectangle([x, y, x+w, y+h], outline="cyan", width=30)
    
    # Superposition de l'image rognée sur l'image floutée
    img_cropped = img_original.crop((x, y, x+w, y+h))
    img_blurred.paste(img_cropped, (x, y))
    
    # Enregistrement de la nouvelle image superposée
    img_blurred.save(new_image_path)

    # Retourner la largeur et la hauteur de l'image rognée
    return new_image_path, w, h


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

    def process_children(parent_item):
        # Extraire le chemin de l'image parente
        parent_image_path_abs = os.path.join(manifest_directory_path, parent_item["href"].split('#')[0])
        parent_image_path_simp = parent_item["href"].split('#')[0]
        
        for child in parent_item.get("children", []):
            # Extraire les informations de rognage
            xywh = child["href"].split("#")[1] # xywh sera sous ce format: 'xywh=x,y,w,h'
            # Générer le nom de la nouvelle image enfant
            new_image_path_simp = f"{parent_image_path_simp.split('.')[0]}_{child['title']}.jpg"
            # Générer le chemin d'enregistrement
            new_image_path_abs = os.path.join(manifest_directory_path, f"{parent_image_path_simp.split('.')[0]}_{child['title']}.jpg")
            
            # Si l'enfant a des enfants, utilisez récursivement process_children
            if "children" in child:
                process_children(child)
            
            # Rogner l'image et superposer, puis récupérer la largeur et la hauteur
            new_image_path_abs, width, height = Highligh_page(parent_image_path_abs, xywh, new_image_path_abs) 
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

    return image_folder_path

'''
if __name__ == "__main__":
    manifest_path_input = "test_main/divina_valide_copie/manifest.json"
    manifest_path_output = "test_main/divina_valide_copie/manifestbon.json"
    main(manifest_path_input, manifest_path_output)
'''
