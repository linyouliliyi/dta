class PromptTemplates:
    @staticmethod
    def character_creation(user_input: str) -> str:
        return f"""
        基于用户输入："{user_input}"
        
        创建一个完整的角色描述，包含以下要素：
        1. 基本信息
        2. 外观特征
        3. 性格特点
        4. 背景故事
        5. 兴趣爱好
        
        要求：
        - 适合儿童故事
        - 形象生动具体
        - 性格特点要积极正面
        - 背景故事要有趣且富有教育意义
        
        请以JSON格式返回，包含以下字段：
        {{
            "name": "角色名称",
            "age": "年龄",
            "appearance": {{
                "physical_traits": [],
                "clothing": [],
                "distinctive_features": []
            }},
            "personality": {{
                "traits": [],
                "strengths": [],
                "weaknesses": []
            }},
            "background": "背景故事",
            "likes": [],
            "dislikes": []
        }}
        """

    @staticmethod
    def story_creation(character: dict) -> str:
        return f"""
        基于以下角色信息创作一个儿童故事：
        
        角色信息：
        {character}
        
        要求：
        1. 故事结构完整，包含开始、发展、高潮和结局
        2. 情节要符合角色特点
        3. 包含教育意义和正面价值观
        4. 语言简单易懂，适合儿童阅读
        5. 每个场景都要有明确的视觉描述
        
        请以JSON格式返回，包含以下字段：
        {{
            "title": "故事标题",
            "theme": "故事主题",
            "moral": "故事寓意",
            "target_age_range": [最小年龄, 最大年龄],
            "scenes": [
                {{
                    "title": "场景标题",
                    "description": "场景描述",
                    "image_prompt": "场景图像提示词"
                }}
            ]
        }}
        """

    @staticmethod
    def image_generation(scene: dict, style: str = "children's book") -> str:
        return f"""
        {style} style,
        {scene['description']},
        colorful, detailed, cute, child-friendly,
        high quality illustration,
        soft lighting, warm colors,
        digital art
        
        Negative prompt: ugly, scary, realistic, photographic, adult content, 
        dark themes, complex backgrounds, text, watermarks
        """

    @staticmethod
    def scene_enhancement(scene_description: str) -> str:
        return f"""
        基于以下场景描述，生成更丰富的视觉细节：
        {scene_description}
        
        请描述：
        1. 场景的具体环境
        2. 光线和颜色
        3. 角色的动作和表情
        4. 重要的道具和物品
        5. 场景的整体氛围
        
        要求：
        - 细节要具体形象
        - 适合儿童绘本风格
        - 避免复杂或消极的元素
        """

    @staticmethod
    def moral_lesson(story: dict) -> str:
        return f"""
        基于以下故事：
        {story}
        
        提炼出3-5个适合儿童的教育点：
        1. 主要寓意
        2. 可以学习的品格特征
        3. 生活中可以应用的经验
        
        要求：
        - 表述要简单明确
        - 适合父母和孩子讨论
        - 联系实际生活
        """