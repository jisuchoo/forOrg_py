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
    company = models.CharField(max_length=255, unique=True, verbose_name="회사명")
    callCenter = models.CharField(max_length=50, blank=True, null=True, verbose_name="콜센터")
    fax = models.CharField(max_length=50, blank=True, null=True, verbose_name="팩스")
    termsUrl = models.URLField(blank=True, null=True, verbose_name="공시실 URL")
    type = models.CharField(max_length=50, blank=True, null=True, verbose_name="보험 종류")
    highlight = models.BooleanField(default=False, verbose_name="강조 여부")

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
    disease = models.CharField(max_length=255, unique=True, verbose_name="질병명")
    current = models.TextField(blank=True, null=True, verbose_name="현증")
    history = models.TextField(blank=True, null=True, verbose_name="과거력/치료력")
    documents = models.TextField(blank=True, null=True, verbose_name="필요서류")

    def __str__(self):
        return self.disease


class Limit(models.Model):
    product = models.CharField(max_length=255, verbose_name="상품명")
    plan = models.CharField(max_length=255, verbose_name="플랜명")
    coverage = models.CharField(max_length=255, verbose_name="담보명")
    minAge = models.IntegerField(verbose_name="최소 연령")
    maxAge = models.IntegerField(verbose_name="최대 연령")
    amount = models.CharField(max_length=50, verbose_name="가입금액 한도")  # ✅ 문자열 저장
    note = models.TextField(blank=True, null=True, verbose_name="비고")

    def __str__(self):
        return f"{self.product} - {self.plan} ({self.coverage})"
