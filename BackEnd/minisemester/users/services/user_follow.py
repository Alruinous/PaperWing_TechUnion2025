from users.models import User, UserFollow
from utils.exceptions import BusinessLogicError

def follow_user(follower_id: int, followee_id: int) -> None:
    follower = User.objects.filter(id=follower_id).first()
    followee = User.objects.filter(id=followee_id).first()
    if not follower or not followee:
        raise BusinessLogicError("用户不存在")
    
    # 检查是否已关注
    if UserFollow.objects.filter(follower=follower, followee=followee).exists():
        raise BusinessLogicError("已关注，无需重复关注")
    
    UserFollow.objects.create(follower=follower, followee=followee)


def unfollow_user(follower_id: int, followee_id: int) -> None:
    follower = User.objects.filter(id=follower_id).first()
    followee = User.objects.filter(id=followee_id).first()
    if not follower or not followee:
        raise BusinessLogicError("用户不存在")
    
    follow_obj = UserFollow.objects.filter(follower=follower, followee=followee).first()
    if not follow_obj:
        raise BusinessLogicError("未关注，无需取关")
    
    follow_obj.delete()


def get_followers_list(user_id: int):
    """
    获取指定用户的关注者列表。
    """
    try:
        user = User.objects.get(id=user_id)
        # 使用 related_name='followers' 进行反向查询
        # 找到所有 UserFollow 记录中，被关注者(followee)是当前用户的记录，
        # 然后获取这些记录的关注者(follower)。
        return User.objects.filter(following__followee=user)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")


def get_following_list(user_id: int):
    """
    获取指定用户正在关注的用户列表。
    """
    try:
        user = User.objects.get(id=user_id)
        # 使用 related_name='following' 进行反向查询
        # 找到所有 UserFollow 记录中，关注者(follower)是当前用户的记录，
        # 然后获取这些记录的被关注者(followee)。
        return User.objects.filter(followers__follower=user)
    except User.DoesNotExist:
        raise BusinessLogicError("用户不存在")
