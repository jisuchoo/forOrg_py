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


class Insurance(models.Model):
    company = models.CharField("회사명", max_length=255, unique=True)
    callCenter = models.CharField("콜센터", max_length=50)
    fax = models.CharField("보험금청구/팩스", max_length=50, blank=True, null=True)
    termsUrl = models.URLField("공시실 URL", blank=True, null=True)
    type = models.CharField("구분", max_length=50)  # 손해보험 / 생명보험 / 공제
    highlight = models.BooleanField("하이라이트", default=False)  # 한화손해보험 같은 강조 카드

    def __str__(self):
        return f"{self.company} ({self.type})"
