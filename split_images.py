from PIL import Image
import zipfile
import shutil
import os

def split_long_images(input_folder, output_folder, page_height=1600, height_threshold=1.5):
    """
    Découpe les images trop longues en pages séparées.
    
    Args:
        input_folder: Dossier contenant les images à traiter
        output_folder: Dossier où sauvegarder les images découpées
        page_height: Hauteur cible d'une page (en pixels)
        height_threshold: Ratio minimum pour considérer une image comme "longue"
                         (ex: 1.5 = images 1.5x plus hautes que page_height)
    """
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Extensions d'images supportées
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    # Parcourir tous les fichiers du dossier
    files = sorted([f for f in os.listdir(input_folder) 
                   if f.lower().endswith(valid_extensions)])
    
    for filename in files:
        input_path = os.path.join(input_folder, filename)
        
        try:
            with Image.open(input_path) as img:
                width, height = img.size
                
                # Vérifier si l'image est trop longue
                if height > page_height * height_threshold:
                    print(f"📏 {filename} - Hauteur: {height}px - DÉCOUPAGE")
                    
                    # Calculer le nombre de pages nécessaires
                    num_pages = (height + page_height - 1) // page_height
                    
                    # Découper l'image
                    for i in range(num_pages):
                        top = i * page_height
                        bottom = min((i + 1) * page_height, height)
                        
                        # Extraire la portion
                        cropped = img.crop((0, top, width, bottom))
                        
                        # Nom du fichier de sortie
                        name, ext = os.path.splitext(filename)
                        output_filename = f"{name}_page{i+1:02d}{ext}"
                        output_path = os.path.join(output_folder, output_filename)
                        
                        # Sauvegarder
                        cropped.save(output_path, quality=95)
                    
                    print(f"   ✓ Découpé en {num_pages} pages")
                else:
                    # Image normale, copier telle quelle
                    print(f"✓ {filename} - Hauteur: {height}px - OK (copie)")
                    output_path = os.path.join(output_folder, filename)
                    img.save(output_path, quality=95)
                    
        except Exception as e:
            print(f"❌ Erreur avec {filename}: {e}")
    
    print(f"\n✅ Traitement terminé ! Résultats dans : {output_folder}")

def create_cbz_split(images_folder, cbz_base_name, max_size_mb=700):
    """
    Crée plusieurs fichiers CBZ à partir d'un dossier d'images, en les divisant
    pour ne pas dépasser une taille maximale.
    
    Args:
        images_folder: Dossier contenant les images
        cbz_base_name: Nom de base pour les CBZ (avec ou sans extension)
        max_size_mb: Taille maximale par CBZ en Mo (défaut: 700)
    """
    
    # Retirer l'extension si présente
    if cbz_base_name.endswith('.cbz'):
        cbz_base_name = cbz_base_name[:-4]
    
    # Extensions d'images supportées
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    # Récupérer et trier les images EXACTEMENT comme dans create_cbz
    images = sorted([f for f in os.listdir(images_folder) 
                    if f.lower().endswith(valid_extensions)])
    
    if not images:
        print(f"❌ Aucune image trouvée dans {images_folder}")
        return False
    
    print(f"\n📦 Création des CBZ (max {max_size_mb} Mo par fichier)")
    print(f"📸 Nombre total d'images: {len(images)}")
    
    max_size_bytes = max_size_mb * 1024 * 1024
    cbz_index = 1
    current_size = 0
    current_images = []
    created_files = []
    
    for img_file in images:
        img_path = os.path.join(images_folder, img_file)
        img_size = os.path.getsize(img_path)
        
        # Si ajouter cette image dépasse la limite ET qu'on a déjà des images
        if current_size + img_size > max_size_bytes and current_images:
            # Créer le CBZ actuel
            cbz_filename = f"{cbz_base_name}_part{cbz_index:02d}.cbz"
            _create_single_cbz(images_folder, current_images, cbz_filename)
            created_files.append(cbz_filename)
            
            # Réinitialiser pour le prochain CBZ
            cbz_index += 1
            current_size = 0
            current_images = []
        
        # Ajouter l'image au CBZ actuel
        current_images.append(img_file)
        current_size += img_size
    
    # Créer le dernier CBZ s'il reste des images
    if current_images:
        if cbz_index == 1:
            # Un seul CBZ suffit, pas besoin de numéro
            cbz_filename = f"{cbz_base_name}.cbz"
        else:
            cbz_filename = f"{cbz_base_name}_part{cbz_index:02d}.cbz"
        
        _create_single_cbz(images_folder, current_images, cbz_filename)
        created_files.append(cbz_filename)
    
    print(f"\n✅ {len(created_files)} fichier(s) CBZ créé(s) avec succès!")
    total_size_mb = sum(os.path.getsize(f) for f in created_files) / (1024 * 1024)
    print(f"📊 Taille totale: {total_size_mb:.2f} MB")
    
    return True


