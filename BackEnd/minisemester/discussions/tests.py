from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from .models import Conversation, Message, ConversationParticipant
import json

class MessageAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(username='sender', password='password123', email='sender@test.com')
        self.receiver = User.objects.create_user(username='receiver', password='password123', email='receiver@test.com')
        
        # 创建一个项目，发起人是 sender
        self.project = Conversation.objects.create(initiator=self.sender, title='Test Project', type='project')
        # 将 sender 添加为项目的正式成员
        ConversationParticipant.objects.create(conversation=self.project, user=self.sender, status='approved')

        self.send_message_url = reverse('send_message')

    def test_send_invitation_message_success(self):
        """测试成功发送邀请消息并创建参与者记录"""
        self.client.login(username='sender', password='password123')
        data = {
            "senderId": self.sender.id,
            "receiverId": self.receiver.id,
            "type": "invitation",
            "content": "邀请您加入项目",
            "projectId": self.project.conversation_id,
            "timestamp": "2025/06/23/17/50"
        }
        response = self.client.post(self.send_message_url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertTrue(response_json['success'])
        self.assertEqual(response_json['receiverId'], self.receiver.id) # 验证返回了正确的 receiverId
        
        # 验证消息已创建
        message_id = response_json['messageId']
        self.assertTrue(Message.objects.filter(message_id=message_id).exists())
        
        # 验证参与者记录已创建且状态正确
        self.assertTrue(ConversationParticipant.objects.filter(
            conversation=self.project,
            user=self.receiver,
            status='invited'
        ).exists())

    def test_send_user_message_success(self):
        """测试成功发送普通用户消息"""
        self.client.login(username='sender', password='password123')
        data = {
            "senderId": self.sender.id,
            "receiverId": self.receiver.id,
            "type": "user",
            "content": "Hello, friend!",
            "projectId": 0,
            "timestamp": "2025/06/23/18/00"
        }
        response = self.client.post(self.send_message_url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        message = Message.objects.get(message_id=response.json()['messageId'])
        self.assertEqual(message.message_type, 'user')
        self.assertIsNone(message.conversation)

    def test_send_message_as_another_user(self):
        """测试以他人名义发送消息的场景"""
        self.client.login(username='receiver', password='password123') # 使用 receiver 登录
        data = {
            "senderId": self.sender.id, # 但声称是 sender 发送
            "receiverId": self.receiver.id,
            "type": "user",
            "content": "hacker attack",
            "projectId": 0,
            "timestamp": "2025/06/23/18/00"
        }
        response = self.client.post(self.send_message_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], '无权以他人身份发送消息。')
    def test_get_messages_inbox_success(self):
        """测试成功获取收件箱"""
        self.client.login(username='sender', password='password123')
        response = self.client.get(self.get_messages_url, {'box': 'inbox', 'userId': self.sender.id})
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        data = response.json()['data']
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['messages'][0]['content'], 'Hi Sender')
        self.assertEqual(data['messages'][0]['senderId'], self.another_user.id)

    def test_get_messages_sent_success(self):
        """测试成功获取已发送"""
        self.client.login(username='sender', password='password123')
        response = self.client.get(self.get_messages_url, {'box': 'sent', 'userId': self.sender.id})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        data = response.json()['data']
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['messages'][0]['content'], 'Hi Receiver')

    def test_get_messages_forbidden(self):
        """测试用户尝试获取他人消息列表"""
        self.client.login(username='receiver', password='password123')
        # receiver 尝试获取 sender 的收件箱
        response = self.client.get(self.get_messages_url, {'box': 'inbox', 'userId': self.sender.id})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['message'], '无权查看他人消息。')