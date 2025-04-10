from agents.character_designer import CharacterDesigner
from agents.art_designer import ArtDesigner
from agents.story_creator import StoryCreator
from agents.book_maker import BookMaker

class StoryWorldSystem:
    def __init__(self):
        self.character_designer = CharacterDesigner()
        self.art_designer = ArtDesigner("http://localhost:8188")  # ComfyUI默认端口
        self.story_creator = StoryCreator()
        self.book_maker = BookMaker()
    
    def create_story_book(self, user_input: str):
        # 1. 创建角色
        character = self.character_designer.create_character(user_input)
        
        # 2. 生成角色图像
        character_image = self.art_designer.generate_character_image(character)
        
        # 3. 创建故事
        story = self.story_creator.create_story(character)
        
        # 4. 为故事场景生成配图
        scene_images = []
        for scene in story.scenes:
            image = self.art_designer.generate_scene_image(scene)
            scene_images.append(image)
        
        # 5. 制作绘本
        book_path = self.book_maker.create_book(story, scene_images)
        
        return book_path

if __name__ == "__main__":
    system = StoryWorldSystem()
    book_path = system.create_story_book("""
    我想创建一个喜欢探险的小猫角色，
    它有着蓝色的毛发和大大的眼睛，
    性格活泼开朗，喜欢帮助他人。
    """)
    print(f"绘本已生成：{book_path}")