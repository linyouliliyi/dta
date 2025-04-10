import ollama
from typing import Dict, Any, Optional
import json
import logging

class OllamaService:
    def __init__(self, model: str = "llama2"):
        self.model = model
        self.logger = logging.getLogger(__name__)
        
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        try:
            # 构建完整的提示词
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            else:
                full_prompt = prompt
                
            # 调用Ollama API
            response = ollama.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False
            )
            
            # 尝试将响应解析为JSON
            try:
                return json.loads(response['response'])
            except json.JSONDecodeError:
                return {"raw_response": response['response']}
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def generate_character_details(self, user_input: str) -> Dict[str, Any]:
        """生成角色详细信息"""
        prompt = f"""
        基于以下用户输入，创建一个详细的角色描述，以JSON格式返回：
        {user_input}
        
        返回格式示例：
        {{
            "name": "角色名称",
            "age": 年龄,
            "appearance": {{
                "physical_traits": [],
                "clothing": [],
                "distinctive_features": []
            }},
            "personality": {{
                "traits": [],
                "strengths": [],
                "weaknesses": []
            }},
            "background": "背景故事",
            "likes": [],
            "dislikes": []
        }}
        """
        return self.generate_response(prompt)
    
    def generate_story_outline(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """生成故事大纲"""
        prompt = f"""
        基于以下角色信息，创建一个儿童故事大纲，以JSON格式返回：
        {json.dumps(character, ensure_ascii=False)}
        
        返回格式示例：
        {{
            "title": "故事标题",
            "theme": "故事主题",
            "moral": "寓意",
            "scenes": [
                {{
                    "title": "场景标题",
                    "description": "场景描述",
                    "image_prompt": "场景图像提示词"
                }}
            ]
        }}
        """
        return self.generate_response(prompt)
    
    def enhance_image_prompt(self, scene_description: str) -> str:
        """优化场景的图像生成提示词"""
        prompt = f"""
        基于以下场景描述，生成详细的Stable Diffusion提示词：
        {scene_description}
        
        要求：
        1. 使用英文
        2. 包含场景的视觉细节
        3. 包含艺术风格描述
        4. 适合儿童绘本的风格
        """
        response = self.generate_response(prompt)
        return response.get('raw_response', '')