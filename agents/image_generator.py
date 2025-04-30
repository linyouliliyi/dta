import requests
import os
import base64
import uuid
from typing import Optional
from models.character import Character

class ImageGenerator:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/images/generations"

    def generate_image(self, scene_description: str, character: Character) -> Optional[str]:
        try:
            # 构建图片提示词
            image_prompt = f"""
            children's book illustration style,
            main character: {character.appearance},
            scene: {scene_description},
            colorful, high quality, soft lighting, warm colors, digital art
            """
            
            # 清理提示词格式
            image_prompt = ' '.join(image_prompt.split())

            # 检查 LM Studio 服务是否可用
            try:
                response = requests.get("http://localhost:1234/v1/models")
                if response.status_code != 200:
                    print("错误：无法连接到 LM Studio 服务，请确保服务已启动")
                    return None
            except requests.exceptions.ConnectionError:
                print("错误：无法连接到 LM Studio 服务，请确保服务已启动")
                return None

            # 生成图片
            response = requests.post(
                self.api_url,
                json={
                    "prompt": image_prompt,
                    "n": 1,
                    "size": "1024x1024",
                    "response_format": "b64_json"
                }
            )

            if response.status_code != 200:
                print(f"错误：生成图片失败，状态码：{response.status_code}")
                return None

            result = response.json()
            image_data = result['data'][0]['b64_json']

            # 保存图片
            image_path = f"static/images/{uuid.uuid4()}.png"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_data))

            return image_path

        except Exception as e:
            print(f"图片生成过程中发生错误: {str(e)}")
            return None 