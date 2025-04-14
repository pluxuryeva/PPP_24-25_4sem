import os
import sys
import subprocess

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lab_dir = os.path.join(current_dir, "2lab")
    
    if not os.path.exists(lab_dir):
        print(f"Ошибка: директория {lab_dir} не найдена")
        return
    
    os.chdir(lab_dir)
    
    python_cmd = "python3" if sys.platform != "win32" else "python"
    cmd = [python_cmd, "main.py"]
    
    print(f"Запуск {' '.join(cmd)} в директории {lab_dir}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

