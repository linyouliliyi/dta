import requests
import json
import base64
import os
from typing import Dict, Any, Optional
import logging
from PIL import Image
import io
import time

class SDService:
    def __init__(self, api_url: str = "http://localhost:8188", workflow_path: str = "workflows/default_workflow.json"):
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
        self.workflow_path = workflow_path
        self.workflow = self._load_workflow()
        
    def _load_workflow(self) -> Dict[str, Any]:
        """加载ComfyUI工作流配置"""
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading workflow: {str(e)}")
            raise
    
    def generate_image(self, 
                      prompt: str, 
                      negative_prompt: str = "",
                      width: int = 1000,
                      height: int = 600,
                      steps: int = 12) -> Optional[str]:
        """生成图像"""
        try:
            # 复制工作流配置
            workflow = {"prompt": self.workflow.copy()}
            
            # 更新工作流参数
            workflow["prompt"]["5"]["inputs"]["width"] = 504  # 初始潜在空间尺寸
            workflow["prompt"]["5"]["inputs"]["height"] = 304
            workflow["prompt"]["10"]["inputs"]["width"] = width  # 上采样后的尺寸
            workflow["prompt"]["10"]["inputs"]["height"] = height
            workflow["prompt"]["3"]["inputs"]["steps"] = steps
            workflow["prompt"]["6"]["inputs"]["text"] = prompt
            workflow["prompt"]["7"]["inputs"]["text"] = negative_prompt
            
            # 发送请求到ComfyUI
            self.logger.info("Sending request to ComfyUI...")
            response = requests.post(f"{self.api_url}/prompt", json=workflow)
            if response.status_code != 200:
                self.logger.error(f"Error queuing prompt: {response.text}")
                return None
                
            # 获取生成结果
            prompt_id = response.json()['prompt_id']
            self.logger.info(f"Generation started with prompt_id: {prompt_id}")
            
            # 等待生成完成
            max_retries = 250  # 最多等待250秒
            retry_count = 0
            while retry_count < max_retries:
                try:
                    history = requests.get(f"{self.api_url}/history/{prompt_id}")
                    if history.status_code == 200:
                        history_data = history.json()
                        if prompt_id in history_data:
                            outputs = history_data[prompt_id]['outputs']
                            if outputs:
                                # 获取生成的图像
                                image_data = outputs['12']['images'][0]
                                return image_data['filename']
                    elif history.status_code == 404:
                        self.logger.info(f"Generation in progress... ({retry_count + 1}/{max_retries})")
                    else:
                        self.logger.error(f"Error checking history: {history.status_code} - {history.text}")
                except Exception as e:
                    self.logger.error(f"Error while checking history: {str(e)}")
                
                time.sleep(1)  # 等待1秒
                retry_count += 1
            
            self.logger.error("Generation timed out")
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
        # 确保提示词格式正确
        prompt = scene['image_prompt'].replace('\n', ' ').strip()
        negative_prompt = scene.get('negative_prompt', "ugly, scary, realistic, photographic, adult content")
        
        # 添加额外的质量控制参数
        return self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            cfg_scale=7.5,  # 增加提示词权重
            sampler_name="DPM++ 2M Karras",  # 使用更好的采样器
            steps=20,  # 增加步数
            width=1000,
            height=600
        )