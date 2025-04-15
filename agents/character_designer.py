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
            基于以下用户输入，创建一个儿童故事角色：
            
            {user_input}
            
            请以JSON格式返回角色信息，格式如下：
            {{
                "name": "角色名称",
                "age": 年龄,
                "appearance": {{
                    "physical_traits": ["特征1", "特征2"],
                    "clothing": ["服装1", "服装2"],
                    "distinctive_features": ["特点1", "特点2"]
                }},
                "personality": {{
                    "traits": ["性格特点1", "性格特点2"],
                    "strengths": ["优点1", "优点2"],
                    "weaknesses": ["缺点1", "缺点2"]
                }},
                "background": "背景故事",
                "likes": ["喜欢的东西1", "喜欢的东西2"],
                "dislikes": ["不喜欢的东西1", "不喜欢的东西2"]
            }}
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
                        {"role": "system", "content": "你是一个专业的儿童故事角色设计师，请严格按照JSON格式返回数据"},
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