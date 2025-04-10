from dataclasses import dataclass
from typing import List

@dataclass
class Character:
    name: str
    age: int
    appearance: dict
    personality: dict
    background: str
    likes: List[str]
    dislikes: List[str]