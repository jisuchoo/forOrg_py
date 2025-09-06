import json
from pathlib import Path
from django.core.management.base import BaseCommand
from guide.models import Employee, Disease

class Command(BaseCommand):
    help = "employees.json과 diseases.json 데이터를 PostgreSQL DB에 import"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent / "data"

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

        # 질병 데이터 Import
        dis_file = base_dir / "diseases.json"
        if dis_file.exists():
            with open(dis_file, encoding="utf-8") as f:
                diseases = json.load(f)
                count = 0
                for d in diseases:
                    Disease.objects.update_or_create(
                        name=d.get("name", "").strip(),
                        defaults={
                            "acceptance": d.get("acceptance", ""),
                            "signature355": d.get("signature355", ""),
                            "treatmentDays": d.get("treatmentDays", ""),
                            "surgery": d.get("surgery", ""),
                            "recurrence": d.get("recurrence", ""),
                            "restrictions": d.get("restrictions", ""),
                        }
                    )
                    count += 1
                self.stdout.write(self.style.SUCCESS(f"질병 {count}건 Import 완료"))
        else:
            self.stdout.write(self.style.WARNING("diseases.json 파일을 찾을 수 없습니다."))
