from models.character import Character
from models.story import Scene
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class PromptEngineer:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        
    def generate_detailed_prompt(self, scene: Scene, character: Character) -> Optional[Dict[str, str]]:
        """
        Generate detailed image generation prompts based on scene and character information.
        Returns a dictionary containing both positive and negative prompts.
        """
        try:
            # Create a compact character description
            character_details = f"Character({character.name}): {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, distinctive features: {', '.join(character.appearance['distinctive_features'])}"

            # Combine scene and character details into a compact prompt
            base_prompt = f"{scene.image_prompt}, {character_details}"

            # Add artistic style and quality modifiers
            style_controllers = {
                "art_style": "(children's book illustration:1.3), (digital art:1.2), (cartoon:0.8)",
                "quality": "(high quality:1.2), (detailed:1.1), (sharp focus:1.2)",
                "lighting": "(soft lighting:1.1), (ambient light:0.8), (warm colors:1.0)",
                "composition": "(rule of thirds:1.1), (centered composition:0.9)",
                "mood": "(cheerful:1.2), (whimsical:1.1), (playful:1.0)",
                "language": "(english text only:1.3), (no chinese characters:1.3), (no asian text:1.3)"
            }
            
            # Combine all elements into a single, compact prompt
            final_positive_prompt = f"{base_prompt}, {style_controllers['art_style']}, {style_controllers['quality']}, {style_controllers['lighting']}, {style_controllers['composition']}, {style_controllers['mood']}, {style_controllers['language']}"

            # Create a compact negative prompt
            negative_prompt = "deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, disconnected limbs, mutation, ugly, disgusting, blurry, fuzzy, out of focus, bad art, watermark, signature, text, chinese characters, asian text, non-english text"

            return {
                "positive_prompt": final_positive_prompt.replace('\n', ' ').replace('  ', ' ').strip(),
                "negative_prompt": negative_prompt
            }

        except Exception as e:
            logger.error(f"Error generating detailed prompt: {str(e)}")
            return None

    def _format_positive_prompt(self, prompt_details: Dict) -> str:
        """Format the positive prompt with proper weighting and organization"""
        elements = [
            prompt_details['style_guide'],
            prompt_details['composition'],
            prompt_details['lighting'],
            prompt_details['positive_prompt'],
            prompt_details['additional_details']
        ]
        return ", ".join([e for e in elements if e])

    def _format_negative_prompt(self, prompt_details: Dict) -> str:
        """Format the negative prompt with standard exclusions"""
        standard_negatives = [
            "deformed", "distorted", "disfigured", "poorly drawn", "bad anatomy",
            "wrong anatomy", "extra limb", "missing limb", "floating limbs",
            "disconnected limbs", "mutation", "ugly", "disgusting", "blurry", "fuzzy"
        ]
        
        custom_negatives = prompt_details['negative_prompt'].split(",")
        all_negatives = standard_negatives + [neg.strip() for neg in custom_negatives]
        
        return ", ".join(all_negatives)

    def generate_scene_prompt(self, scene_elements: dict) -> str:
        """生成场景提示词"""
        try:
            # 打印接收到的场景元素，帮助调试
            print(f"Received scene_elements: {scene_elements}")
            
            # 获取场景描述
            scene_description = ""
            if isinstance(scene_elements, dict):
                # 获取主要描述并处理
                description = scene_elements.get('description', '').strip()
                
                # 处理主角描述
                # 找到第一个逗号前的主角名字
                parts = description.split(',', 1)
                if len(parts) > 1:
                    character_name = parts[0].strip()
                    rest_description = parts[1].strip()
                    
                    # 如果主角名字后面有"is"或"was"，去掉它们
                    character_name = character_name.replace(' is', '').replace(' was', '')
                    
                    # 重组描述，使其更自然
                    description = f"{character_name}, {rest_description}"
                
                # 获取其他元素
                main_character_action = scene_elements.get('main_character_action', '').strip()
                supporting_characters = scene_elements.get('supporting_characters', '').strip()
                environment = scene_elements.get('environment', '').strip()
                image_prompt = scene_elements.get('image_prompt', '').strip()
                
                # 组合所有描述，过滤掉空字符串、None、[]等
                scene_description = ', '.join([
                    part.strip() for part in [
                        description,
                        main_character_action,
                        supporting_characters,
                        environment,
                        image_prompt
                    ] if part and part.strip() and part.strip() != '[]'
                ])
            elif isinstance(scene_elements, str):
                scene_description = scene_elements.strip()
                
            # 确保场景描述是字符串并清理格式
            scene_description = str(scene_description).strip()
            # 清理连续的逗号和空格
            scene_description = ', '.join(
                part.strip() for part in scene_description.split(',')
                if part.strip() and part.strip() != '[]'
            )
            print(f"Processed scene_description: {scene_description}")
            
            # 构建基本提示词
            base_elements = [
                scene_description,  # 完整的场景描述
                'children\'s book illustration style',  # 风格
                'digital art',  # 艺术形式
                'colorful',  # 色彩
                'detailed',  # 细节
                'character interaction',  # 角色互动
                'full scene'  # 完整场景
            ]
            
            # 移除空的部分并连接，确保清理格式
            full_prompt = ', '.join(
                part.strip() for part in base_elements
                if part and part.strip() and part.strip() != '[]'
            )
            
            # 最后清理一次连续的逗号和空格
            full_prompt = ', '.join(
                part.strip() for part in full_prompt.split(',')
                if part.strip() and part.strip() != '[]'
            )
            
            print(f"Generated prompt: {full_prompt}")
            return full_prompt
            
        except Exception as e:
            print(f"Error generating scene prompt: {str(e)}")
            print(f"scene_elements type: {type(scene_elements)}")
            print(f"scene_elements content: {scene_elements}")
            return ""

    def generate_negative_prompt(self) -> str:
        """生成负面提示词"""
        return "ugly, scary, realistic, photographic, adult content, deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, disconnected limbs, mutation, blurry, fuzzy, out of focus, bad art, watermark, signature, text, chinese characters, asian text, non-english text, empty background, isolated character, single character, no interaction, static pose" 