from models.character import Character
from models.story import Scene
import json
import requests
from PIL import Image
import os
from typing import Optional
from datetime import datetime
import time

class ArtDesigner:
    def __init__(self, comfyui_api_url: str):
        self.api_url = comfyui_api_url
        # 修改输出目录为static/images，这样Flask可以直接提供这些文件
        self.output_dir = "static/images"
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
            
            # 返回相对于static目录的路径，这样Flask可以直接提供这个文件
            return os.path.relpath(image_path, "static")
            
        except Exception as e:
            print(f"生成角色图片时发生错误: {str(e)}")
            return None
            
    def generate_scene_image(self, scene: Scene, character: Character) -> Optional[str]:
        try:
            # 检查角色信息的完整性
            if not character.appearance or not all(key in character.appearance for key in ['physical_traits', 'clothing', 'distinctive_features']):
                print("警告：角色信息不完整，可能影响图片生成效果")
            
            # 检查ComfyUI服务是否可用
            try:
                response = requests.get(f"{self.api_url}/history")
                if response.status_code != 200:
                    print(f"错误：无法连接到ComfyUI服务，状态码: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    return None
            except requests.exceptions.ConnectionError as e:
                print(f"错误：无法连接到ComfyUI服务: {str(e)}")
                return None
            
            # 构建角色特征描述
            character_description = f"""
            角色特征：
            - 身体特征：{', '.join(character.appearance['physical_traits'])}
            - 服装：{', '.join(character.appearance['clothing'])}
            - 显著特点：{', '.join(character.appearance['distinctive_features'])}
            """
            
            # 构建完整的场景提示词，包含角色特征
            full_prompt = f"{scene.image_prompt}\n\n{character_description}"
            print(f"生成场景图片，场景标题: {scene.title}")
            print(f"提示词: {full_prompt}")
            
            # 构建ComfyUI工作流
            workflow = {
                "prompt": {
                    "1": {
                        "inputs": {
                            "ckpt_name": "sd_xl_base_1.0.safetensors"
                        },
                        "class_type": "CheckpointLoaderSimple",
                        "_meta": {
                            "title": "Load Checkpoint"
                        }
                    },
                    "2": {
                        "inputs": {
                            "width": 768,
                            "height": 768,
                            "batch_size": 1
                        },
                        "class_type": "EmptyLatentImage",
                        "_meta": {
                            "title": "Empty Latent Image"
                        }
                    },
                    "3": {
                        "inputs": {
                            "lora_name": "COOLKIDS_MERGE_V2.5.safetensors",
                            "strength_model": 0.75,
                            "strength_clip": 1,
                            "model": ["1", 0],
                            "clip": ["1", 1]
                        },
                        "class_type": "LoraLoader",
                        "_meta": {
                            "title": "Load LoRA"
                        }
                    },
                    "4": {
                        "inputs": {
                            "text": full_prompt,
                            "clip": ["3", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {
                            "title": "CLIP Text Encode (Prompt)"
                        }
                    },
                    "5": {
                        "inputs": {
                            "text": "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face",
                            "clip": ["3", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {
                            "title": "CLIP Text Encode (Prompt)"
                        }
                    },
                    "6": {
                        "inputs": {
                            "seed": 530938972832347,
                            "steps": 30,
                            "cfg": 7,
                            "sampler_name": "dpmpp_2m",
                            "scheduler": "karras",
                            "denoise": 1,
                            "model": ["3", 0],
                            "positive": ["4", 0],
                            "negative": ["5", 0],
                            "latent_image": ["2", 0]
                        },
                        "class_type": "KSampler",
                        "_meta": {
                            "title": "KSampler"
                        }
                    },
                    "7": {
                        "inputs": {
                            "samples": ["6", 0],
                            "vae": ["1", 2]
                        },
                        "class_type": "VAEDecode",
                        "_meta": {
                            "title": "VAE Decode"
                        }
                    },
                    "8": {
                        "inputs": {
                            "filename_prefix": "scene_",
                            "images": ["7", 0]
                        },
                        "class_type": "SaveImage",
                        "_meta": {
                            "title": "Save Image"
                        }
                    }
                }
            }
            
            # 发送请求到ComfyUI
            print("正在发送请求到ComfyUI...")
            response = requests.post(f"{self.api_url}/prompt", json=workflow)
            if response.status_code != 200:
                print(f"错误：生成图片失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return None
                
            # 获取生成结果
            prompt_id = response.json()['prompt_id']
            print(f"图片生成任务已创建，ID: {prompt_id}")
            
            # 等待生成完成
            max_retries = 30  # 最多等待30秒
            retry_count = 0
            while retry_count < max_retries:
                print(f"等待图片生成完成... ({retry_count + 1}/{max_retries})")
                history = requests.get(f"{self.api_url}/history/{prompt_id}")
                if history.status_code == 200:
                    history_data = history.json()
                    if prompt_id in history_data:
                        outputs = history_data[prompt_id]['outputs']
                        if outputs:
                            # 获取生成的图像
                            image_data = outputs['8']['images'][0]
                            # 移除标题中的所有空格和特殊字符
                            safe_title = ''.join(e for e in scene.title if e.isalnum() or e in ('_', '-'))
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            image_filename = f"scene_{safe_title}_{timestamp}.png"
                            image_path = os.path.join(self.output_dir, image_filename)
                            
                            # 确保输出目录存在
                            os.makedirs(os.path.dirname(image_path), exist_ok=True)
                            
                            # 下载并保存图片
                            print(f"正在下载生成的图片: {image_data['filename']}")
                            image_response = requests.get(f"{self.api_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}")
                            if image_response.status_code == 200:
                                with open(image_path, "wb") as f:
                                    f.write(image_response.content)
                                print(f"图片已保存到: {image_path}")
                                # 返回包含/static前缀的路径，使用正斜杠作为分隔符
                                relative_path = os.path.relpath(image_path, "static").replace("\\", "/")
                                return f"/static/{relative_path}"
                            else:
                                print(f"错误：下载图片失败，状态码: {image_response.status_code}")
                                print(f"响应内容: {image_response.text}")
                time.sleep(1)  # 等待1秒
                retry_count += 1
                
            print("错误：图片生成超时")
            return None
            
        except Exception as e:
            print(f"生成场景图片时发生错误: {str(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return None