def _create_single_cbz(images_folder, image_list, cbz_filename):
    """
    Fonction interne pour créer un seul fichier CBZ.
    Utilise la même logique que create_cbz original.
    """
    print(f"\n📦 Création: {cbz_filename}")
    print(f"   Images: {len(image_list)}")
    
    with zipfile.ZipFile(cbz_filename, 'w', zipfile.ZIP_STORED) as cbz:
        for i, img_file in enumerate(image_list, 1):
            img_path = os.path.join(images_folder, img_file)
            
            # Renommer avec un format uniforme (00001.jpg, 00002.jpg, etc.)
            ext = os.path.splitext(img_file)[1]
            new_name = f"{i:05d}{ext}"
            
            # Ajouter l'image au CBZ
            cbz.write(img_path, new_name)
    
    size_mb = os.path.getsize(cbz_filename) / (1024 * 1024)
    print(f"   ✅ Taille: {size_mb:.2f} MB")


# UTILISATION
if __name__ == "__main__":
    # ⚙️ CONFIGURATION - Modifiez ces valeurs selon vos besoins

    manga_name = input("Nom du manga (dossier dans 'scans/'): ")

    crop = input("Veux tu crop les images ? O/N")
    if crop == "O":
        CROP_IMAGES = True
        PAGE_HEIGHT = int(input("Hauteur d'une page normale (ajustez selon votre liseuse): "))
        HEIGHT_THRESHOLD = 1.2
    else:
        CROP_IMAGES = False
        PAGE_HEIGHT = 1600
        HEIGHT_THRESHOLD = 1.2

    
    CBZ_OUTPUT = f"splitted/{manga_name}.cbz"    # Nom du fichier

    INPUT_FOLDER = f"scans/{manga_name}"      # Dossier contenant vos scans
    OUTPUT_FOLDER = f"splitted/{manga_name}"    # Dossier pour les images découpées
    
    print("🔪 Découpage automatique d'images de manga")
    print(f"📂 Dossier source: {INPUT_FOLDER}")
    print(f"📂 Dossier destination: {OUTPUT_FOLDER}")
    print(f"📏 Hauteur de page: {PAGE_HEIGHT}px")
    print(f"📐 Seuil de découpage: x{HEIGHT_THRESHOLD}\n")

    if CROP_IMAGES:
        split_long_images(INPUT_FOLDER, OUTPUT_FOLDER, PAGE_HEIGHT, HEIGHT_THRESHOLD)
        create_cbz_split(OUTPUT_FOLDER, CBZ_OUTPUT)
        shutil.rmtree(OUTPUT_FOLDER)
    else:
        os.makedirs(OUTPUT_FOLDER)
        print("⚠️ Découpage automatique désactivé.")
        print("📦 Création du CBZ sans découpage...")
        create_cbz_split(INPUT_FOLDER, CBZ_OUTPUT)

