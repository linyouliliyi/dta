from models.character import Character
import requests
import json
from typing import Optional
import re

class CharacterDesigner:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
    
    def create_character(self, user_input: str) -> Optional[Character]:
        try:
            # 使用 LM Studio 生成角色特征
            prompt = f"""
            Create a children's story character based on the following user input:
            
            {user_input}
            
            Please return the character information in JSON format as follows:
            {{
                "name": "Character name",
                "age": age,
                "identity": "a young boy/a little cat/a friendly dog etc.",  # 角色身份描述
                "appearance": {{
                    "physical_traits": ["trait1", "trait2"],
                    "clothing": ["clothing1", "clothing2"],
                    "distinctive_features": ["feature1", "feature2"]
                }},
                "personality": {{
                    "traits": ["trait1", "trait2"],
                    "strengths": ["strength1", "strength2"],
                    "weaknesses": ["weakness1", "weakness2"]
                }},
                "background": "background story",
                "likes": ["like1", "like2"],
                "dislikes": ["dislike1", "dislike2"]
            }}
            
            Important: 
            1. All text must be in English only. Do not use any non-English characters or text.
            2. The identity field should clearly describe what the character is (e.g., "a young boy", "a little cat", "a friendly dog").
            3. Make sure the identity matches the physical traits and overall character concept.
            """
            
            # 检查 LM Studio 服务是否可用
            try:
                response = requests.get("http://localhost:1234/v1/models")
                if response.status_code != 200:
                    print("错误：无法连接到 LM Studio 服务，请确保服务已启动")
                    return None
            except requests.exceptions.ConnectionError:
                print("错误：无法连接到 LM Studio 服务，请确保服务已启动")
                return None
            
            # 生成角色
            response = requests.post(
                self.api_url,
                json={
                    "messages": [
                        {"role": "system", "content": "You are a professional children's story character designer. Return data in JSON format only, using English text exclusively. Do not use any non-English characters or text. Always include a clear identity description for the character."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code != 200:
                print(f"错误：生成角色失败，状态码：{response.status_code}")
                return None
                
            result = response.json()
            character_text = result['choices'][0]['message']['content']
            
            # 尝试从文本中提取JSON
            try:
                # 使用正则表达式提取JSON部分
                json_match = re.search(r'\{.*\}', character_text, re.DOTALL)
                if json_match:
                    character_data = json.loads(json_match.group())
                    return Character(
                        name=character_data.get("name", "未知"),
                        age=character_data.get("age", 5),
                        identity=character_data.get("identity", "a character"),  # 添加identity字段
                        appearance=character_data.get("appearance", {
                            "physical_traits": [],
                            "clothing": [],
                            "distinctive_features": []
                        }),
                        personality=character_data.get("personality", {
                            "traits": [],
                            "strengths": [],
                            "weaknesses": []
                        }),
                        background=character_data.get("background", ""),
                        likes=character_data.get("likes", []),
                        dislikes=character_data.get("dislikes", [])
                    )
                else:
                    print("错误：无法从响应中提取JSON数据")
                    print(f"原始响应：{character_text}")
                    return None
            except json.JSONDecodeError as e:
                print(f"错误：解析角色JSON失败 - {str(e)}")
                print(f"原始响应：{character_text}")
                return None
            
        except Exception as e:
            print(f"创建角色时发生错误: {str(e)}")
            return None