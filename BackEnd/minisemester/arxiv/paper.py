import os
import sys
import json
import asyncio
from typing import Dict, List
from rich.console import Console
from django.utils.decorators import sync_and_async_middleware
from asgiref.sync import sync_to_async

# 获取当前文件所在目录的父目录（项目根目录）
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # 假设paper.py在项目子目录中

# 将项目根目录添加到Python路径
sys.path.append(project_root)

# 配置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minisemester.settings')
import django
django.setup()

from django.db import transaction
from users.models import User  # 替换为你的自定义用户模型路径
from document.models import Document  # 替换为你的实际应用名

class PaperDatabase:
    def __init__(self):
        self.console = Console()
        self._ensure_system_user()

    @sync_to_async
    def _ensure_system_user(self):
        """确保系统用户存在"""
        self.system_user, _ = User.objects.get_or_create(
            username='arxiv_bot',
            defaults={
                'email': 'arxiv_bot@example.com',
                'is_active': False,
                'is_staff': False
            }
        )

    @sync_to_async
    def _create_document(self, paper: Dict, topic: str):
        """创建单个文档的同步方法"""
        return Document.objects.create(
            title=paper['title'],
            authors=paper['authors'],
            journal=paper['journal'],
            year=paper['year'],
            abstract=paper['abstract'],
            keywords=paper['keywords'],
            source='arxiv',
            research_fields=topic,
            arxiv_url=paper.get('pdf_url', '').replace('/pdf/', '/abs/'),
            pdf_url=paper.get('pdf_url', ''),
            comments=paper.get('comments', ''),
        )

    async def save_to_database(self, papers_data: Dict[str, List[Dict]]):
        """将论文数据保存到Django数据库"""
        total_created = 0
        
        # 使用sync_to_async包装整个事务
        @sync_to_async
        def save_topic_papers(topic, papers):
            created = 0
            for paper in papers:
                # 检查是否已存在相同arxiv_id的文档
                if Document.objects.filter(
                    title=paper['title'],
                    authors=paper['authors']
                ).exists():
                    continue
                
                try:
                    Document.objects.create(
                        title=paper['title'],
                        authors=paper['authors'],
                        journal=paper['journal'],
                        year=paper['year'],
                        abstract=paper['abstract'],
                        keywords=topic,
                        source='arxiv',
                        research_fields=paper['research_fields'],
                        arxiv_url=paper.get('pdf_url', '').replace('/pdf/', '/abs/'),
                        pdf_url=paper.get('pdf_url', ''),
                        comments=paper.get('comments', ''),
                    )
                    created += 1
                except Exception as e:
                    self.console.log(f"[red]Error saving paper {paper['title']}: {str(e)}")
            return created

        # 确保系统用户已创建
        await self._ensure_system_user()

        # 处理每个主题的论文
        for topic, papers in papers_data.items():
            created = await save_topic_papers(topic, papers)
            self.console.log(f"[green]Saved {created} papers for {topic}")
            total_created += created
        
        return total_created

class PaperProcessor:
    def __init__(self):
        self.db = PaperDatabase()
        self.console = Console()

    async def process_papers(self, input_file: str = "minisemester/arxiv/arxiv_papers.json"):
        """处理并保存论文数据"""
        try:
            with open(input_file, "r") as f:
                papers_data = json.load(f)
        except FileNotFoundError:
            self.console.log("[red]Error: arxiv_papers.json not found. Run arxiv_crawler.py first.")
            return

        # 保存到数据库
        total_saved = await self.db.save_to_database(papers_data)
        self.console.log(f"[bold green]Total saved: {total_saved} new papers")

if __name__ == "__main__":
    processor = PaperProcessor()
    asyncio.run(processor.process_papers())