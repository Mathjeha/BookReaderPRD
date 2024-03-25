import os
import shutil
import zipfile
import Highlight_prog
import ZoomIn_prog
import ZoomInBlack_prog

def main(fichier_divina_path, Accessibility_mode):
    # Vérifier si le fichier Divina existe
    try:
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


        if Accessibility_mode == "Highlight":
            # Appeler la fonction highlight
            Highlight_prog.main(input_manifest, output_manifest)

            # Renommer l'archive ZIP avec l'extension .divina
            new_divina_file_name = nom_fichier_origine_sans_extension + "_Highlighted"
            new_divina_file = new_divina_file_name + ".divina"

        elif Accessibility_mode == "ZoomIn":
            # Appeler la fonction zoomin
            ZoomIn_prog.main(input_manifest, output_manifest)

            # Renommer l'archive ZIP avec l'extension .divina
            new_divina_file_name = nom_fichier_origine_sans_extension + "_ZoomedIn"
            new_divina_file = new_divina_file_name + ".divina"

        elif Accessibility_mode == "ZoomInBlack":
            # Appeler la fonction zoomin
            ZoomInBlack_prog.main(input_manifest, output_manifest)

            # Renommer l'archive ZIP avec l'extension .divina
            new_divina_file_name = nom_fichier_origine_sans_extension + "_ZoomedInBlack"
            new_divina_file = new_divina_file_name + ".divina"    
        
        # Si le mode d'accessibilité n'est pas valide
        else:
            # Supprimer le dossier extrait
            shutil.rmtree(dossier_extrait_absolu)
            raise ValueError("Le mode d'accessibilité spécifié est invalide.")

        # Créer une archive ZIP contenant le dossier extrait et ses contenus
        shutil.make_archive(nom_fichier_nouveau_sans_extension, 'zip', dossier_extrait_absolu)

        shutil.move(nom_fichier_nouveau_sans_extension + ".zip", new_divina_file)

        # Supprimer le dossier extrait
        shutil.rmtree(dossier_extrait_absolu)

        return new_divina_file
        
    except FileNotFoundError:
        # Le chemin au fichier Divina n'existe pas
        raise FileNotFoundError("Le chemin spécifié pour le fichier Divina est invalide.")
''' 
if __name__ == "__main__":
    Accessibility_mode = "ZoomInBlack"
    # Fichiers_Tests/exception_test/TestConverter.divina
    # Fichiers_Tests/exception_test/ValidDivina.divina
    fichier_divina_path = "Fichiers_Tests/exception_test/ValidDifdvina.divina"
    new_divina_file = main(fichier_divina_path, Accessibility_mode)
    print("Nouveau fichier Divina:", new_divina_file)
'''
