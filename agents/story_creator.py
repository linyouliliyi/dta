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
            response = requests.get("http://localhost:1234/v1/models", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"API服务不可用: {str(e)}")
            return False

    def _make_api_request(self, prompt: str) -> Optional[dict]:
        """发送API请求并处理重试逻辑"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a professional children's story writer. Return data in JSON format only, using English text exclusively."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=30  # 设置较长的超时时间
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"API请求失败 (尝试 {attempt + 1}/{self.max_retries}): 状态码 {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"API请求异常 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
            
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return None
    
    def create_story(self, character: Character) -> Optional[Story]:
        try:
            # 构建角色描述
            character_description = f"""
            Character Information:
            Name: {character.name}
            Age: {character.age}
            Personality: {character.personality}
            Appearance: {character.appearance}
            Backstory: {character.backstory}
            """

            # 构建提示词
            prompt = f"""
            Create a children's story based on the following character:
            
            {character_description}
            
            Please follow these guidelines in order:

            1. Character Features (Must be consistent throughout the story):
               - Maintain the character's appearance, personality, and traits
               - Keep the character's age-appropriate behavior
               - Ensure the character's actions align with their personality
               - Preserve the character's unique characteristics in each scene

            2. Scene Development (Create 3-5 engaging scenes):
               - Each scene should showcase the character's personality
               - Include clear visual descriptions for image generation
               - Create a logical progression from beginning to end
               - Ensure each scene builds upon the previous one
               - Include meaningful character interactions and development

            3. Story Requirements:
               - Clear and appropriate theme for children
               - Age-appropriate content and language
               - Engaging and educational value
               - Meaningful moral lesson
               - Proper story structure (beginning, middle, end)

            Please return the story in JSON format as follows:
            {{
                "title": "Story title",
                "theme": "The main theme of the story (e.g., friendship, courage, kindness)",
                "target_age_range": "The target age range for the story (e.g., 4-8, 6-10)",
                "scenes": [
                    {{
                        "title": "Scene 1 title",
                        "description": "Detailed description of scene 1",
                        "image_prompt": "Detailed prompt for generating an image of scene 1"
                    }},
                    {{
                        "title": "Scene 2 title",
                        "description": "Detailed description of scene 2",
                        "image_prompt": "Detailed prompt for generating an image of scene 2"
                    }},
                    {{
                        "title": "Scene 3 title",
                        "description": "Detailed description of scene 3",
                        "image_prompt": "Detailed prompt for generating an image of scene 3"
                    }}
                ],
                "moral": "The moral of the story"
            }}
            
            Important:
            1. All text must be in English only.
            2. Each scene must include an image_prompt that describes how the scene should look visually.
            3. Make sure to return valid JSON format with proper quotes and commas.
            4. Do not include any explanatory text outside the JSON structure.
            """

            # 检查 LM Studio 服务是否可用
            if not self._check_api_availability():
                logger.error("无法连接到 LM Studio 服务，请确保服务已启动")
                return None

            # 生成故事
            result = self._make_api_request(prompt)
            if not result:
                logger.error("多次尝试后仍无法生成故事")
                return None

            story_text = result['choices'][0]['message']['content']

            # 尝试从文本中提取JSON
            try:
                # 使用正则表达式提取JSON部分
                json_match = re.search(r'\{[\s\S]*\}', story_text)
                if json_match:
                    story_data = json.loads(json_match.group())
                    
                    # 验证必要的字段
                    if not all(key in story_data for key in ['title', 'theme', 'scenes', 'moral', 'target_age_range']):
                        logger.error("故事数据缺少必要字段")
                        return None
                    
                    # 验证场景数据
                    if not isinstance(story_data['scenes'], list) or not story_data['scenes']:
                        logger.error("场景数据格式不正确")
                        return None
                    
                    # 验证每个场景的必要字段
                    for scene in story_data['scenes']:
                        if not all(key in scene for key in ['title', 'description', 'image_prompt']):
                            logger.error("场景数据缺少必要字段")
                            return None
                    
                    story = Story(
                        title=story_data['title'],
                        character=character,
                        theme=story_data['theme'],
                        target_age_range=story_data['target_age_range'],
                        scenes=[
                            Scene(
                                title=scene['title'],
                                description=scene['description'],
                                image_prompt=scene['image_prompt']
                            )
                            for scene in story_data['scenes']
                        ],
                        moral=story_data['moral']
                    )
                    logger.info(f"故事生成成功：{story.title}")
                    return story
                else:
                    logger.error("无法从响应中提取JSON数据")
                    logger.debug(f"原始响应：{story_text}")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"解析故事JSON失败: {str(e)}")
                logger.debug(f"原始响应：{story_text}")
                return None

        except Exception as e:
            logger.error(f"故事生成过程中发生错误: {str(e)}")
            return None