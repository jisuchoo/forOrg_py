# admin.py
from django.contrib import admin
from .models import Employee, Disease

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("empno", "name")

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ("name", "acceptance", "surgery", "recurrence")
