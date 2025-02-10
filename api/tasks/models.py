from django.db import models
from time import time
from os.path import splitext
from datetime import datetime

# Кастомная функция для генерации пути загрузки файла
def generate_file_upload_path(instance: 'File', filename: str) -> str:
    """
    Генерирует уникальный путь для загрузки файла на основе текущего времени и расширения файла.

    Args:
        instance (File): Экземпляр модели File.
        filename (str): Имя загружаемого файла.

    Returns:
        str: Уникальный путь для файла.
    """
    timestamp = int(time())  # Преобразуем время в целочисленный временной штамп
    file_extension = splitext(filename)[1]  # Получаем расширение файла
    return f"uploads/{timestamp}_{filename[:15]}{file_extension}"  # Используем временной штамп и часть имени файла

class File(models.Model):
    name = models.CharField(max_length=1024, blank=True, verbose_name="Имя файла")
    extension = models.CharField(max_length=64, blank=True, verbose_name="Расширение файла")
    file = models.FileField(upload_to=generate_file_upload_path, verbose_name="Загруженный файл")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        ordering = ['-created_at']  # Сортировка по дате создания
        verbose_name = "Запись файла"
        verbose_name_plural = "Записи файлов"

    def __str__(self):
        return f"{self.name} ({self.extension})"
