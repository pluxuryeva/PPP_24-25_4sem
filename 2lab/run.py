import os
import sys
import subprocess
import platform

def main():
    # Определяем путь к директории 2lab
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lab_dir = os.path.join(current_dir, "2lab")
    
    # Проверяем, что директория существует
    if not os.path.isdir(lab_dir):
        print(f"Ошибка: Директория {lab_dir} не найдена")
        sys.exit(1)
    
    # Определяем команду для запуска в зависимости от ОС
    if platform.system() == "Windows":
        command = f"python {os.path.join(lab_dir, 'main.py')}"
    else:
        command = f"python3 {os.path.join(lab_dir, 'main.py')}"
    
    # Запускаем приложение
    print(f"Запуск приложения: {command}")
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    main() 