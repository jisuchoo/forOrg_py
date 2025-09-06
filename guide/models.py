from django.db import models

class Employee(models.Model):
    empno = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.empno} - {self.name}"

class Disease(models.Model):
    name = models.CharField(max_length=100)
    acceptance = models.TextField(blank=True)
    signature355 = models.TextField(blank=True)
    treatmentDays = models.CharField(max_length=50, blank=True)
    surgery = models.CharField(max_length=50, blank=True)
    recurrence = models.CharField(max_length=50, blank=True)
    restrictions = models.TextField(blank=True)

    def __str__(self):
        return self.name
