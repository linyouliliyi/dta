from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from agents.character_designer import CharacterDesigner
from agents.story_creator import StoryCreator
from agents.art_designer import ArtDesigner
from agents.book_maker import BookMaker
from services.character_service import CharacterService
import os
import traceback
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 设置 Werkzeug 日志级别为 WARNING，减少不必要的输出
logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/images'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化服务和代理
character_service = CharacterService()
logger.info("Loading characters...")
character_service.load_characters()
character_designer = CharacterDesigner()
story_creator = StoryCreator()
art_designer = ArtDesigner("http://localhost:8188")
book_maker = BookMaker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/characters/random', methods=['GET'])
def get_random_character():
    logger.debug("Getting random character...")
    character, source_file = character_service.get_random_character()
    logger.debug(f"Random character data: {character}, from file: {source_file}")
    if character:
        return jsonify({
            "character": character,
            "source_file": source_file
        })
    return jsonify({"error": "No characters available"}), 404

@app.route('/characters', methods=['POST'])
def create_character():
    character_data = request.json
    if not character_data:
        return jsonify({"error": "No character data provided"}), 400
    
    try:
        character_id = character_service.create_character(character_data)
        return jsonify({"id": character_id, "character": character_data})
    except Exception as e:
        logger.error(f"Error creating character: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/characters/<character_id>', methods=['GET'])
def get_character(character_id):
    character = character_service.get_character(character_id)
    if character:
        return jsonify(character)
    return jsonify({"error": "Character not found"}), 404

def generate_story_stream(user_input, character_data=None):
    try:
        # Generate or use provided character
        logger.debug("Starting character generation...")
        yield json.dumps({"status": "generating_character"}) + "\n"
        
        if character_data:
            character = character_designer.create_character_from_data(character_data)
        else:
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
                'personality': character.personality,
                'appearance': character.appearance,
                'backstory': character.backstory
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
    character_data = request.json.get('character', None)
    logger.debug(f"收到用户输入: {user_input}")
    logger.debug(f"收到角色数据: {character_data}")
    return Response(generate_story_stream(user_input, character_data), mimetype='text/event-stream')

if __name__ == '__main__':
    # Enable Windows color support
    import os
    os.system('')  # This enables ANSI escape sequences in Windows

    # ANSI escape codes for colors
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

    print(f"\n{YELLOW}{'='*50}{END}")
    print(f"{GREEN}{BOLD}Children's Story Generator Server{END}")
    print(f"{YELLOW}{'='*50}{END}")
    print(f"\n{BOLD}Server is running at: {END}{BLUE}http://localhost:5000{END}")
    print(f"{YELLOW}Press Ctrl+C to stop the server{END}")
    print(f"{YELLOW}{'='*50}{END}\n")
    app.run(debug=True, port=5000) 