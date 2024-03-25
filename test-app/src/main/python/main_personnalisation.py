import os
import shutil
import zipfile
import ChangeFont_prog

def main(fichier_divina_path, font_choice_ID = "Arial", font_colorID = "black", background_colorID = "white"):
    try:
        # Vérifier si le fichier Divina existe
        if not os.path.exists(fichier_divina_path):
            raise FileNotFoundError("Le chemin du fichier Divina est introuvable.")

        # Extraire le nom de fichier sans l'extension
        nom_fichier_origine_sans_extension = os.path.splitext(fichier_divina_path)[0]

        # Copier le fichier Divina d'origine
        fichier_divina_copie = fichier_divina_path.replace(".divina", "_copie.divina")
        shutil.copyfile(fichier_divina_path, fichier_divina_copie)

        # Changer l'extension en .zip
        fichier_zip_copie = fichier_divina_copie.replace(".divina", ".zip")
        os.rename(fichier_divina_copie, fichier_zip_copie)

        # Définir le chemin relatif pour le dossier extrait
        nom_fichier_nouveau_sans_extension = nom_fichier_origine_sans_extension + "_copie"

        # Chemin absolu du dossier extrait
        dossier_extrait_absolu = os.path.join(os.path.dirname(os.path.dirname(fichier_divina_path)), nom_fichier_nouveau_sans_extension)

        # Décompresser le fichier .zip
        try:
            with zipfile.ZipFile(fichier_zip_copie, 'r') as zip_ref:
                zip_ref.extractall(dossier_extrait_absolu)
        except zipfile.BadZipFile:
            # Si le fichier n'est pas un fichier zip valide
            raise ValueError("Le fichier n'est pas un fichier zip valide.")

        # Supprimer le fichier zip après extraction
        os.remove(fichier_zip_copie)

        # Chemin du fichier manifest.json
        input_manifest = os.path.join(dossier_extrait_absolu, "manifest.json")
        output_manifest = input_manifest

        # Appeler le programme ChangeFont_prog
        ChangeFont_prog.main(input_manifest, output_manifest, font_choice_ID, font_colorID, background_colorID)
        newext = "_FontAdded_" + font_choice_ID
        # Renommer l'archive ZIP avec l'extension .divina
        new_divina_file_name = nom_fichier_origine_sans_extension + newext
        new_divina_file = new_divina_file_name + ".divina"     

        # Créer une archive ZIP contenant le dossier extrait et ses contenus
        shutil.make_archive(nom_fichier_nouveau_sans_extension, 'zip', dossier_extrait_absolu)
        shutil.move(nom_fichier_nouveau_sans_extension + ".zip", new_divina_file)

        # Supprimer le dossier extrait
        shutil.rmtree(dossier_extrait_absolu)

        return new_divina_file
    
    except FileNotFoundError:
        # Le chemin au fichier Divina n'existe pas
        raise FileNotFoundError("Le chemin spécifié pour le fichier Divina est invalide.")

if __name__ == "__main__":
    font_choice_ID = "Open Sans" # Helvetica Open Sans Luciole
    font_colorID = "black"
    background_colorID = "yellow"
    # test_main/ValidDivina.divina
    # test_main/TestConverter.divina
    fichier_divina_path = "Fichiers_Tests/Input/ValidDivina.divina"
    new_divina_file = main(fichier_divina_path, font_choice_ID, font_colorID, background_colorID)
    if new_divina_file:
        print("Nouveau fichier Divina:", new_divina_file)
    else:
        print("Le traitement du fichier Divina a échoué.")