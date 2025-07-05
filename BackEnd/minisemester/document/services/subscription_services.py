from ..models import AnalysisSubscription
from django.contrib.auth import get_user_model
from utils.exceptions import BusinessLogicError
from django.utils import timezone
User = get_user_model()


def create_or_update_subscription(user_id: int, keyword: str, frequency: str) -> AnalysisSubscription:
    """
    为用户创建或更新技术速递订阅。
    - 如果是新创建的订阅，则将其标记为立即生成报告。
    - 如果是更新已有的订阅，则不改变其下一次运行时间。
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")

    # 使用 update_or_create 方法，它会返回一个布尔值`created`
    subscription, created = AnalysisSubscription.objects.update_or_create(
        user=user,
        keyword=keyword,
        defaults={'frequency': frequency}
    )

    # --- 核心修改 ---
    # 只有在新创建订阅时，才设置 next_run_at 为当前时间，以触发首次报告生成
    if created:
        subscription.next_run_at = timezone.now()
        subscription.save(update_fields=['next_run_at'])

    return subscription
