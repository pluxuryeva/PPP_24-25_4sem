import hashlib
import itertools
import time
from typing import Generator, Optional


class BruteforceService:
    def __init__(self, hash_type: str = "md5"):
        self.hash_type = hash_type.lower()
        self.hash_functions = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512
        }
    
    def hash_string(self, text: str) -> str:
        """Хеширует строку выбранным алгоритмом"""
        if self.hash_type in self.hash_functions:
            hash_func = self.hash_functions[self.hash_type]
            return hash_func(text.encode()).hexdigest()
        else:
            # Для RAR/ZIP можно добавить специальную логику
            return hashlib.md5(text.encode()).hexdigest()
    
    def generate_combinations(self, charset: str, max_length: int) -> Generator[str, None, None]:
        """Генерирует все возможные комбинации символов"""
        for length in range(1, max_length + 1):
            for combination in itertools.product(charset, repeat=length):
                yield ''.join(combination)
    
    def bruteforce(self, target_hash: str, charset: str, max_length: int, 
                   progress_callback=None) -> Optional[str]:
        """
        Выполняет брутфорс атаку
        
        Args:
            target_hash: Целевой хеш для взлома
            charset: Набор символов для перебора
            max_length: Максимальная длина пароля
            progress_callback: Функция для отчета о прогрессе
        
        Returns:
            Найденный пароль или None
        """
        start_time = time.time()
        attempts = 0
        total_combinations = sum(len(charset) ** i for i in range(1, max_length + 1))
        
        for combination in self.generate_combinations(charset, max_length):
            attempts += 1
            
            # Вычисляем хеш текущей комбинации
            current_hash = self.hash_string(combination)
            
            # Отчет о прогрессе каждые 1000 попыток
            if attempts % 1000 == 0 and progress_callback:
                progress = int((attempts / total_combinations) * 100)
                elapsed = time.time() - start_time
                combinations_per_second = int(attempts / elapsed) if elapsed > 0 else 0
                
                progress_callback(
                    progress=min(progress, 99),  # Не показываем 100% до завершения
                    current_combination=combination,
                    combinations_per_second=combinations_per_second
                )
            
            # Проверяем совпадение
            if current_hash.lower() == target_hash.lower():
                return combination
            
            # Защита от бесконечного выполнения (максимум 10 минут)
            if time.time() - start_time > 600:
                break
        
        return None 