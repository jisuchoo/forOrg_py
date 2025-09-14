from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    empno = models.CharField("사번", max_length=50, unique=True)
    password = models.CharField("비밀번호", max_length=128)
    name = models.CharField("이름", max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.empno} - {self.name or '이름없음'}"


class Disease(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="질병명")
    health = models.TextField(blank=True, null=True, verbose_name="건강고지형")
    general = models.TextField(blank=True, null=True, verbose_name="일반고지형")
    simple = models.TextField(blank=True, null=True, verbose_name="간편고지형")

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
    actor = models.CharField(max_length=100, null=True, blank=True)  # ← 세션에 저장한 사용자명
    action = models.CharField(max_length=50)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        who = self.user.username if self.user else (self.actor or "-")
        return f"[{self.created_at}] {who} - {self.action}"

class Fetal(models.Model):
    disease = models.CharField(max_length=255, verbose_name="질병명", unique=True)
    current = models.TextField(blank=True, null=True, verbose_name="현증")
    history = models.TextField(blank=True, null=True, verbose_name="과거력/치료력")
    documents = models.TextField(blank=True, null=True, verbose_name="필요서류")

    def __str__(self):
        return self.disease


class Limit(models.Model):
    product = models.CharField(max_length=100)
    plan = models.CharField(max_length=100)
    coverage = models.CharField(max_length=200)
    minAge = models.IntegerField()
    maxAge = models.IntegerField()
    amount = models.CharField(max_length=50, verbose_name="가입금액 한도")
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "limits"
        verbose_name = "인수한도"
        verbose_name_plural = "인수한도"

    def __str__(self):
        return f"{self.product} - {self.plan} ({self.minAge}~{self.maxAge})"
