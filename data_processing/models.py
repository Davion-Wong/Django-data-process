from django.db import models

class DatasetModel(models.Model):
    name = models.CharField(max_length=255)
    birthdate = models.DateField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=5, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name  # or any identifier for the dataset row
