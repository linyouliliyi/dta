from models.character import Character
from models.story import Scene
import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class PromptEngineer:
    def __init__(self):
        self.api_url = "http://localhost:1234/v1/chat/completions"
        
    def generate_detailed_prompt(self, scene: Scene, character: Character) -> Optional[Dict[str, str]]:
        """
        Generate detailed image generation prompts based on scene and character information.
        Returns a dictionary containing both positive and negative prompts.
        """
        try:
            # Create a compact character description
            character_details = f"Character({character.name}): {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, distinctive features: {', '.join(character.appearance['distinctive_features'])}"

            # Combine scene and character details into a compact prompt
            base_prompt = f"{scene.image_prompt}, {character_details}"

            # Add artistic style and quality modifiers
            style_controllers = {
                "art_style": "(children's book illustration:1.3), (digital art:1.2), (cartoon:0.8)",
                "quality": "(high quality:1.2), (detailed:1.1), (sharp focus:1.2)",
                "lighting": "(soft lighting:1.1), (ambient light:0.8), (warm colors:1.0)",
                "composition": "(rule of thirds:1.1), (centered composition:0.9)",
                "mood": "(cheerful:1.2), (whimsical:1.1), (playful:1.0)"
            }
            
            # Combine all elements into a single, compact prompt
            final_positive_prompt = f"{base_prompt}, {style_controllers['art_style']}, {style_controllers['quality']}, {style_controllers['lighting']}, {style_controllers['composition']}, {style_controllers['mood']}"

            # Create a compact negative prompt
            negative_prompt = "deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, disconnected limbs, mutation, ugly, disgusting, blurry, fuzzy, out of focus, bad art, watermark, signature, text"

            return {
                "positive_prompt": final_positive_prompt.replace('\n', ' ').replace('  ', ' ').strip(),
                "negative_prompt": negative_prompt
            }

        except Exception as e:
            logger.error(f"Error generating detailed prompt: {str(e)}")
            return None

    def _format_positive_prompt(self, prompt_details: Dict) -> str:
        """Format the positive prompt with proper weighting and organization"""
        elements = [
            prompt_details['style_guide'],
            prompt_details['composition'],
            prompt_details['lighting'],
            prompt_details['positive_prompt'],
            prompt_details['additional_details']
        ]
        return ", ".join([e for e in elements if e])

    def _format_negative_prompt(self, prompt_details: Dict) -> str:
        """Format the negative prompt with standard exclusions"""
        standard_negatives = [
            "deformed", "distorted", "disfigured", "poorly drawn", "bad anatomy",
            "wrong anatomy", "extra limb", "missing limb", "floating limbs",
            "disconnected limbs", "mutation", "ugly", "disgusting", "blurry", "fuzzy"
        ]
        
        custom_negatives = prompt_details['negative_prompt'].split(",")
        all_negatives = standard_negatives + [neg.strip() for neg in custom_negatives]
        
        return ", ".join(all_negatives) 