from dataclasses import dataclass
from typing import List, Optional
from models.character import Character

@dataclass
class Scene:
    title: str
    description: str
    image_prompt: str
    image_path: Optional[str] = None

@dataclass
class Story:
    title: str
    character: Character
    scenes: List[Scene]
    theme: str
    moral: str
    target_age_range: tuple
    
    def add_scene(self, scene: Scene):
        self.scenes.append(scene)
    
    def get_total_scenes(self) -> int:
        return len(self.scenes)
    
    def to_dict(self):
        return {
            "title": self.title,
            "character": {
                "name": self.character.name,
                "age": self.character.age,
                "appearance": self.character.appearance,
                "personality": self.character.personality
            },
            "scenes": [
                {
                    "title": scene.title,
                    "description": scene.description,
                    "image_prompt": scene.image_prompt,
                    "image_path": scene.image_path
                }
                for scene in self.scenes
            ],
            "theme": self.theme,
            "moral": self.moral,
            "target_age_range": self.target_age_range
        }

    def __str__(self) -> str:
        scenes_text = "\n\n".join([f"场景 {i+1}:\n{scene.description}" 
                                 for i, scene in enumerate(self.scenes)])
        return f"""故事标题：{self.title}

{scenes_text}

教育意义：{self.moral}"""