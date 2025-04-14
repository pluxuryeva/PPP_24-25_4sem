import os
import socket
import threading
import subprocess
import json
import time
import logging
import signal
import sys
from datetime import datetime

# Константы
DATA_FILE = 'programs_data.json'
OUTPUT_DIR = 'programs_output'
INTERVAL = 10  # Интервал запуска программ по умолчанию (в секундах)
HOST = 'localhost'
PORT = 5555

# Глобальные переменные
program_threads = {}  # Словарь для хранения потоков и событий остановки

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    filename='server.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

def load_programs():
    """Загрузка данных о программах из JSON-файла."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Ошибка при загрузке данных: {e}")
            return {"interval": INTERVAL, "programs": {}}
    return {"interval": INTERVAL, "programs": {}}

def save_programs(programs_data):
    """Сохранение данных о программах в JSON-файл."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(programs_data, f, indent=4)
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных: {e}")

def run_program(program_name, stop_event, interval):
    """Циклический запуск программы с записью вывода в файл."""
    folder = os.path.join(OUTPUT_DIR, program_name)
    os.makedirs(folder, exist_ok=True)
    
    logging.info(f"Запуск программы: {program_name} с интервалом {interval} сек.")
    
    while not stop_event.is_set():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(folder, f'run_{timestamp}.txt')
        
        try:
            # Запуск программы и перехват вывода
            result = subprocess.run(
                program_name, 
                shell=True, 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=interval  # Ограничиваем время выполнения интервалом
            )
            
            # Запись вывода в файл
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
                
            logging.info(f"Программа {program_name} выполнена, вывод сохранен в {output_file}")
        
        except subprocess.TimeoutExpired:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"ОШИБКА: Превышено время выполнения ({interval} сек)\n")
            logging.warning(f"Программа {program_name} превысила время выполнения")
        
        except Exception as e:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"ОШИБКА: {str(e)}\n")
            logging.error(f"Ошибка при выполнении программы {program_name}: {e}")
        
        # Ожидание перед следующим запуском
        for _ in range(interval):
            if stop_event.is_set():
                break
            time.sleep(1)

def start_programs(programs_data):
    """Запуск всех активных программ из загруженных данных."""
    interval = programs_data.get('interval', INTERVAL)
    for prog, info in programs_data.get('programs', {}).items():
        if info.get('active', True):
            stop_event = threading.Event()
            thread = threading.Thread(
                target=run_program, 
                args=(prog, stop_event, interval), 
                daemon=True
            )
            program_threads[prog] = {'thread': thread, 'event': stop_event}
            thread.start()
            logging.info(f"Поток для программы {prog} запущен")

def get_combined_output(program):
    """Формирование объединенного вывода всех запусков программы."""
    folder = os.path.join(OUTPUT_DIR, program)
    if not os.path.exists(folder):
        return f"Вывод для программы {program} не найден"
    
    outputs = sorted(os.listdir(folder))
    if not outputs:
        return f"Нет данных о запусках программы {program}"
    
    combined_output = f"===== Объединенный вывод для программы {program} =====\n\n"
    
    for file in outputs:
        try:
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                combined_output += f"\n===== {file} =====\n{f.read()}\n"
        except Exception as e:
            combined_output += f"\n===== {file} =====\nОшибка чтения файла: {e}\n"
    
    return combined_output

def handle_client(conn, addr, programs_data):
    """Обработка запросов от клиента."""
    logging.info(f"Подключение от {addr}")
    
    try:
        # Получение данных от клиента
        data = conn.recv(8192).decode('utf-8')
        if not data:
            conn.close()
            return
            
        try:
            request = json.loads(data)
        except json.JSONDecodeError:
            conn.sendall("Ошибка: некорректный формат запроса".encode('utf-8'))
            conn.close()
            return
            
        action = request.get('action')
        program = request.get('program')
        
        response = "Неизвестная команда"
        
        # Обработка команды добавления программы
        if action == 'add' and program:
            if program not in programs_data['programs']:
                programs_data['programs'][program] = {'active': True}
                save_programs(programs_data)
                
                # Запуск программы в отдельном потоке
                stop_event = threading.Event()
                thread = threading.Thread(
                    target=run_program, 
                    args=(program, stop_event, programs_data.get('interval', INTERVAL)), 
                    daemon=True
                )
                program_threads[program] = {'thread': thread, 'event': stop_event}
                thread.start()
                
                response = f"Программа {program} добавлена и запущена"
                logging.info(response)
            else:
                response = f"Программа {program} уже существует"
        
        # Обработка команды получения вывода программы
        elif action == 'get_output' and program:
            response = get_combined_output(program)
            logging.info(f"Отправлен объединенный вывод для программы {program}")
        
        # Отправка ответа клиенту
        conn.sendall(response.encode('utf-8'))
        
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        try:
            conn.sendall(f"Ошибка сервера: {str(e)}".encode('utf-8'))
        except:
            pass
    finally:
        conn.close()

def graceful_shutdown(signum, frame):
    """Корректное завершение работы сервера."""
    logging.info("Получен сигнал завершения работы")
    
    # Останавливаем все запущенные программы
    for prog, thread_info in program_threads.items():
        thread_info['event'].set()
        logging.info(f"Остановлена программа: {prog}")
    
    # Сохраняем данные перед выходом
    programs_data = load_programs()
    save_programs(programs_data)
    
    logging.info("Сервер завершил работу")
    sys.exit(0)

def add_initial_programs(programs):
    """Добавление программ, переданных при запуске сервера."""
    programs_data = load_programs()
    
    for program in programs:
        if program and program not in programs_data['programs']:
            programs_data['programs'][program] = {'active': True}
            logging.info(f"Добавлена программа из аргументов: {program}")
    
    save_programs(programs_data)
    return programs_data

def run_server(initial_programs=None):
    """Запуск сервера."""
    if initial_programs is None:
        initial_programs = []
        
    # Создаем директорию для вывода
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Загружаем данные о программах и добавляем новые
    programs_data = add_initial_programs(initial_programs)
    
    # Запускаем все активные программы
    start_programs(programs_data)
    
    # Регистрируем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Запускаем сервер
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        
        logging.info(f"Сервер запущен на {HOST}:{PORT}")
        print(f"Сервер запущен на {HOST}:{PORT}")
        
        try:
            while True:
                conn, addr = server.accept()
                client_thread = threading.Thread(
                    target=handle_client, 
                    args=(conn, addr, programs_data),
                    daemon=True
                )
                client_thread.start()
        except KeyboardInterrupt:
            graceful_shutdown(None, None)

if __name__ == "__main__":
    # Получаем программы из аргументов командной строки
    import sys
    initial_programs = sys.argv[1:] if len(sys.argv) > 1 else []
    
    run_server(initial_programs) 