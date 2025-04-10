from models.character import Character
from models.story import Story, Scene
import ollama
import json
from typing import Optional
import re

class StoryCreator:
    def __init__(self):
        self.model = "llama2"
    
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
                "scenes": [
                    {{
                        "description": "场景1的详细描述"
                    }},
                    {{
                        "description": "场景2的详细描述"
                    }},
                    {{
                        "description": "场景3的详细描述"
                    }}
                ],
                "moral": "故事的教育意义"
            }}
            
            故事要求：
            1. 适合儿童阅读
            2. 包含教育意义
            3. 分为3-5个场景
            4. 每个场景都要有具体的描述
            """
            
            response = ollama.generate(model=self.model, prompt=prompt)
            
            # 尝试从响应中提取JSON
            try:
                # 使用正则表达式提取JSON部分
                json_match = re.search(r'\{.*\}', response['response'], re.DOTALL)
                if json_match:
                    story_data = json.loads(json_match.group())
                else:
                    print("错误：无法从响应中提取JSON数据")
                    return None
            except json.JSONDecodeError as e:
                print(f"错误：解析JSON失败 - {str(e)}")
                return None
            
            # 创建Story对象
            scenes = [Scene(description=scene["description"]) 
                     for scene in story_data["scenes"]]
            
            return Story(
                title=story_data["title"],
                scenes=scenes,
                moral=story_data["moral"]
            )
            
        except Exception as e:
            print(f"创建故事时发生错误: {str(e)}")
            return None