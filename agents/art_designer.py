from models.character import Character
import json
import requests
from PIL import Image
import os
from typing import Optional
from datetime import datetime

class ArtDesigner:
    def __init__(self, comfyui_api_url: str):
        self.api_url = comfyui_api_url
        self.output_dir = "output/images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_character_image(self, character: Character) -> Optional[str]:
        try:
            # 构建角色描述
            description = f"""
            一个{character.age}岁的角色，
            外表特征：{character.appearance}
            性格特点：{character.personality}
            """
            
            # 检查ComfyUI服务是否可用
            try:
                response = requests.get(f"{self.api_url}/history")
                if response.status_code != 200:
                    print("错误：无法连接到ComfyUI服务，请确保服务已启动")
                    return None
            except requests.exceptions.ConnectionError:
                print("错误：无法连接到ComfyUI服务，请确保服务已启动")
                return None
            
            # 调用ComfyUI API
            # 这里需要根据你的ComfyUI配置来调整
            workflow = {
                # ComfyUI工作流配置
            }
            
            response = requests.post(f"{self.api_url}/queue", json=workflow)
            if response.status_code != 200:
                print("错误：生成图片失败")
                return None
            
            # 生成图片文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.output_dir, f"character_{timestamp}.png")
            
            # 保存图片
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            return image_path
            
        except Exception as e:
            print(f"生成角色图片时发生错误: {str(e)}")
            return None