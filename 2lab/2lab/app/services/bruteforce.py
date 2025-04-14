import itertools
import threading
import time
from typing import List, Callable

from app.cruds.bruteforce import update_task_status


def generate_passwords(charset: str, max_length: int) -> List[str]:
    all_passwords = []
    for length in range(1, max_length + 1):
        for password in itertools.product(charset, repeat=length):
            all_passwords.append(''.join(password))
    return all_passwords


def check_hash(hash_to_check: str, password: str) -> bool:
    return hash_to_check == password


def brute_force(task_id: str, hash_to_crack: str, charset: str, max_length: int, 
                update_callback: Callable[[str, str, float, str], None]) -> None:
    update_callback(task_id, "running", 0.0, None)
    
    try:
        passwords = generate_passwords(charset, max_length)
        total_passwords = len(passwords)
        
        for i, password in enumerate(passwords):
            if check_hash(hash_to_crack, password):
                update_callback(task_id, "completed", 100.0, password)
                return
            
            if i % 1000 == 0 or i == total_passwords - 1:
                progress = (i + 1) / total_passwords * 100
                update_callback(task_id, "running", progress, None)
        
        update_callback(task_id, "completed", 100.0, None)
    
    except Exception as e:
        update_callback(task_id, "failed", 0.0, str(e))


def start_brute_force_task(task_id: str, hash_to_crack: str, charset: str, max_length: int, 
                          db_callback: Callable[[str, str, float, str], None]) -> None:
    thread = threading.Thread(
        target=brute_force,
        args=(task_id, hash_to_crack, charset, max_length, db_callback)
    )
    thread.daemon = True
    thread.start() 