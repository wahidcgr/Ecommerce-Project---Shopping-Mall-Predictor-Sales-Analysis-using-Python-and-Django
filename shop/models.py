from django.db import models

class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    
    def __str__(self):
        return self.file.name
