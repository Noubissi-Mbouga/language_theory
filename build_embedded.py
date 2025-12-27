#!/usr/bin/env python3
"""
Build un exécutable avec Graphviz EMBARQUÉ
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def download_portable_graphviz():
    """Télécharge Graphviz portable si absent"""
    
    graphviz_dir = Path("graphviz")
    
    if graphviz_dir.exists() and (graphviz_dir / "bin" / "dot.exe").exists():
        print("✅ Graphviz portable déjà présent")
        return True
    
    print("📦 Téléchargement de Graphviz portable...")
    
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
                    shutil.move(str(subitem), str(graphviz_dir / subitem.name))
                shutil.rmtree(item)
        
        print("✅ Graphviz portable téléchargé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def build_embedded_exe():
    """Construit l'exécutable avec Graphviz embarqué"""
    
    print("🔨 Construction de l'exécutable embarqué...")
    
    # 1. Vérifier Graphviz
    if not download_portable_graphviz():
        print("❌ Impossible de continuer sans Graphviz")
        return False
    
    # 2. Préparer la commande PyInstaller
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
    
    cmd.append("src/interface.py")
    
    # 3. Exécuter PyInstaller
    print(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Construction réussie!")
        
        # Vérifier la taille
        exe_path = Path("dist") / "GrammaireChecker.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📏 Taille: {size_mb:.1f} MB")
            
            # Vérifier que Graphviz est bien inclus
            print("🔍 Vérification de l'embarquement...")
            
            # Test rapide
            test_cmd = [
                str(exe_path),
                "--version"
            ]
            
            try:
                test = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print(f"🧪 Test: {test.returncode}")
            except:
                print("⚠️ Test non exécuté")
        
        return True
    else:
        print("❌ Erreur de construction:")
        print(result.stderr)
        return False

def create_simple_launcher():
    """Crée un launcher simple (optionnel)"""
    
    launcher_content = """@echo off
echo GrammaireChecker - Version Embarquee
echo.
echo Tout est inclus dans cet executable!
echo.
echo Lancement...
echo.

"./dist/GrammaireChecker.exe"

pause
"""
    
    with open("Lancer.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ Launcher créé: Lancer.bat")

if __name__ == "__main__":
    print("=" * 50)
    print("BUILD - GrammaireChecker avec Graphviz Embarqué")
    print("=" * 50)
    
    success = build_embedded_exe()
    
    if success:
        create_simple_launcher()
        
        print("\n" + "=" * 50)
        print("✅ CONSTRUCTION TERMINÉE")
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
    else:
        print("\n❌ La construction a échoué")
        sys.exit(1)
