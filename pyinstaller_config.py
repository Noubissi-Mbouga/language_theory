# pyinstaller_config.py
import os
import sys
from pathlib import Path

def get_graphviz_files():
    """Collecte les fichiers Graphviz à inclure"""
    
    # Chercher Graphviz localement
    graphviz_paths = [
        Path("graphviz"),  # Dans le dossier du projet
        Path("C:\\Program Files\\Graphviz"),  # Installation système
        Path("C:\\Program Files (x86)\\Graphviz"),  # Alternative
    ]
    
    for graphviz_dir in graphviz_paths:
        if graphviz_dir.exists():
            print(f"Graphviz trouvé: {graphviz_dir}")
            
            # Collecter les fichiers
            files = []
            
            # Fichiers binaires
            bin_dir = graphviz_dir / "bin"
            if bin_dir.exists():
                for file in bin_dir.glob("*"):
                    if file.is_file():
                        files.append((str(file), "graphviz/bin"))
            
            # Fichiers de configuration
            etc_dir = graphviz_dir / "etc"
            if etc_dir.exists():
                for file in etc_dir.glob("**/*"):
                    if file.is_file():
                        rel_path = file.relative_to(graphviz_dir)
                        files.append((str(file), f"graphviz/{rel_path.parent}"))
            
            return files
    
    print("ATTENTION: Graphviz non trouvé localement")
    print("Téléchargez Graphviz et placez-le dans le dossier 'graphviz/'")
    return []

def build_spec():
    """Crée la spécification PyInstaller"""
    
    # Récupérer les fichiers Graphviz
    graphviz_files = get_graphviz_files()
    
    spec = {
        'name': 'GrammaireChecker',
        'input_files': ['src/interface.py', 'src/graphing.py', 'src/verifier.py'],
        'data_files': graphviz_files,
        'hidden_imports': ['graphviz', 'graphviz.backend', 'graphviz.backend.execute'],
        'options': {
            'onefile': True,
            'windowed': True,
            'icon': 'data/icon.ico' if os.path.exists('data/icon.ico') else None,
            'upx': True,
            'upx_exclude': [],
        }
    }
    
    return spec

if __name__ == "__main__":
    spec = build_spec()
    print("Configuration PyInstaller générée:")
    print(f"- Nom: {spec['name']}")
    print(f"- Fichiers Graphviz: {len(spec['data_files'])}")
