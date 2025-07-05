import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from document.models import Document


class Command(BaseCommand):
    help = 'Randomizes the creation date of all documents to be within the last 7 days.'

    def handle(self, *args, **options):
        self.stdout.write("开始随机化文献的创建时间...")

        documents = Document.objects.all()
        if not documents.exists():
            self.stdout.write(self.style.WARNING("数据库中没有文献，无需操作。"))
            return

        updated_count = 0
        now = timezone.now()

        for doc in documents:
            # 生成一个0到6之间的随机天数，以及随机的小时和分钟
            random_days = random.randint(0, 6)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)

            # 计算出随机的过去时间
            new_date = now - \
                timedelta(days=random_days, hours=random_hours,
                          minutes=random_minutes)

            # 直接更新时间戳
            # 注意：我们不能用 doc.save()，因为它不会更新 auto_now_add 字段
            # 必须使用 .update() 方法来强制更新
            Document.objects.filter(pk=doc.pk).update(created_at=new_date)
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"操作完成！成功更新了 {updated_count} 篇文献的创建时间。"
        ))
