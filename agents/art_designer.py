from models.character import Character
from models.story import Scene
import json
import requests
from PIL import Image
import os
from typing import Optional
from datetime import datetime
import time

class ArtDesigner:
    def __init__(self, comfyui_api_url: str):
        self.api_url = comfyui_api_url
        # Modify output directory to static/images so Flask can serve these files directly
        self.output_dir = "static/images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_character_image(self, character: Character) -> Optional[str]:
        try:
            # Build character description
            description = f"""
            A {character.age} year old character,
            Physical features: {character.appearance}
            Personality traits: {character.personality}
            """
            
            # Check if ComfyUI service is available
            try:
                response = requests.get(f"{self.api_url}/history")
                if response.status_code != 200:
                    print("Error: Unable to connect to ComfyUI service, please ensure the service is running")
                    return None
            except requests.exceptions.ConnectionError:
                print("Error: Unable to connect to ComfyUI service, please ensure the service is running")
                return None
            
            # Call ComfyUI API
            # This needs to be adjusted according to your ComfyUI configuration
            workflow = {
                # ComfyUI workflow configuration
            }
            
            response = requests.post(f"{self.api_url}/queue", json=workflow)
            if response.status_code != 200:
                print("Error: Failed to generate image")
                return None
            
            # Generate image filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.output_dir, f"character_{timestamp}.png")
            
            # Save image
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            # Return path relative to static directory so Flask can serve this file directly
            return os.path.relpath(image_path, "static")
            
        except Exception as e:
            print(f"Error occurred while generating character image: {str(e)}")
            return None
            
    def generate_scene_image(self, scene: Scene, character: Character) -> Optional[str]:
        try:
            # Check character information completeness
            if not character.appearance or not all(key in character.appearance for key in ['physical_traits', 'clothing', 'distinctive_features']):
                print("Warning: Character information is incomplete, may affect image generation quality")
            
            # Check if ComfyUI service is available
            try:
                response = requests.get(f"{self.api_url}/history")
                if response.status_code != 200:
                    print(f"Error: Unable to connect to ComfyUI service, status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return None
            except requests.exceptions.ConnectionError as e:
                print(f"Error: Unable to connect to ComfyUI service: {str(e)}")
                return None
            
            # Build character feature description
            character_description = f"Character features: {', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}"
            
            # Build complete scene prompt including character features
            full_prompt = f"{scene.image_prompt}, {character_description}"
            print(f"DEBUG: ComfyUI prompt for scene '{scene.title}': {full_prompt}")
            
            # Build ComfyUI workflow
            workflow = {
                "prompt": {
                    "1": {
                        "inputs": {
                            "ckpt_name": "sd_xl_base_1.0.safetensors"
                        },
                        "class_type": "CheckpointLoaderSimple",
                        "_meta": {
                            "title": "Load Checkpoint"
                        }
                    },
                    "2": {
                        "inputs": {
                            "width": 768,
                            "height": 768,
                            "batch_size": 1
                        },
                        "class_type": "EmptyLatentImage",
                        "_meta": {
                            "title": "Empty Latent Image"
                        }
                    },
                    "3": {
                        "inputs": {
                            "lora_name": "COOLKIDS_MERGE_V2.5.safetensors",
                            "strength_model": 0.75,
                            "strength_clip": 1,
                            "model": ["1", 0],
                            "clip": ["1", 1]
                        },
                        "class_type": "LoraLoader",
                        "_meta": {
                            "title": "Load LoRA"
                        }
                    },
                    "4": {
                        "inputs": {
                            "text": full_prompt,
                            "clip": ["3", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {
                            "title": "CLIP Text Encode (Prompt)"
                        }
                    },
                    "5": {
                        "inputs": {
                            "text": "(worst quality, low quality:1.4), (bad anatomy), text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, deformed face",
                            "clip": ["3", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {
                            "title": "CLIP Text Encode (Prompt)"
                        }
                    },
                    "6": {
                        "inputs": {
                            "seed": 530938972832347,
                            "steps": 30,
                            "cfg": 7,
                            "sampler_name": "dpmpp_2m",
                            "scheduler": "karras",
                            "denoise": 1,
                            "model": ["3", 0],
                            "positive": ["4", 0],
                            "negative": ["5", 0],
                            "latent_image": ["2", 0]
                        },
                        "class_type": "KSampler",
                        "_meta": {
                            "title": "KSampler"
                        }
                    },
                    "7": {
                        "inputs": {
                            "samples": ["6", 0],
                            "vae": ["1", 2]
                        },
                        "class_type": "VAEDecode",
                        "_meta": {
                            "title": "VAE Decode"
                        }
                    },
                    "8": {
                        "inputs": {
                            "filename_prefix": "scene_",
                            "images": ["7", 0]
                        },
                        "class_type": "SaveImage",
                        "_meta": {
                            "title": "Save Image"
                        }
                    }
                }
            }
            
            # Send request to ComfyUI
            print("Sending request to ComfyUI...")
            response = requests.post(f"{self.api_url}/prompt", json=workflow)
            if response.status_code != 200:
                print(f"Error: Failed to generate image, status code: {response.status_code}")
                print(f"Response content: {response.text}")
                return None
                
            # Get generation result
            prompt_id = response.json()['prompt_id']
            print(f"Image generation task created, ID: {prompt_id}")
            
            # Wait for generation to complete
            max_retries = 30  # Wait up to 30 seconds
            retry_count = 0
            while retry_count < max_retries:
                print(f"Waiting for image generation to complete... ({retry_count + 1}/{max_retries})")
                history = requests.get(f"{self.api_url}/history/{prompt_id}")
                if history.status_code == 200:
                    history_data = history.json()
                    if prompt_id in history_data:
                        outputs = history_data[prompt_id]['outputs']
                        if outputs:
                            # Get generated image
                            image_data = outputs['8']['images'][0]
                            # Remove all spaces and special characters from title
                            safe_title = ''.join(e for e in scene.title if e.isalnum() or e in ('_', '-'))
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            image_filename = f"scene_{safe_title}_{timestamp}.png"
                            image_path = os.path.join(self.output_dir, image_filename)
                            
                            # Ensure output directory exists
                            os.makedirs(os.path.dirname(image_path), exist_ok=True)
                            
                            # Download and save image
                            print(f"Downloading generated image: {image_data['filename']}")
                            image_response = requests.get(f"{self.api_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}")
                            if image_response.status_code == 200:
                                with open(image_path, "wb") as f:
                                    f.write(image_response.content)
                                print(f"Image saved to: {image_path}")
                                # Return path with /static prefix, using forward slash as separator
                                relative_path = os.path.relpath(image_path, "static").replace("\\", "/")
                                return f"/static/{relative_path}"
                            else:
                                print(f"Error: Failed to download image, status code: {image_response.status_code}")
                                print(f"Response content: {image_response.text}")
                time.sleep(1)  # Wait 1 second
                retry_count += 1
                
            print("Error: Image generation timed out")
            return None
            
        except Exception as e:
            print(f"Error occurred while generating scene image: {str(e)}")
            import traceback
            print(f"Error stack trace: {traceback.format_exc()}")
            return None