import subprocess
import sys

def install_requirements():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", 'requirements.txt'])
        print("\033[1m\033[32mAll packages installed successfully!\033[0m")
    except subprocess.CalledProcessError as e:
        print("\033[1m\033[31mError installing packages:\033[0m", e)