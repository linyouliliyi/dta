from flask import Flask, render_template, request, jsonify, Response
from agents.character_designer import CharacterDesigner
from agents.story_creator import StoryCreator
from agents.art_designer import ArtDesigner
from agents.book_maker import BookMaker
import os
import traceback
import logging
import json

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化代理
character_designer = CharacterDesigner()
story_creator = StoryCreator()
art_designer = ArtDesigner("http://localhost:8188")
book_maker = BookMaker()

@app.route('/')
def index():
    return render_template('index.html')

def generate_story_stream(user_input):
    try:
        # Generate character
        logger.debug("Starting character generation...")
        yield json.dumps({"status": "generating_character"}) + "\n"
        character = character_designer.create_character(user_input)
        if not character:
            logger.error("Character generation failed")
            yield json.dumps({"error": "Character generation failed"}) + "\n"
            return
        logger.debug(f"Character generated successfully: {character}")
        yield json.dumps({"status": "character_completed"}) + "\n"
        
        # Generate story
        logger.debug("Starting story generation...")
        yield json.dumps({"status": "generating_story"}) + "\n"
        story = story_creator.create_story(character)
        if not story:
            logger.error("Story generation failed")
            yield json.dumps({"error": "Story generation failed"}) + "\n"
            return
        logger.debug(f"Story generated successfully: {story}")
        yield json.dumps({"status": "story_completed"}) + "\n"
        
        # Generate images
        logger.debug("Starting image generation...")
        scene_images = []
        for i, scene in enumerate(story.scenes):
            yield json.dumps({"status": "generating_image", "scene": i+1, "total": len(story.scenes)}) + "\n"
            logger.debug(f"Generating image for scene: {scene.title}")
            image_path = art_designer.generate_scene_image(scene, character)
            if not image_path:
                logger.error(f"Image generation failed for scene: {scene.title}")
                yield json.dumps({"error": f"Image generation failed for scene: {scene.title}"}) + "\n"
                return
            scene_images.append(image_path)
        yield json.dumps({"status": "images_completed"}) + "\n"
        
        # Generate storybook
        logger.debug("Starting storybook generation...")
        book_path = book_maker.create_book(story, scene_images)
        if not book_path:
            logger.error("Storybook generation failed")
            yield json.dumps({"error": "Storybook generation failed"}) + "\n"
            return
        logger.debug(f"Storybook generated successfully: {book_path}")
        
        # 返回结果
        logger.debug("准备返回结果...")
        yield json.dumps({
            "status": "completed",
            "character": {
                'name': character.name,
                'age': character.age,
                'appearance': character.appearance,
                'personality': character.personality,
                'background': character.background
            },
            'story': {
                'title': story.title,
                'scenes': [{
                    'title': scene.title,
                    'description': scene.description,
                    'image_path': image_path
                } for scene, image_path in zip(story.scenes, scene_images)],
                'moral': story.moral
            },
            'book_path': book_path
        }) + "\n"
        
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        logger.error(traceback.format_exc())
        yield json.dumps({"error": str(e)}) + "\n"

@app.route('/generate', methods=['POST'])
def generate_story():
    user_input = request.json.get('description', '')
    logger.debug(f"收到用户输入: {user_input}")
    return Response(generate_story_stream(user_input), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True) 