import socket
import json
import sys

HOST = 'localhost'
PORT = 5555
BUFFER_SIZE = 65536

def send_request(request):
    """Отправка запроса на сервер и получение ответа."""
    try:
        # Создание сокета и подключение к серверу
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))
            
            # Отправка запроса
            sock.sendall(json.dumps(request).encode('utf-8'))
            
            # Получение ответа
            response = b""
            while True:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    break
                response += data
            
            return response.decode('utf-8')
    except ConnectionRefusedError:
        return "Ошибка: Не удалось подключиться к серверу. Убедитесь, что сервер запущен."
    except socket.error as e:
        return f"Ошибка соединения: {e}"
    except Exception as e:
        return f"Ошибка: {e}"

def add_program():
    """Добавление новой программы на сервер."""
    program = input("Введите название программы для добавления: ")
    if not program:
        print("Ошибка: Название программы не может быть пустым.")
        return
    
    response = send_request({"action": "add", "program": program})
    print(response)

def get_output():
    """Получение объединенного вывода программы."""
    program = input("Введите название программы для получения вывода: ")
    if not program:
        print("Ошибка: Название программы не может быть пустым.")
        return
    
    response = send_request({"action": "get_output", "program": program})
    print(response)

def print_help():
    """Вывод справки по командам."""
    print("\nДоступные команды:")
    print("1 или add      - Добавить новую программу")
    print("2 или output   - Получить вывод программы")
    print("help           - Показать эту справку")
    print("exit или q     - Выйти из программы")

def main():
    """Основная функция клиента."""
    print("Клиент для управления программами")
    print_help()
    
    while True:
        try:
            command = input("\nВведите команду: ").strip().lower()
            
            if command in ['exit', 'q']:
                print("Выход из программы.")
                break
            
            if command in ['help', '?']:
                print_help()
                continue
            
            if command in ['1', 'add']:
                add_program()
            elif command in ['2', 'output']:
                get_output()
            else:
                print(f"Неизвестная команда: {command}")
                print_help()
        
        except KeyboardInterrupt:
            print("\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main() 