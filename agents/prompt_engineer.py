from models.character import Character
from models.story import Scene
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class PromptEngineer:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        self.character_consistency_weights = {
            "physical_traits": {
                "species": 1.5,      # 最高权重，确保物种特征
                "gender": 1.4,       # 高权重，确保性别特征
                "height": 1.3,       # 高权重，确保身高特征
                "build": 1.3,        # 高权重，确保体型特征
                "skin_tone": 1.4,    # 高权重，确保肤色特征
                "hair_color": 1.4,   # 高权重，确保发色特征
                "hair_style": 1.4,   # 高权重，确保发型特征
                "eye_color": 1.4,    # 高权重，确保眼睛颜色特征
                "age_appearance": 1.3 # 高权重，确保年龄特征
            },
            "clothing": {
                "main_outfit": 1.4,    # 高权重，确保主要服装
                "signature_item": 1.5,  # 最高权重，确保标志性物品
                "accessories": 1.3,     # 高权重，确保配饰
                "colors": 1.4          # 高权重，确保颜色特征
            },
            "distinctive_features": {
                "unique_markings": 1.5,    # 最高权重，确保独特标记
                "special_features": 1.5,   # 最高权重，确保特殊特征
                "characteristic_pose": 1.4, # 高权重，确保特征姿势
                "expression": 1.4          # 高权重，确保表情特征
            }
        }
        
    def generate_detailed_prompt(self, scene: Scene, character: Character) -> Optional[Dict[str, str]]:
        """
        Generate detailed image generation prompts based on scene and character information.
        Returns a dictionary containing both positive and negative prompts.
        """
        try:
            # Create a weighted character description that emphasizes consistent features
            character_details = []
            
            # Add physical traits with specific weights
            if character.appearance.get('physical_traits'):
                for trait in character.appearance['physical_traits']:
                    # 提取特征类型和描述
                    trait_type = trait.split(':')[0].strip().lower()
                    trait_desc = trait.split(':')[1].strip() if ':' in trait else trait
                    
                    # 获取对应的权重
                    weight = self.character_consistency_weights['physical_traits'].get(trait_type, 1.3)
                    character_details.append(f"({trait_desc}:{weight})")
            
            # Add clothing with specific weights
            if character.appearance.get('clothing'):
                for item in character.appearance['clothing']:
                    # 提取服装类型和描述
                    item_type = item.split(':')[0].strip().lower()
                    item_desc = item.split(':')[1].strip() if ':' in item else item
                    
                    # 获取对应的权重
                    weight = self.character_consistency_weights['clothing'].get(item_type, 1.2)
                    character_details.append(f"({item_desc}:{weight})")
            
            # Add distinctive features with specific weights
            if character.appearance.get('distinctive_features'):
                for feature in character.appearance['distinctive_features']:
                    # 提取特征类型和描述
                    feature_type = feature.split(':')[0].strip().lower()
                    feature_desc = feature.split(':')[1].strip() if ':' in feature else feature
                    
                    # 获取对应的权重
                    weight = self.character_consistency_weights['distinctive_features'].get(feature_type, 1.4)
                    character_details.append(f"({feature_desc}:{weight})")
            
            # Combine character details
            character_prompt = f"Character({character.name}): {', '.join(character_details)}"

            # Combine scene and character details into a compact prompt
            base_prompt = f"{scene.image_prompt}, {character_prompt}"

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

    def generate_scene_prompt(self, scene_elements: dict, character: Optional[Character] = None) -> str:
        """生成场景提示词"""
        try:
            # 打印接收到的场景元素，帮助调试
            print(f"Received scene_elements: {scene_elements}")
            
            # 构建基本提示词
            base_elements = []
            
            # 1. 角色特征部分
            if character and hasattr(character, 'appearance'):
                character_features = []
                
                # 添加物理特征
                if isinstance(character.appearance, dict) and 'physical_traits' in character.appearance:
                    for trait in character.appearance['physical_traits']:
                        trait_type = trait.split(':')[0].strip().lower()
                        trait_desc = trait.split(':')[1].strip() if ':' in trait else trait
                        weight = self.character_consistency_weights['physical_traits'].get(trait_type, 1.3)
                        character_features.append(f"({trait_desc}:{weight})")
                
                # 添加服装特征
                if isinstance(character.appearance, dict) and 'clothing' in character.appearance:
                    for item in character.appearance['clothing']:
                        item_type = item.split(':')[0].strip().lower()
                        item_desc = item.split(':')[1].strip() if ':' in item else item
                        weight = self.character_consistency_weights['clothing'].get(item_type, 1.2)
                        character_features.append(f"({item_desc}:{weight})")
                
                # 添加独特特征
                if isinstance(character.appearance, dict) and 'distinctive_features' in character.appearance:
                    for feature in character.appearance['distinctive_features']:
                        feature_type = feature.split(':')[0].strip().lower()
                        feature_desc = feature.split(':')[1].strip() if ':' in feature else feature
                        weight = self.character_consistency_weights['distinctive_features'].get(feature_type, 1.4)
                        character_features.append(f"({feature_desc}:{weight})")
                
                # 将角色特征添加到基本元素中
                if character_features:
                    base_elements.append(f"Character({character.name}) features: {', '.join(character_features)}")

            # 2. 场景描述部分
            scene_elements_list = []
            if isinstance(scene_elements, dict):
                # 获取主要描述并处理
                description = scene_elements.get('description', '').strip()
                
                # 处理主角描述
                parts = description.split(',', 1)
                if len(parts) > 1:
                    character_name = parts[0].strip()
                    rest_description = parts[1].strip()
                    character_name = character_name.replace(' is', '').replace(' was', '')
                    description = f"{character_name}, {rest_description}"
                
                scene_elements_list.extend([
                    description,
                    scene_elements.get('main_character_action', '').strip(),
                    scene_elements.get('supporting_characters', '').strip(),
                    scene_elements.get('environment', '').strip(),
                    scene_elements.get('image_prompt', '').strip()
                ])
            elif isinstance(scene_elements, str):
                scene_elements_list.append(scene_elements.strip())
            
            # 过滤并添加场景描述
            scene_description = ', '.join(
                part.strip() for part in scene_elements_list
                if part and part.strip() and part.strip() != '[]'
            )
            if scene_description:
                base_elements.append(scene_description)

            # 3. 风格要求部分
            style_elements = [
                'children\'s book illustration style',  # 基本风格
                'digital art',                         # 艺术形式
                'colorful',                           # 色彩要求
                'detailed',                           # 细节要求
                'character interaction',              # 互动要求
                'full scene'                          # 场景完整性
            ]
            base_elements.extend(style_elements)
            
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