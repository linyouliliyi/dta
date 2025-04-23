from models.character import Character
from models.story import Story, Scene
import requests
import json
from typing import Optional
import re
import logging
import time

logger = logging.getLogger(__name__)

class StoryCreator:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _check_api_availability(self) -> bool:
        """检查API服务是否可用"""
        try:
            response = requests.get(self.api_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"API服务不可用: {str(e)}")
            return False
    
    def create_story(self, character: Character) -> Optional[Story]:
        # 检查API服务是否可用
        if not self._check_api_availability():
            logger.error("故事生成API服务不可用")
            return None
            
        for attempt in range(self.max_retries):
            try:
                prompt = f"""
                Create an interesting children's story for the following character:
                
                Character information:
                - Name: {character.name}
                - Age: {character.age}
                - Appearance: {', '.join(character.appearance['physical_traits'])}
                - Clothing: {', '.join(character.appearance['clothing'])}
                - Features: {', '.join(character.appearance['distinctive_features'])}
                - Personality: {', '.join(character.personality['traits'])}
                - Background: {character.background}
                
                Please return the story content in JSON format as follows:
                {{
                    "title": "Story title",
                    "theme": "Story theme",
                    "moral": "Educational value of the story",
                    "target_age_range": [3, 8],
                    "scenes": [
                        {{
                            "title": "Scene 1 title",
                            "description": "Detailed description of scene 1, including supporting characters and their actions",
                            "supporting_characters": "Description of supporting characters in this scene",
                            "main_character_action": "Detailed description of main character's action and expression",
                            "environment": "Description of the scene environment",
                            "image_prompt": "children's book illustration style, {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}, detailed scene description, colorful, high quality, soft lighting, warm colors, digital art"
                        }},
                        {{
                            "title": "Scene 2 title",
                            "description": "Detailed description of scene 2, including supporting characters and their actions",
                            "supporting_characters": "Description of supporting characters in this scene",
                            "main_character_action": "Detailed description of main character's action and expression",
                            "environment": "Description of the scene environment",
                            "image_prompt": "children's book illustration style, {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}, detailed scene description, colorful, high quality, soft lighting, warm colors, digital art"
                        }},
                        {{
                            "title": "Scene 3 title",
                            "description": "Detailed description of scene 3, including supporting characters and their actions",
                            "supporting_characters": "Description of supporting characters in this scene",
                            "main_character_action": "Detailed description of main character's action and expression",
                            "environment": "Description of the scene environment",
                            "image_prompt": "children's book illustration style, {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}, detailed scene description, colorful, high quality, soft lighting, warm colors, digital art"
                        }}
                    ]
                }}
                
                Story requirements:
                1. Suitable for children
                2. Contains educational value
                3. Divided into 3-5 scenes
                4. Each scene must have:
                   - At least one supporting character (friend, family member, teacher, etc.)
                   - Clear description of the main character's actions and expressions
                   - Detailed environment description
                   - Interaction between characters
                5. Please strictly follow the JSON format above
                6. All text must be in English only, no non-English characters or text
                7. image_prompt must be in English and suitable for image generation
                8. Each scene's image_prompt must include:
                   - Main character's appearance, clothing and features
                   - Supporting characters' descriptions
                   - Main character's action and expression
                   - Scene environment details
                9. Ensure character descriptions in the story match the input character information exactly
                10. Do not use any non-English characters or text in any part of the story
                """
                
                logger.info("Sending story generation request to API...")
                response = requests.post(
                    self.api_url,
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a professional children's story writer. Please return data strictly in JSON format and in English only. Do not use any non-English characters or text in any part of the story."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=30  # 设置超时时间
                )
                
                if response.status_code != 200:
                    logger.error(f"故事生成API请求失败，状态码: {response.status_code}")
                    logger.error(f"响应内容: {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                    
                result = response.json()
                story_text = result['choices'][0]['message']['content']
                
                # 尝试从文本中提取JSON
                try:
                    # 使用正则表达式提取JSON部分
                    json_match = re.search(r'\{.*\}', story_text, re.DOTALL)
                    if json_match:
                        story_data = json.loads(json_match.group())
                        scenes = []
                        for scene in story_data["scenes"]:
                            # 构建更详细的图片提示词
                            scene_description = scene["description"]
                            supporting_characters = scene.get("supporting_characters", "")
                            main_character_action = scene.get("main_character_action", "")
                            environment = scene.get("environment", "")
                            
                            image_prompt = f"""
                            children's book illustration style,
                            main character: {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}, {main_character_action},
                            supporting characters: {supporting_characters},
                            environment: {environment},
                            colorful, high quality, soft lighting, warm colors, digital art
                            """
                            
                            # 清理提示词格式
                            image_prompt = ' '.join(image_prompt.split())
                            
                            scenes.append(Scene(
                                title=scene["title"],
                                description=scene_description,
                                image_prompt=image_prompt
                            ))
                            
                        logger.info("故事生成成功")
                        return Story(
                            title=story_data["title"],
                            character=character,
                            scenes=scenes,
                            theme=story_data["theme"],
                            moral=story_data["moral"],
                            target_age_range=tuple(story_data["target_age_range"])
                        )
                    else:
                        logger.error("无法从响应中提取JSON数据")
                        logger.error(f"原始响应: {story_text}")
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay)
                            continue
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"解析故事JSON失败: {str(e)}")
                    logger.error(f"原始响应: {story_text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
            except requests.exceptions.RequestException as e:
                logger.error(f"故事生成请求异常: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
            except Exception as e:
                logger.error(f"故事生成过程中发生错误: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
        
        logger.error("故事生成失败，已达到最大重试次数")
        return None