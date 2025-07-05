from django.test import TestCase, Client
from django.urls import reverse
from .models import User
import json


class UserAPITests(TestCase):
    """
    用户相关API的单元测试
    """

    def setUp(self):
        """
        在每个测试方法运行前执行，用于设置初始环境。
        """
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.check_url = reverse('check_account_or_email')
        self.userinfo_url = reverse('userinfo')

        # 创建一个预置用户，用于测试登录、信息查询等
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com',
            name='Test User',
            institution='Test University',
            avatar_url='http://example.com/avatar.png'  # 确保测试用户有头像链接
        )

    def test_register_view_success(self):
        """测试成功注册的场景"""
        data = {
            "institution": "New University",
            "account": "newuser",
            "name": "New User",
            "email": "new@example.com",
            "password": "newpassword123",
            "research_fields": "Testing, Django"
        }
        response = self.client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['status'], 'success')
        # 验证数据库中是否真的创建了用户
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_success(self):
        """测试成功登录的场景"""
        data = {
            "account": "testuser",
            "password": "testpassword123"
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['account'], 'testuser')
        # 验证 session 是否成功建立
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_view_fail(self):
        """测试密码错误导致登录失败的场景"""
        data = {
            "account": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], '账号或密码错误')

    def test_check_account_or_email_view_exists(self):
        """测试账号或邮箱已存在的场景"""
        data = {
            "account": "testuser",  # 这个账号已存在
            "email": "other@example.com"
        }
        response = self.client.post(
            self.check_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['exists'])

    def test_check_account_or_email_view_not_exists(self):
        """测试账号和邮箱都未被占用的场景"""
        data = {
            "account": "nonexistentuser",
            "email": "nonexistent@example.com"
        }
        response = self.client.post(
            self.check_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['exists'])

    def test_user_info_view_success(self):
        """测试成功查询用户信息的场景 (GET)"""
        # 对于GET请求，参数直接跟在URL后面
        response = self.client.get(
            self.userinfo_url,
            data={'userId': self.test_user.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 200)
        self.assertEqual(response.json()['data']['user_id'], self.test_user.id)
        self.assertEqual(response.json()['data']['name'], 'Test User')

    def test_user_info_view_not_found(self):
        """测试查询一个不存在的用户ID的场景 (GET)"""
        response = self.client.get(
            self.userinfo_url,
            data={'userId': 9999}  # 一个不存在的ID
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], '用户不存在')
    def test_update_user_info_success(self):
        """测试成功更新用户信息的场景"""
        # 首先登录用户以建立 session
        self.client.login(username='testuser', password='testpassword123')

        new_data = {
            "account": "testuser_updated",
            "email": "test_updated@example.com",
            "name": "Test User Updated",
            "title": "Senior Researcher",
            "education": "PhD",
            "institution": "Updated University",
            "avatar_url": "http://example.com/new_avatar.png",
            "bio": "Updated bio.",
            "research_fields": "Updated fields"
        }

        response = self.client.post(
            self.updateinfo_url,
            data=json.dumps(new_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], '用户信息更新成功')

        # 从数据库重新获取用户，验证字段是否已更新
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.username, new_data['account'])
        self.assertEqual(self.test_user.title, new_data['title'])

    
