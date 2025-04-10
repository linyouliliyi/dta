from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, List, Optional
import textwrap

class ImageUtils:
    def __init__(self):
        self.default_font_size = 30
        self.default_font_path = "path/to/your/font.ttf"  # 需要替换为实际字体路径
        
    def load_font(self, size: int = None) -> ImageFont.FreeTypeFont:
        """加载字体"""
        size = size or self.default_font_size
        return ImageFont.truetype(self.default_font_path, size)
    
    def resize_image(self, 
                    image_path: str, 
                    target_size: Tuple[int, int],
                    maintain_aspect: bool = True) -> Image.Image:
        """调整图像大小"""
        img = Image.open(image_path)
        
        if maintain_aspect:
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            # 创建新的白色背景图像
            new_img = Image.new('RGB', target_size, 'white')
            # 将调整后的图像粘贴到中心
            offset = ((target_size[0] - img.size[0]) // 2,
                     (target_size[1] - img.size[1]) // 2)
            new_img.paste(img, offset)
            return new_img
        else:
            return img.resize(target_size, Image.Resampling.LANCZOS)
    
    def add_text_to_image(self,
                         image: Image.Image,
                         text: str,
                         position: str = 'bottom',
                         padding: int = 20,
                         text_color: str = 'black',
                         background_color: Optional[str] = 'white',
                         max_chars_per_line: int = 40) -> Image.Image:
        """向图像添加文字"""
        draw = ImageDraw.Draw(image)
        font = self.load_font()
        
        # 文字换行
        wrapped_text = textwrap.fill(text, width=max_chars_per_line)
        lines = wrapped_text.split('\n')
        
        # 计算文字区域大小
        text_height = len(lines) * (font.size + padding)
        max_line_width = max(draw.textlength(line, font=font) for line in lines)
        
        # 创建新图像（包含文字区域）
        new_height = image.height + text_height + 2 * padding
        new_image = Image.new('RGB', (image.width, new_height), background_color)
        new_image.paste(image, (0, 0))
        
        # 添加文字
        draw = ImageDraw.Draw(new_image)
        y = image.height + padding
        for line in lines:
            x = (image.width - draw.textlength(line, font=font)) / 2
            draw.text((x, y), line, font=font, fill=text_color)
            y += font.size + padding
            
        return new_image
    
    def create_page(self,
                   image_path: str,
                   text: str,
                   page_size: Tuple[int, int] = (800, 1000)) -> Image.Image:
        """创建绘本页面"""
        # 加载并调整图像大小
        image = self.resize_image(image_path, (page_size[0], int(page_size[1] * 0.7)))
        
        # 添加文字
        return self.add_text_to_image(image, text)
    
    def create_cover(self,
                    title: str,
                    image_path: str,
                    author: str,
                    page_size: Tuple[int, int] = (800, 1000)) -> Image.Image:
        """创建绘本封面"""
        # 创建封面图像
        cover = Image.new('RGB', page_size, 'white')
        
        # 添加标题
        title_font = self.load_font(size=50)
        draw = ImageDraw.Draw(cover)
        
        # 计算标题位置
        title_width = draw.textlength(title, font=title_font)
        title_x = (page_size[0] - title_width) / 2
        draw.text((title_x, 50), title, font=title_font, fill='black')
        
        # 添加封面图像
        cover_image = self.resize_image(image_path, 
                                      (page_size[0] - 100, int(page_size[1] * 0.6)))
        cover.paste(cover_image, 
                   ((page_size[0] - cover_image.size[0]) // 2, 150))
        
        # 添加作者信息
        author_font = self.load_font(size=30)
        author_text = f"Created by: {author}"
        author_width = draw.textlength(author_text, font=author_font)
        author_x = (page_size[0] - author_width) / 2
        draw.text((author_x, page_size[1] - 100), 
                 author_text, 
                 font=author_font, 
                 fill='black')
        
        return cover