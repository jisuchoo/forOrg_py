import json
from pathlib import Path
from django.core.management.base import BaseCommand
from guide.models import Employee, Disease, Insurance, Fetal, Limit


class Command(BaseCommand):
    help = "employees.json, diseases.json, insurances.json, fetal_ins.json 데이터를 PostgreSQL DB에 import"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent

        # 직원 데이터 Import
        emp_file = base_dir / "employees.json"
        if emp_file.exists():
            with open(emp_file, encoding="utf-8") as f:
                employees = json.load(f)
                count = 0
                for e in employees:
                    empno = str(e.get("empno") or e.get("code") or "").strip()
                    pwd = str(e.get("password") or "").strip()
                    name = str(e.get("name") or "").strip()
                    if empno and pwd:
                        Employee.objects.update_or_create(
                            empno=empno,
                            defaults={"password": pwd, "name": name}
                        )
                        count += 1
                self.stdout.write(self.style.SUCCESS(f"직원 {count}명 Import 완료"))
        else:
            self.stdout.write(self.style.WARNING("employees.json 파일을 찾을 수 없습니다."))

        # 질병 데이터 Import (건강/일반/간편)
        dis_file = base_dir / "disease_new.json"
        if dis_file.exists():
            with open(dis_file, encoding="utf-8") as f:
                diseases = json.load(f)
                count = 0
                for d in diseases:
                    Disease.objects.update_or_create(
                        name=d.get("DSAS_CSFNM", "").strip(),
                        defaults={
                            "health": d.get("UD_HTH", ""),
                            "general": d.get("UD_GEN", ""),
                            "simple": d.get("UD_SI", ""),
                        }
                    )
                    count += 1
                self.stdout.write(self.style.SUCCESS(f"질병 {count}건 Import 완료 (건강/일반/간편)"))
        else:
            self.stdout.write(self.style.WARNING("disease_new.json 파일을 찾을 수 없습니다."))

        # 보험사 데이터 Import
        ins_file = base_dir / "insurances.json"
        if ins_file.exists():
            with open(ins_file, encoding="utf-8") as f:
                insurances = json.load(f)
                count = 0
                for i in insurances:
                    Insurance.objects.update_or_create(
                        company=i.get("company", "").strip(),
                        defaults={
                            "callCenter": i.get("callCenter", ""),
                            "fax": i.get("fax", ""),
                            "termsUrl": i.get("termsUrl", ""),
                            "type": i.get("type", ""),
                            "highlight": bool(i.get("highlight", False)),
                        }
                    )
                    count += 1
                self.stdout.write(self.style.SUCCESS(f"보험사 {count}건 Import 완료"))
        else:
            self.stdout.write(self.style.WARNING("insurances.json 파일을 찾을 수 없습니다."))

        # 태아 인수가이드 데이터 Import
        fetal_file = base_dir / "fetal_ins.json"
        if fetal_file.exists():
            with open(fetal_file, encoding="utf-8") as f:
                fetals = json.load(f)
                count = 0
                for ft in fetals:
                    disease = str(ft.get("disease") or "").strip()
                    if disease:
                        Fetal.objects.update_or_create(
                            disease=disease,
                            defaults={
                                "current": ft.get("current", ""),
                                "history": ft.get("history", ""),
                                "documents": ft.get("documents", ""),
                            }
                        )
                        count += 1
                self.stdout.write(self.style.SUCCESS(f"태아 인수가이드 {count}건 Import 완료"))
        else:
            self.stdout.write(self.style.WARNING("fetal_ins.json 파일을 찾을 수 없습니다."))

       # 인수한도 데이터 Import
        limit_file = base_dir / "limits.json"
        if limit_file.exists():
            with open(limit_file, encoding="utf-8") as f:
                limits = json.load(f)
                count = 0
                for l in limits:
                    product = str(l.get("product") or "").strip()
                    plan = str(l.get("plan") or "").strip()
                    coverage = str(l.get("coverage") or "").strip()
                    min_age = int(l.get("minAge") or 0)
                    max_age = int(l.get("maxAge") or 0)
                    amount = int(l.get("amount") or 0)
                    note = str(l.get("note") or "").strip()

                    if product and plan and coverage:
                        Limit.objects.update_or_create(
                            product=product,
                            plan=plan,
                            coverage=coverage,
                            minAge=min_age,
                            maxAge=max_age,
                            defaults={
                                "amount": amount,
                                "note": note,
                            }
                        )
                        count += 1
                self.stdout.write(self.style.SUCCESS(f"인수한도 {count}건 Import 완료"))
        else:
            self.stdout.write(self.style.WARNING("limits.json 파일을 찾을 수 없습니다."))
