from models.character import Character
import ollama
import requests
from typing import Optional

class CharacterDesigner:
    def __init__(self):
        self.model = "llama2"  # 或其他你喜欢的模型
        self.api_url = "http://localhost:11434"  # Ollama默认地址
    
    def create_character(self, user_input: str) -> Optional[Character]:
        try:
            # 使用Ollama生成角色特征
            prompt = f"""
            基于以下用户输入，创建一个儿童故事角色：
            {user_input}
            
            请提供以下信息：
            - 名字
            - 年龄
            - 外貌特征
            - 性格特点
            - 背景故事
            - 喜欢的东西
            - 不喜欢的东西
            """
            
            # 检查Ollama服务是否可用
            try:
                response = requests.get(f"{self.api_url}/api/tags")
                if response.status_code != 200:
                    print("错误：无法连接到Ollama服务，请确保服务已启动")
                    return None
            except requests.exceptions.ConnectionError:
                print("错误：无法连接到Ollama服务，请确保服务已启动")
                return None
            
            # 生成角色
            response = ollama.generate(model=self.model, prompt=prompt)
            
            # 解析响应并创建Character对象
            # TODO: 实现响应解析逻辑
            return Character(
                name="临时名字",
                age=5,
                appearance="临时外貌",
                personality="临时性格",
                background="临时背景",
                likes=["临时喜好"],
                dislikes=["临时不喜欢"]
            )
            
        except Exception as e:
            print(f"创建角色时发生错误: {str(e)}")
            return None