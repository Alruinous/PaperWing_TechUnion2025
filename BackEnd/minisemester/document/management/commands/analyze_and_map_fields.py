import json
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from document.models import Document
import os


class Command(BaseCommand):
    help = 'Analyzes all documents to create a map from research fields to specific keywords.'

    def handle(self, *args, **options):
        self.stdout.write("开始分析文献，构建研究领域到关键词的映射...")

        # 使用 defaultdict(set) 可以方便地处理新领域并自动去重关键词
        field_to_keywords_map = defaultdict(set)

        documents = Document.objects.all()
        if not documents.exists():
            self.stdout.write(self.style.WARNING("数据库中没有文献，无法生成映射。"))
            return

        processed_docs = 0
        for doc in documents:
            # 使用模型中的 @property 方法获取列表
            research_fields = doc.research_fields_list
            keywords = doc.keywords_list

            if not research_fields or not keywords:
                continue

            for field in research_fields:
                # 将该文献的所有关键词添加到对应的研究领域下
                field_to_keywords_map[field].update(keywords)

            processed_docs += 1

        # 将 set 转换为 list 以便 JSON 序列化
        final_map = {field: list(kw_set)
                     for field, kw_set in field_to_keywords_map.items()}

        # 定义保存路径
        output_path = os.path.join(
            settings.BASE_DIR, 'document', 'field_keyword_map.json')

        # 保存到 JSON 文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_map, f, ensure_ascii=False, indent=4)
            self.stdout.write(self.style.SUCCESS(
                f"分析完成！处理了 {processed_docs} 篇文献。"
            ))
            self.stdout.write(self.style.SUCCESS(
                f"映射关系已成功保存到: {output_path}"
            ))
        except IOError as e:
            self.stderr.write(self.style.ERROR(f"无法写入文件: {e}"))
