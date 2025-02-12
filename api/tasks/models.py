from os.path import splitext
from time import time

from django.db import models

# Create your models here.


def user_directory_path(instance: 'File', filename: str):
    """

    Args:
        instance (File):
        filename (str):

    Returns:
        str:
    """
    _, extension = splitext(filename)
    return f'user/{time()}{extension}'


class File(models.Model):
    name = models.CharField(max_length=1024, blank=True)
    extension = models.CharField(max_length=64, blank=True)
    file = models.FileField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
