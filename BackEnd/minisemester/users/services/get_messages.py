from typing import List, Optional, TypedDict
from users.models import User
from utils.exceptions import BusinessLogicError
from publications.models import Publication, PublicationUser
from django.db.models import Q
from discussions.models import Conversation
import random


class Author(TypedDict, total=False):
    userId: int
    userName: str
    registed: bool


class Message(TypedDict, total=False):
    type: int  # 1, 2, 3, 4
    abstract: str                 # type 1, 2, 3, 4
    authors: List[Author]        # type 1, 3
    followerName: str            # type 3, 4
    paperId: int                 # type 1, 3
    paperTitle: str              # type 1, 3
    questionId: int              # type 2, 4   
    questionAuthorId: int        # type 2, 4
    questionAuthor: str          # type 2, 4
    questionTitle: str           # type 2, 4
    year: str                    # type 1, 2, 3, 4
    # 可扩展字段也允许存在


"""
type:
1 = 根据领域推荐成果*5
2 = 根据领域推荐问题*5
3 = 关注的人发表新的成果
4 = 关注的人发表新的问题
"""

def get_authors(pub: Publication) -> List[Author]:
    authors = []
    authors_name_pub = pub.authors_list
    authors_registed = PublicationUser.objects.filter(publication_id=pub.pub_id)
    registed_name_to_id = {au.user.name: au.user.id for au in authors_registed}

    for author_name in authors_name_pub:
        if author_name in registed_name_to_id:
            authors.append({
                "userId": registed_name_to_id[author_name],
                "userName": author_name,
                "registed": True
            })
        else:
            authors.append({
                "userName": author_name,
                "registed": False
            })
    
    return authors

def get_messages(user_id: int) -> List[Message]:
    messages = []
    user = User.objects.filter(id=user_id).first()
    if not user:
        raise BusinessLogicError("用户不存在")
    
    user_fields = user.research_fields_list
    followees = list(User.objects.filter(followers__follower_id=user_id))
    # type 1: 根据领域推荐成果
    if not user_fields:
        latest_pub_5 = list(Publication.objects.order_by('-created_at')[:5])
    else:
        query = Q()
        for field in user_fields:
            query |= Q(research_fields__icontains=field)
        matched_pubs = list(Publication.objects.filter(query).order_by('-created_at')[:3])
        if len(matched_pubs) < 5:
            fallback_pubs = list(Publication.objects.exclude(pub_id__in=[p.pub_id for p in matched_pubs]).order_by('-created_at')[:5 - len(matched_pubs)])
            matched_pubs += fallback_pubs
        latest_pub_5 = matched_pubs
    for pub in latest_pub_5:
            authors = get_authors(pub)
            messages.append({
                "type": 1,
                "abstract": pub.abstract,
                "authors": authors,
                "paperId": pub.pub_id,
                "paperTitle": pub.title,
                "year": str(pub.year) if pub.year is not None else ""
            })

    # type 2: 根据领域推荐问题
    if not user_fields:
        lastest_forum_5 = Conversation.objects.filter(type='forum').order_by('-created_at')[:5]
    else:
        # 有研究方向：构造查询条件
        query = Q()
        for field in user_fields:
            query |= Q(research_fields__icontains=field)
        # 先根据研究方向筛选前5个
        matched_forums = list(Conversation.objects.filter(type='forum').filter(query).order_by('-created_at')[:3])
        if len(matched_forums) < 5:
            # 还需要补多少个
            needed = 5 - len(matched_forums)
            exclude_ids = [f.conversation_id for f in matched_forums]
            # 补充最新的，不重复已有的
            fillers = list(Conversation.objects.filter(type='forum').exclude(conversation_id__in=exclude_ids).order_by('-created_at')[:needed])
            matched_forums += fillers
        lastest_forum_5 = matched_forums
        if not lastest_forum_5:
            # 如果按领域匹配结果为空，fallback 返回最新的公开论坛
            lastest_forum_5 = Conversation.objects.filter(type='forum').order_by('-created_at')[:5]
    for forum in lastest_forum_5:
        messages.append({
            "type": 2,
            "questionId": forum.conversation_id,
            "questionAuthorId": forum.initiator.id,
            "questionAuthor": forum.initiator.name,
            "abstract": forum.abstract,
            "questionTitle": forum.title,
            "year": forum.created_at.strftime("%Y-%m-%d %H:%M")
        })

    # type 3: 关注的人的新成果
    random.shuffle(followees)
    latest_follow_pubs_2 = []

    for followee in followees:
        pub = Publication.objects.filter(created_by=followee).order_by('-created_at').first()
        if pub:
            latest_follow_pubs_2.append((followee, pub))
            if len(latest_follow_pubs_2) >= 2:
                break  # 收集够两个成果就退出
    for followee, pub in latest_follow_pubs_2:
        authors = get_authors(pub)
        messages.append({
            "type": 3,
            "abstract": pub.abstract,
            "authors": authors,
            "followerName": followee.name,
            "paperId": pub.pub_id,
            "paperTitle": pub.title,
            "year": str(pub.year) if pub.year is not None else ""
        })

    # type 4: 关注的人的新问题
    random.shuffle(followees)
    latest_follow_convs_2 = []
    for followee in followees:
        conv = Conversation.objects.filter(type='forum', initiator=followee).order_by('-created_at').first()
        if conv:
            latest_follow_convs_2.append((followee, conv))
            if len(latest_follow_convs_2) >= 2:
                break  # 找到两个就退出

    # 构造 message 结构
    for followee, conv in latest_follow_convs_2:
        messages.append({
            "type": 4,
            "followerName": followee.name,
            "questionId": conv.conversation_id,
            "questionAuthorId": conv.initiator.id,
            "questionAuthor": conv.initiator.name,
            "abstract": conv.abstract,
            "questionTitle": conv.title,
            "year": conv.created_at.strftime("%Y-%m-%d %H:%M")
            
        })
    return messages