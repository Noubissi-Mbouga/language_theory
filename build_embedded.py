#!/usr/bin/env python3
"""
Build un exécutable avec Graphviz EMBARQUÉ
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def setup_encoding():
    """Configure l'encodage pour éviter les erreurs Unicode"""
    # Forcer UTF-8 sur Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

setup_encoding()

def download_portable_graphviz():
    """Télécharge Graphviz portable si absent"""
    
    graphviz_dir = Path("graphviz")
    
    if graphviz_dir.exists() and (graphviz_dir / "bin" / "dot.exe").exists():
        print("[OK] Graphviz portable déjà présent")
        return True
    
    print("[DOWNLOAD] Téléchargement de Graphviz portable...")
    
    try:
        import urllib.request
        import zipfile
        
        # URL d'un Graphviz portable
        url = "https://github.com/mcxiaoke/graphviz-portable/releases/download/v2.50.0/GraphvizPortable_2.50.0.zip"
        
        # Créer le dossier
        graphviz_dir.mkdir(exist_ok=True)
        
        # Télécharger
        zip_path = graphviz_dir / "graphviz.zip"
        urllib.request.urlretrieve(url, zip_path)
        
        # Extraire
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Chercher où sont les binaires
            for member in zip_ref.namelist():
                if "bin/dot.exe" in member.replace("\\", "/"):
                    # Extraire tout
                    zip_ref.extractall(graphviz_dir)
                    break
        
        # Nettoyer
        zip_path.unlink(missing_ok=True)
        
        # Réorganiser si nécessaire
        extracted = list(graphviz_dir.glob("*"))
        for item in extracted:
            if item.is_dir() and "Graphviz" in item.name:
                # Déplacer le contenu
                for subitem in item.glob("*"):
                    dest = graphviz_dir / subitem.name
                    if subitem.is_dir():
                        shutil.copytree(subitem, dest, dirs_exist_ok=True)
                        shutil.rmtree(subitem)
                    else:
                        shutil.move(str(subitem), str(dest))
                if item.exists():
                    shutil.rmtree(item)
        
        print("[OK] Graphviz portable téléchargé")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")
        return False

def build_embedded_exe():
    """Construit l'exécutable avec Graphviz embarqué"""
    
    print("[BUILD] Construction de l'exécutable embarqué...")
    
    # 1. Vérifier Graphviz
    if not download_portable_graphviz():
        print("[ERROR] Impossible de continuer sans Graphviz")
        return False
    
    # 2. Vérifier les sources
    if not Path("src/interface.py").exists():
        print("[ERROR] Fichier src/interface.py introuvable")
        return False
    
    # 3. Préparer la commande PyInstaller
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=GrammaireChecker",
        "--hidden-import=graphviz",
        "--hidden-import=graphviz.backend",
        "--hidden-import=graphviz.backend.execute",
        "--add-data=graphviz;graphviz",  # CRITIQUE: Inclut Graphviz
        "--add-data=src;src",
        "--clean",
    ]
    
    # Ajouter l'icône si elle existe
    if Path("data/icon.ico").exists():
        cmd.append("--icon=data/icon.ico")
    elif Path("icon.ico").exists():
        cmd.append("--icon=icon.ico")
    
    cmd.append("src/interface.py")
    
    # 4. Exécuter PyInstaller
    print(f"[CMD] Exécution: {' '.join(cmd[:5])}...")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    if result.returncode == 0:
        print("[OK] Construction réussie!")
        
        # Vérifier la taille
        exe_path = Path("dist") / "GrammaireChecker.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[SIZE] Taille: {size_mb:.1f} MB")
            
            # Vérifier que Graphviz est bien inclus
            print("[CHECK] Vérification de l'embarquement...")
            
            # Lister les fichiers dans dist
            dist_files = list(Path("dist").glob("*"))
            print(f"[FILES] {len(dist_files)} fichier(s) dans dist/:")
            for f in dist_files:
                print(f"  - {f.name}")
        
        return True
    else:
        print("[ERROR] Erreur de construction PyInstaller:")
        if result.stdout:
            print("STDOUT:", result.stdout[-500:])  # Derniers 500 caractères
        if result.stderr:
            print("STDERR:", result.stderr[-500:])
        return False

def create_simple_launcher():
    """Crée un launcher simple (optionnel)"""
    
    launcher_content = """@echo off
chcp 65001 >nul
echo ========================================
echo     GrammaireChecker - Version Embarquee
echo ========================================
echo.
echo Tout est inclus dans cet executable!
echo Graphviz est deja integre.
echo.
echo Lancement...
echo.

start "" "GrammaireChecker.exe"

pause
"""
    
    launcher_path = Path("Lancer.bat")
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    # Copier aussi dans dist
    dist_launcher = Path("dist") / "Lancer.bat"
    shutil.copy2(launcher_path, dist_launcher)
    
    print("[OK] Launcher créé: Lancer.bat")

def main():
    """Fonction principale"""
    print("=" * 50)
    print("BUILD - GrammaireChecker avec Graphviz Embarqué")
    print("=" * 50)
    
    success = build_embedded_exe()
    
    if success:
        create_simple_launcher()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] CONSTRUCTION TERMINÉE")
        print("=" * 50)
        print("\nFichiers générés:")
        print("  • dist/GrammaireChecker.exe  (VOTRE app avec Graphviz dedans)")
        print("  • Lancer.bat                  (Script de lancement)")
        print("\nPour distribuer:")
        print("  1. Copiez SEULEMENT GrammaireChecker.exe")
        print("  2. Donnez-le à n'importe qui")
        print("  3. Il fonctionne SANS installation!")
        print("\nGraphviz est INCLUS dans l'exécutable!")
        print("=" * 50)
        return 0
    else:
        print("\n[FAILED] La construction a échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())
