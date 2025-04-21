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
            workflow = {
                "prompt": {
                    "1": {
                        "inputs": {
                            "unet_name": "flux1-schnell.sft",
                            "weight_dtype": "fp8_e5m2"
                        },
                        "class_type": "UNETLoader",
                        "_meta": {"title": "Load Diffusion Model"}
                    },
                    "2": {
                        "inputs": {
                            "clip_name1": "t5xxl_fp16.safetensors",
                            "clip_name2": "clip_l.safetensors",
                            "type": "flux"
                        },
                        "class_type": "DualCLIPLoader",
                        "_meta": {"title": "DualCLIPLoader"}
                    },
                    "3": {
                        "inputs": {
                            "vae_name": "ae.sft"
                        },
                        "class_type": "VAELoader",
                        "_meta": {"title": "Load VAE"}
                    },
                    "4": {
                        "inputs": {
                            "seed": 501348891644945,
                            "steps": 15,
                            "cfg": 1,
                            "sampler_name": "euler",
                            "scheduler": "simple",
                            "denoise": 1,
                            "model": ["54", 0],
                            "positive": ["58", 0],
                            "negative": ["46", 0],
                            "latent_image": ["42", 0]
                        },
                        "class_type": "KSampler",
                        "_meta": {"title": "KSampler"}
                    },
                    "16": {
                        "inputs": {
                            "samples": ["4", 0],
                            "vae": ["3", 0]
                        },
                        "class_type": "VAEDecode",
                        "_meta": {"title": "VAE Decode"}
                    },
                    "37": {
                        "inputs": {
                            "images": ["16", 0]
                        },
                        "class_type": "PreviewImage",
                        "_meta": {"title": "Preview Image"}
                    },
                    "42": {
                        "inputs": {
                            "width": 904,
                            "height": 600,
                            "batch_size": 1
                        },
                        "class_type": "EmptyLatentImage",
                        "_meta": {"title": "Empty Latent Image"}
                    },
                    "46": {
                        "inputs": {
                            "text": "bad hands, text, watermark, low quality, blurry, malformed, abnormal",
                            "clip": ["2", 0]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "CLIP Text Encode (Prompt)"}
                    },
                    "53": {
                        "inputs": {
                            "text": description,
                            "clip": ["54", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "CLIP Text Encode (Prompt)"}
                    },
                    "54": {
                        "inputs": {
                            "lora_name": "儿童动物插画故事绘本_V2.0.safetensors",
                            "strength_model": 0.8,
                            "strength_clip": 1,
                            "model": ["1", 0],
                            "clip": ["2", 0]
                        },
                        "class_type": "LoraLoader",
                        "_meta": {"title": "Load LoRA"}
                    },
                    "58": {
                        "inputs": {
                            "guidance": 3.5,
                            "conditioning": ["53", 0]
                        },
                        "class_type": "FluxGuidance",
                        "_meta": {"title": "FluxGuidance"}
                    }
                }
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
            character_description = f"{', '.join(character.appearance['physical_traits'])}, wearing {', '.join(character.appearance['clothing'])}, with {', '.join(character.appearance['distinctive_features'])}"
            
            # Build complete scene prompt including character features
            full_prompt = f"{scene.image_prompt}, {character_description}, consistent character design, high quality, detailed, clear"
            
            # Print detailed prompt information
            print("\n=== Scene Generation Details ===")
            print(f"Scene Title: {scene.title}")
            print(f"Scene Description: {scene.image_prompt}")
            print(f"Character Features: {character_description}")
            print(f"Full Prompt: {full_prompt}")
            print("=============================\n")
            
            # Build ComfyUI workflow
            workflow = {
                "prompt": {
                    "1": {
                        "inputs": {
                            "unet_name": "flux1-schnell.sft",
                            "weight_dtype": "fp8_e5m2"
                        },
                        "class_type": "UNETLoader",
                        "_meta": {"title": "Load Diffusion Model"}
                    },
                    "2": {
                        "inputs": {
                            "clip_name1": "t5xxl_fp16.safetensors",
                            "clip_name2": "clip_l.safetensors",
                            "type": "flux"
                        },
                        "class_type": "DualCLIPLoader",
                        "_meta": {"title": "DualCLIPLoader"}
                    },
                    "3": {
                        "inputs": {
                            "vae_name": "ae.sft"
                        },
                        "class_type": "VAELoader",
                        "_meta": {"title": "Load VAE"}
                    },
                    "4": {
                        "inputs": {
                            "seed": 501348891644945,
                            "steps": 15,
                            "cfg": 1,
                            "sampler_name": "euler",
                            "scheduler": "simple",
                            "denoise": 1,
                            "model": ["54", 0],
                            "positive": ["58", 0],
                            "negative": ["46", 0],
                            "latent_image": ["42", 0]
                        },
                        "class_type": "KSampler",
                        "_meta": {"title": "KSampler"}
                    },
                    "16": {
                        "inputs": {
                            "samples": ["4", 0],
                            "vae": ["3", 0]
                        },
                        "class_type": "VAEDecode",
                        "_meta": {"title": "VAE Decode"}
                    },
                    "37": {
                        "inputs": {
                            "images": ["16", 0]
                        },
                        "class_type": "PreviewImage",
                        "_meta": {"title": "Preview Image"}
                    },
                    "42": {
                        "inputs": {
                            "width": 904,
                            "height": 600,
                            "batch_size": 1
                        },
                        "class_type": "EmptyLatentImage",
                        "_meta": {"title": "Empty Latent Image"}
                    },
                    "46": {
                        "inputs": {
                            "text": "low quality",
                            "clip": ["2", 0]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "CLIP Text Encode (Prompt)"}
                    },
                    "53": {
                        "inputs": {
                            "text": full_prompt,
                            "clip": ["54", 1]
                        },
                        "class_type": "CLIPTextEncode",
                        "_meta": {"title": "CLIP Text Encode (Prompt)"}
                    },
                    "54": {
                        "inputs": {
                            "lora_name": "儿童动物插画故事绘本_V2.0.safetensors",
                            "strength_model": 0.8,
                            "strength_clip": 1,
                            "model": ["1", 0],
                            "clip": ["2", 0]
                        },
                        "class_type": "LoraLoader",
                        "_meta": {"title": "Load LoRA"}
                    },
                    "58": {
                        "inputs": {
                            "guidance": 3.5,
                            "conditioning": ["53", 0]
                        },
                        "class_type": "FluxGuidance",
                        "_meta": {"title": "FluxGuidance"}
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
            max_retries = 500  # Increase timeout to 500 seconds
            retry_count = 0
            while retry_count < max_retries:
                try:
                    print(f"Waiting for image generation to complete... ({retry_count + 1}/{max_retries})")
                    history = requests.get(f"{self.api_url}/history/{prompt_id}")
                    if history.status_code == 200:
                        history_data = history.json()
                        if prompt_id in history_data:
                            outputs = history_data[prompt_id]['outputs']
                            if outputs:
                                # Get generated image
                                image_data = outputs['37']['images'][0]  # Changed from '12' to '37' to match our workflow
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
                    elif history.status_code == 404:
                        print("Generation task not found, retrying...")
                    else:
                        print(f"Error checking generation status: {history.status_code}")
                        print(f"Response content: {history.text}")
                except requests.exceptions.RequestException as e:
                    print(f"Network error while checking generation status: {str(e)}")
                except Exception as e:
                    print(f"Unexpected error while checking generation status: {str(e)}")
                    import traceback
                    print(f"Error stack trace: {traceback.format_exc()}")
                
                time.sleep(1)  # Wait 1 second
                retry_count += 1
                
            print("Error: Image generation timed out")
            return None
            
        except Exception as e:
            print(f"Error occurred while generating scene image: {str(e)}")
            import traceback
            print(f"Error stack trace: {traceback.format_exc()}")
            return None