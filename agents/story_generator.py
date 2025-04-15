    def generate_story(self, character: Character) -> Story:
        """生成故事"""
        # 生成故事大纲
        outline = self.generate_outline(character)
        
        # 生成场景
        scenes = []
        for scene_title, scene_description in outline.scenes.items():
            # 生成场景图片提示词
            image_prompt = self.generate_image_prompt(scene_title, scene_description, character)
            
            # 生成场景图片
            image_path = self.art_designer.generate_scene_image(
                Scene(title=scene_title, description=scene_description, image_prompt=image_prompt),
                character  # 传递角色信息
            )
            
            scenes.append(Scene(
                title=scene_title,
                description=scene_description,
                image_prompt=image_prompt,
                image_path=image_path
            ))
        
        # 生成教育意义
        moral = self.generate_moral(character, outline)
        
        return Story(
            title=outline.title,
            scenes=scenes,
            moral=moral
        ) 