from models.character import Character
from models.story import Story, Scene
import requests
import json
from typing import Optional
import re

class StoryCreator:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
    
    def create_story(self, character: Character) -> Optional[Story]:
        try:
            prompt = f"""
            为以下角色创作一个有趣的儿童故事：
            
            角色名字：{character.name}
            年龄：{character.age}
            性格：{character.personality}
            背景：{character.background}
            
            请以JSON格式返回故事内容，格式如下：
            {{
                "title": "故事标题",
                "theme": "故事主题",
                "moral": "故事的教育意义",
                "target_age_range": [3, 8],
                "scenes": [
                    {{
                        "title": "场景1的标题",
                        "description": "场景1的详细描述",
                        "image_prompt": "场景1的图像生成提示词"
                    }},
                    {{
                        "title": "场景2的标题",
                        "description": "场景2的详细描述",
                        "image_prompt": "场景2的图像生成提示词"
                    }},
                    {{
                        "title": "场景3的标题",
                        "description": "场景3的详细描述",
                        "image_prompt": "场景3的图像生成提示词"
                    }}
                ]
            }}
            
            故事要求：
            1. 适合儿童阅读
            2. 包含教育意义
            3. 分为3-5个场景
            4. 每个场景都要有具体的描述
            5. 请严格按照上述JSON格式返回数据
            6. image_prompt 应该是英文的，适合用于图像生成的提示词
            """
            
            response = requests.post(
                self.api_url,
                json={
                    "messages": [
                        {"role": "system", "content": "你是一个专业的儿童故事作家，请严格按照JSON格式返回数据"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                print(f"错误：生成故事失败，状态码：{response.status_code}")
                return None
                
            result = response.json()
            story_text = result['choices'][0]['message']['content']
            
            # 尝试从文本中提取JSON
            try:
                # 使用正则表达式提取JSON部分
                json_match = re.search(r'\{.*\}', story_text, re.DOTALL)
                if json_match:
                    story_data = json.loads(json_match.group())
                    scenes = [
                        Scene(
                            title=scene["title"],
                            description=scene["description"],
                            image_prompt=scene["image_prompt"]
                        ) for scene in story_data["scenes"]
                    ]
                    return Story(
                        title=story_data["title"],
                        character=character,
                        scenes=scenes,
                        theme=story_data["theme"],
                        moral=story_data["moral"],
                        target_age_range=tuple(story_data["target_age_range"])
                    )
                else:
                    print("错误：无法从响应中提取JSON数据")
                    print(f"原始响应：{story_text}")
                    return None
            except json.JSONDecodeError as e:
                print(f"错误：解析故事JSON失败 - {str(e)}")
                print(f"原始响应：{story_text}")
                return None
            
        except Exception as e:
            print(f"创建故事时发生错误: {str(e)}")
            return None