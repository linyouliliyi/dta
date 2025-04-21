from models.story import Story
from PIL import Image
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from typing import List
from datetime import datetime

class BookMaker:
    def __init__(self):
        self.page_size = A4
        self.margin = inch
        self.line_height = 14
        self.font_size = 12
        self.output_dir = "output/books"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def create_book(self, story: Story, images: List[str]) -> str:
        try:
            # 生成PDF文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = os.path.join(self.output_dir, f"story_{timestamp}.pdf")
            
            # 创建PDF
            c = canvas.Canvas(pdf_path, pagesize=self.page_size)
            
            # 设置字体
            c.setFont("Helvetica", self.font_size)
            
            # 添加封面
            self._add_cover(c, story.title)
            c.showPage()
            
            # 添加故事内容
            for i, (scene, image_path) in enumerate(zip(story.scenes, images)):
                # 添加场景标题
                c.setFont("Helvetica-Bold", self.font_size + 2)
                c.drawString(self.margin, self.page_size[1] - self.margin, 
                           f"场景 {i+1}")
                
                # 添加图片
                y = self.page_size[1] - self.margin - self.line_height * 2  # 初始化y坐标
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    # 调整图片大小以适应页面
                    img_width, img_height = img.size
                    max_width = self.page_size[0] - 2 * self.margin
                    max_height = self.page_size[1] / 2
                    
                    scale = min(max_width / img_width, max_height / img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # 居中显示图片
                    x = (self.page_size[0] - new_width) / 2
                    y = self.page_size[1] - self.margin - new_height
                    c.drawImage(image_path, x, y, width=new_width, height=new_height)
                
                # 添加场景描述
                c.setFont("Helvetica", self.font_size)
                y = y - self.line_height * 2  # 在图片下方留出空间
                for line in textwrap.wrap(scene.description, width=60):
                    c.drawString(self.margin, y, line)
                    y -= self.line_height
                
                c.showPage()
            
            # 添加教育意义页面
            c.setFont("Helvetica-Bold", self.font_size + 2)
            c.drawString(self.margin, self.page_size[1] - self.margin, 
                        "这个故事告诉我们：")
            c.setFont("Helvetica", self.font_size)
            y = self.page_size[1] - self.margin - self.line_height * 2
            for line in textwrap.wrap(story.moral, width=60):
                c.drawString(self.margin, y, line)
                y -= self.line_height
            
            # 保存PDF
            c.save()
            return pdf_path
            
        except Exception as e:
            print(f"创建绘本时发生错误: {str(e)}")
            return ""
    
    def _add_cover(self, c, title):
        """添加封面"""
        c.setFont("Helvetica-Bold", 24)
        # 居中显示标题
        text_width = c.stringWidth(title, "Helvetica-Bold", 24)
        x = (self.page_size[0] - text_width) / 2
        y = self.page_size[1] / 2
        c.drawString(x, y, title)