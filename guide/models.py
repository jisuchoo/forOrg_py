from django.db import models

class Employee(models.Model):
    empno = models.CharField("사번", max_length=50, unique=True)
    password = models.CharField("비밀번호", max_length=128)
    name = models.CharField("이름", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.empno} - {self.name or '이름없음'}"


class Disease(models.Model):
    name = models.CharField("질병명", max_length=255, unique=True)
    acceptance = models.TextField("인수기준", blank=True, null=True)
    signature355 = models.TextField("시그니처355", blank=True, null=True)
    treatmentDays = models.CharField("치료일수", max_length=100, blank=True, null=True)
    surgery = models.CharField("수술여부", max_length=100, blank=True, null=True)
    recurrence = models.CharField("재발여부", max_length=100, blank=True, null=True)
    restrictions = models.TextField("제한사항", blank=True, null=True)

    def __str__(self):
        return self.name
