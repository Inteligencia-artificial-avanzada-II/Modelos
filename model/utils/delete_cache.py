import os
import shutil

def delete_pycache(directory="."):
    for root, dirs, files in os.walk(directory):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Eliminado: {pycache_path}")