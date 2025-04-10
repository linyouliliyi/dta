from flask import Flask, render_template, request, jsonify
from agents.character_designer import CharacterDesigner
from agents.story_creator import StoryCreator
from agents.art_designer import ArtDesigner
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化代理
character_designer = CharacterDesigner()
story_creator = StoryCreator()
art_designer = ArtDesigner("http://localhost:8188")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_story():
    try:
        # 获取用户输入
        user_input = request.json.get('description', '')
        
        # 生成角色
        character = character_designer.create_character(user_input)
        if not character:
            return jsonify({'error': '角色生成失败'}), 500
        
        # 生成故事
        story = story_creator.create_story(character)
        if not story:
            return jsonify({'error': '故事生成失败'}), 500
        
        # 生成图片
        scene_images = []
        for scene in story.scenes:
            image_path = art_designer.generate_scene_image(scene)
            if not image_path:
                return jsonify({'error': '图片生成失败'}), 500
            scene_images.append(image_path)
        
        # 返回结果
        return jsonify({
            'character': {
                'name': character.name,
                'age': character.age,
                'appearance': character.appearance,
                'personality': character.personality,
                'background': character.background
            },
            'story': {
                'title': story.title,
                'scenes': [{
                    'description': scene.description,
                    'image_path': image_path
                } for scene, image_path in zip(story.scenes, scene_images)],
                'moral': story.moral
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 