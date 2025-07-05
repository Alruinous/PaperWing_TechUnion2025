from django.core.management.base import BaseCommand
from django.utils import timezone
from document.models import AnalysisSubscription
from document.services import report_generation_services
import logging

# 配置日志
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '为到期的订阅生成技术速递报告，并为每个用户清理过时订阅。'

    def handle(self, *args, **options):
        self.stdout.write(f"[{timezone.now()}] 开始检查需要生成的报告...")

        # 1. 找出所有到期的订阅
        due_subscriptions = AnalysisSubscription.objects.filter(
            next_run_at__lte=timezone.now()
        )

        if not due_subscriptions.exists():
            self.stdout.write("没有需要生成的报告。")
            return

        # 2. 获取有到期订阅的独立用户ID列表
        due_user_ids = due_subscriptions.values_list(
            'user_id', flat=True).distinct()

        self.stdout.write(f"发现 {len(due_user_ids)} 个用户有待处理的订阅。")

        # 3. 遍历每个用户，只处理其最新的订阅
        for user_id in due_user_ids:
            # 找出该用户所有订阅中，按创建时间排序，最新的一个
            try:
                latest_subscription = AnalysisSubscription.objects.filter(
                    user_id=user_id
                ).latest('created_at')
            except AnalysisSubscription.DoesNotExist:
                continue  # 如果找不到订阅，跳过此用户

            # 检查这个最新的订阅是否真的到期了
            if latest_subscription.next_run_at and latest_subscription.next_run_at > timezone.now():
                # 如果最新的订阅还没到期，则跳过该用户，并清理其他可能的过时订阅
                subscriptions_to_delete = AnalysisSubscription.objects.filter(
                    user_id=user_id
                ).exclude(pk=latest_subscription.id)
                if subscriptions_to_delete.exists():
                    deleted_count, _ = subscriptions_to_delete.delete()
                    self.stdout.write(self.style.WARNING(
                        f"为用户ID {user_id} 清理了 {deleted_count} 个过时的订阅，保留了未到期的最新订阅。"
                    ))
                continue

            self.stdout.write(
                f"正在为用户ID {user_id} 的最新订阅 (ID: {latest_subscription.id}, 关键词: '{latest_subscription.keyword}') 生成报告...")

            try:
                # 4. 为最新的订阅生成报告
                report_generation_services.generate_and_save_report(
                    latest_subscription.id)

                self.stdout.write(self.style.SUCCESS(
                    f"成功为订阅ID {latest_subscription.id} 生成报告。"
                ))

                # 5. 报告成功后，删除该用户所有其他的订阅记录
                subscriptions_to_delete = AnalysisSubscription.objects.filter(
                    user_id=user_id
                ).exclude(pk=latest_subscription.id)

                if subscriptions_to_delete.exists():
                    deleted_count, _ = subscriptions_to_delete.delete()
                    self.stdout.write(self.style.WARNING(
                        f"为用户ID {user_id} 删除了 {deleted_count} 个过时的订阅。"
                    ))

            except Exception as e:
                logger.error(
                    f"为订阅ID {latest_subscription.id} 生成报告时出错: {e}", exc_info=True)
                self.stderr.write(self.style.ERROR(
                    f"为订阅ID {latest_subscription.id} 生成报告时失败: {e}"
                ))
                # 如果生成失败，则不删除任何订阅，以便下次重试

        self.stdout.write(self.style.SUCCESS("所有到期报告处理完毕。"))
