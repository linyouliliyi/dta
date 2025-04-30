import os
import yaml
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CharacterService:
    def __init__(self, characters_dir: str = "characters"):
        self.characters_dir = characters_dir
        self._ensure_characters_dir()
        self.characters: Dict[str, dict] = {}
        self.load_characters()

    def _ensure_characters_dir(self):
        """Ensure the characters directory exists"""
        if not os.path.exists(self.characters_dir):
            os.makedirs(self.characters_dir)

    def load_characters(self):
        """Load all character YAML files from the characters directory"""
        self.characters.clear()
        if not os.path.exists(self.characters_dir):
            return

        loaded_count = 0
        for filename in os.listdir(self.characters_dir):
            if filename.endswith('.yaml'):
                file_path = os.path.join(self.characters_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        character_data = yaml.safe_load(f)
                        self.characters[filename[:-5]] = character_data
                        loaded_count += 1
                except Exception as e:
                    logger.error(f"Error loading character file {filename}: {e}")
        
        if loaded_count > 0:
            logger.info(f"Successfully loaded {loaded_count} characters")
        else:
            logger.warning("No character files found")

    def get_random_character(self) -> Optional[tuple]:
        """Get a random character from the library"""
        if not self.characters:
            logger.warning("No characters available")
            return None
        character_id = random.choice(list(self.characters.keys()))
        character = self.characters[character_id]
        source_file = f"{character_id}.yaml"
        logger.debug(f"Selected character from {source_file}")
        return character, source_file

    def get_character(self, character_id: str) -> Optional[dict]:
        """Get a specific character by ID"""
        return self.characters.get(character_id)

    def create_character(self, character_data: dict) -> str:
        """Create a new character and save it to a YAML file"""
        # Generate a unique ID for the new character
        character_id = f"{random.randint(0, 9999):04d}g"
        while character_id in self.characters:
            character_id = f"{random.randint(0, 9999):04d}g"

        # Save the character to a YAML file
        file_path = os.path.join(self.characters_dir, f"{character_id}.yaml")
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(character_data, f, allow_unicode=True)

        # Add to in-memory storage
        self.characters[character_id] = character_data
        return character_id

    def get_all_characters(self) -> List[dict]:
        """Get all characters from the library"""
        return list(self.characters.values()) 