from models.character import Character
import requests
import json
from typing import Optional
import re

class CharacterDesigner:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        self.required_features = {
            "physical_traits": [
                "species",  # 物种（人类/动物/魔法生物等）
                "gender",   # 性别
                "height",   # 身高
                "build",    # 体型
                "skin_tone", # 肤色
                "hair_color", # 发色
                "hair_style", # 发型
                "eye_color",  # 眼睛颜色
                "age_appearance" # 外表年龄特征
            ],
            "clothing": [
                "main_outfit",    # 主要服装
                "signature_item", # 标志性物品
                "accessories",    # 配饰
                "colors"          # 服装颜色
            ],
            "distinctive_features": [
                "unique_markings", # 独特标记
                "special_features", # 特殊特征
                "characteristic_pose", # 特征姿势
                "expression"      # 表情特征
            ]
        }
    
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
                "personality": "Detailed personality description",
                "appearance": {{
                    "physical_traits": [
                        "Species: [specify if human, animal, magical creature, etc.]",
                        "Gender: [specify if applicable]",
                        "Height: [specific height or relative height]",
                        "Build: [body type description]",
                        "Skin tone: [specific color]",
                        "Hair: [color, length, and style]",
                        "Eyes: [color and shape]",
                        "Age appearance: [how they look for their age]"
                    ],
                    "clothing": [
                        "Main outfit: [detailed description of primary clothing]",
                        "Signature item: [any distinctive clothing or accessory]",
                        "Accessories: [list of specific accessories]",
                        "Colors: [specific color scheme]"
                    ],
                    "distinctive_features": [
                        "Unique markings: [any special marks, scars, or patterns]",
                        "Special features: [any magical or unusual characteristics]",
                        "Characteristic pose: [how they typically stand or move]",
                        "Expression: [typical facial expression or emotion]"
                    ]
                }},
                "backstory": "Detailed background story"
            }}
            
            Important: 
            1. All text must be in English only. Do not use any non-English characters or text.
            2. The appearance should be extremely detailed and consistent, suitable for illustration.
            3. Make sure all appearance details are appropriate for the character's age and species.
            4. If the user input lacks certain appearance details, intelligently fill in appropriate details that match the character's personality and backstory.
            5. Include distinctive visual features that make the character easily recognizable and consistent across different scenes.
            6. For physical_traits, clothing, and distinctive_features, provide at least 3-5 specific details each.
            7. Ensure all details are specific and measurable to maintain consistency across illustrations.
            8. Include color descriptions for all relevant features.
            9. Always specify species, gender, hair color and style, eye color, and skin tone even if not mentioned in the input.
            10. Create a signature look that makes the character instantly recognizable.
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
                        {
                            "role": "system", 
                            "content": """You are a professional children's story character designer specializing in creating visually distinctive and consistent characters.
                            Focus on creating memorable visual features that can be maintained across different illustrations.
                            Always ensure the appearance details are comprehensive and child-friendly.
                            If any appearance aspects are not specified in the user input, intelligently generate appropriate details that align with the character's nature."""
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500
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
                    
                    # 将结构化的外貌信息转换为描述性文本
                    appearance_data = character_data.get("appearance", {})
                    appearance_text = self._format_appearance(appearance_data)
                    
                    return Character(
                        name=character_data.get("name", "未知"),
                        age=character_data.get("age", 5),
                        personality=character_data.get("personality", ""),
                        appearance=appearance_text,
                        backstory=character_data.get("backstory", "")
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

    def _format_appearance(self, appearance_data: dict) -> str:
        """Convert structured appearance data into a descriptive text"""
        if not appearance_data:
            return ""
        
        parts = []
        
        # Add species information
        if "species" in appearance_data:
            parts.append(f"This character is a {appearance_data['species']}.")
        
        # Add body information
        if "body" in appearance_data:
            body = appearance_data["body"]
            body_desc = []
            if "height" in body:
                body_desc.append(body["height"])
            if "build" in body:
                body_desc.append(body["build"])
            if body_desc:
                parts.append(" ".join(body_desc))
            if "distinguishing_features" in body:
                features = body["distinguishing_features"]
                if features:
                    parts.append("Notable features include " + ", ".join(features) + ".")
        
        # Add face information
        if "face" in appearance_data:
            face = appearance_data["face"]
            face_desc = []
            if "eyes" in face:
                face_desc.append(f"has {face['eyes']}")
            if "nose" in face:
                face_desc.append(f"with {face['nose']}")
            if "mouth" in face:
                face_desc.append(f"and {face['mouth']}")
            if face_desc:
                parts.append("The character " + ", ".join(face_desc) + ".")
            if "other_features" in face and face["other_features"]:
                parts.append("Other facial features include " + ", ".join(face["other_features"]) + ".")
        
        # Add clothing information
        if "clothing" in appearance_data:
            clothing = appearance_data["clothing"]
            if "style" in clothing:
                parts.append(f"Their style is {clothing['style']}.")
            if "main_outfit" in clothing:
                parts.append(f"They wear {clothing['main_outfit']}.")
            if "accessories" in clothing and clothing["accessories"]:
                parts.append("Accessories include " + ", ".join(clothing["accessories"]) + ".")
            if "colors" in clothing and clothing["colors"]:
                parts.append("The outfit features " + ", ".join(clothing["colors"]) + " colors.")
        
        # Add movement information
        if "movement" in appearance_data:
            parts.append(appearance_data["movement"])
        
        return " ".join(parts)

    def create_character_from_data(self, character_data):
        """Create a character from existing character data"""
        try:
            # 从现有数据创建角色，保持原始数据结构
            return Character(
                name=character_data.get('name', ''),
                age=character_data.get('age', 0),
                personality=character_data.get('personality', ''),
                appearance=character_data.get('appearance', ''),
                backstory=character_data.get('backstory', '')
            )
        except Exception as e:
            print(f"Error creating character from data: {e}")
            return None