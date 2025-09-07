from django.db import models
from django.contrib.auth.models import User

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
    callCenter = models.CharField("콜센터", max_length=50, blank=True, null=True)
    fax = models.CharField("팩스", max_length=50, blank=True, null=True)
    termsUrl = models.URLField("공시실 URL", blank=True, null=True)
    type = models.CharField("보험 종류", max_length=50, blank=True, null=True)
    highlight = models.BooleanField("강조 여부", default=False)

    def __str__(self):
        return self.company

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)   # LOGIN, SEARCH 등
    detail = models.TextField(blank=True)      # 검색어, 조회한 항목 등
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at}] {self.user} - {self.action}"
