import requests
import json
import base64
import os
from typing import Dict, Any, Optional
import logging
from PIL import Image
import io

class SDService:
    def __init__(self, api_url: str = "http://localhost:8188"):
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
        
    def _load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """加载ComfyUI工作流配置"""
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: str = "",
                      width: int = 512,
                      height: int = 512,
                      steps: int = 20) -> Optional[str]:
        """生成图像"""
        try:
            # 构建基本的ComfyUI工作流
            workflow = {
                "3": {
                    "inputs": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "width": width,
                        "height": height,
                        "steps": steps
                    },
                    "class_type": "KSampler",
                    "class_defaults": {
                        "seed": -1,
                        "cfg": 7,
                        "sampler_name": "euler_ancestral",
                        "scheduler": "normal"
                    }
                }
            }
            
            # 发送请求到ComfyUI
            response = requests.post(f"{self.api_url}/queue", json=workflow)
            if response.status_code != 200:
                self.logger.error(f"Error queuing prompt: {response.text}")
                return None
                
            # 获取生成结果
            prompt_id = response.json()['prompt_id']
            
            # 等待生成完成
            while True:
                history = requests.get(f"{self.api_url}/history/{prompt_id}")
                if history.status_code == 200:
                    break
                    
            # 获取生成的图像
            output_images = history.json()['outputs']
            if output_images:
                return output_images[0]['image']  # 返回图像路径
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            return None
            
    def generate_character_image(self, 
                               character_description: Dict[str, Any],
                               style: str = "children's book illustration") -> Optional[str]:
        """生成角色图像"""
        prompt = f"""
        {style}, {character_description['appearance']['physical_traits']},
        {character_description['appearance']['clothing']},
        {character_description['appearance']['distinctive_features']},
        high quality, detailed, cute, friendly
        """
        
        negative_prompt = "ugly, scary, realistic, photographic, adult content"
        
        return self.generate_image(prompt, negative_prompt)
    
    def generate_scene_image(self, scene: Dict[str, Any]) -> Optional[str]:
        """生成场景图像"""
        return self.generate_image(
            prompt=scene['image_prompt'],
            negative_prompt="ugly, scary, realistic, photographic, adult content"
        )