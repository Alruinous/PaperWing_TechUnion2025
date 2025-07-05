from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from users.models import User
from .models import Publication
import json
import os

class PublicationAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.upload_url = reverse('publication_upload')
        self.create_url = reverse('publication_create')

    def test_file_upload_success(self):
        """测试文件成功上传"""
        self.client.login(username='testuser', password='password123')
        
        dummy_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        
        response = self.client.post(self.upload_url, {'file': dummy_file})
        
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json['status'], 'success')
        self.assertTrue(response_json['file_path'].startswith('publications/'))
        self.assertTrue(response_json['file_path'].endswith('.pdf'))
        
        # 验证文件是否真的被创建
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, response_json['file_path'])))

    def test_create_publication_success(self):
        """测试科研成果元数据成功创建"""
        self.client.login(username='testuser', password='password123')
        
        data = {
            "title": "A Novel Approach to Quantum Computing",
            "type": "Conference Paper",
            "authors": "Zhang San, Li Si",
            "journal": "Proceedings of Quantum 2025",
            "volume": "12",
            "issue": "3",
            "year": 2025,
            "abstract": "本文提出了…",
            "keywords": "quantum computing, entanglement, algorithms",
            "external_url": "https://example.com/qc2025",
            "local_file_path": "publications/qc2025.pdf",
            "created_by": self.user.id
        }
        
        response = self.client.post(self.create_url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        # 验证数据库中是否真的创建了记录
        self.assertTrue(Publication.objects.filter(title=data['title'], created_by=self.user).exists())
        publication = Publication.objects.get(title=data['title'])
        self.assertEqual(publication.local_file.name, data['local_file_path'])
