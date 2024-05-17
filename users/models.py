from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from user_management_system.settings import STATICFILES_DIRS
import uuid

def user_directory_path(instance, filename):
    # Get the filename extension
    ext = filename.split('.')[-1]
    # Generate the filename
    unique_filename = f'{uuid.uuid4()}.{filename.split(".")[-1]}'
    # Return the path to upload the file
    return os.path.join(STATICFILES_DIRS[0],'images', instance.username, 'avatars', unique_filename)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name
    
    def delete(self, *args, **kwargs):
        # Delete user's avatar file if it exists
        if self.avatar:
            if os.path.isfile(self.avatar.path):
                os.remove(self.avatar.path)
        # Call parent class delete method
        super().delete(*args, **kwargs)


    
