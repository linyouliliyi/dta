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
                        "description": "Detailed description of scene 1",
                        "image_prompt": "Image generation prompt for scene 1, must include character features"
                    }},
                    {{
                        "title": "Scene 2 title",
                        "description": "Detailed description of scene 2",
                        "image_prompt": "Image generation prompt for scene 2, must include character features"
                    }},
                    {{
                        "title": "Scene 3 title",
                        "description": "Detailed description of scene 3",
                        "image_prompt": "Image generation prompt for scene 3, must include character features"
                    }}
                ]
            }}
            
            Story requirements:
            1. Suitable for children
            2. Contains educational value
            3. Divided into 3-5 scenes
            4. Each scene must have detailed descriptions
            5. Please strictly follow the JSON format above
            6. All text must be in English only, no non-English characters or text
            7. image_prompt must be in English and suitable for image generation
            8. Each scene's image_prompt must include character's appearance, clothing and features
            9. Ensure character descriptions in the story match the input character information exactly
            10. Do not use any non-English characters or text in any part of the story
            """
            
            response = requests.post(
                self.api_url,
                json={
                    "messages": [
                        {"role": "system", "content": "You are a professional children's story writer. Please return data strictly in JSON format and in English only. Do not use any non-English characters or text in any part of the story."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                print(f"Error: Failed to generate story, status code: {response.status_code}")
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