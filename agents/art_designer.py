from models.character import Character
from models.story import Scene
import requests
import os
from typing import Optional
from datetime import datetime
from services.sd_service import SDService
from agents.prompt_engineer import PromptEngineer

class ArtDesigner:
    def __init__(self, comfyui_api_url: str):
        self.sd_service = SDService(api_url=comfyui_api_url)
        self.prompt_engineer = PromptEngineer()
        self.output_dir = "static/images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_scene_image(self, scene: Scene, character: Character) -> Optional[str]:
        """生成场景图片"""
        try:
            # 使用 PromptEngineer 生成提示词
            scene_elements = {
                'description': scene.description,
                'title': scene.title,
                'image_prompt': scene.image_prompt
            }
            
            # 获取正向和负向提示词
            full_prompt = self.prompt_engineer.generate_scene_prompt(scene_elements)
            negative_prompt = self.prompt_engineer.generate_negative_prompt()
            
            # 生成图片
            image_path = self.sd_service.generate_image(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                width=1000,
                height=600,
                steps=20
            )
            
            if not image_path:
                print("Error: Failed to generate image")
                return None
            
            # 保存图片
            safe_title = ''.join(e for e in scene.title if e.isalnum() or e in ('_', '-'))
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(self.output_dir, f"scene_{safe_title}_{timestamp}.png")
            
            with open(output_path, "wb") as f:
                f.write(requests.get(f"{self.sd_service.api_url}/view?filename={image_path}").content)
            
            return f"/static/images/{os.path.basename(output_path)}"
            
        except Exception as e:
            print(f"Error occurred while generating scene image: {str(e)}")
            return None 