from dataclasses import dataclass
from typing import List

@dataclass
class Character:
    name: str
    age: int
    identity: str  # 角色身份，例如 "a young boy", "a little cat", "a friendly dog" 等
    appearance: dict
    personality: dict
    background: str
    likes: List[str]
    dislikes: List[str]