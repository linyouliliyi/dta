"""
模型配置文件，包含所有使用的模型信息和下载链接
"""

# 基础模型
BASE_MODELS = {
    "children_book_mix": {
        "name": "Children's Book MIX_V1",
        "filename": "Children's Book MIX_V1.safetensors",
        "description": "儿童绘本风格的基础模型",
        "download_url": "https://drive.google.com/file/d/1GZGxQakaymBhD4bQVABVlRpMPg5bEskF/view?usp=sharing",  # 下载链接
        "type": "checkpoint"
    }
}

# LoRA模型
LORA_MODELS = {
    "muertu_children_book": {
        "name": "Muertu 1.5丨Hand-drawn Fairy Tale World Children's Book Enhancement LoRA",
        "filename": "Muertu 1.5丨Hand-drawn Fairy Tale World Children's Book Enhancement LoRA.safetensors",
        "description": "增强儿童绘本风格的LoRA模型",
        "download_url": "https://drive.google.com/file/d/1hfaFc5KfJc_sWMk1WwqV1gsqQbm7ULBM/view?usp=drive_link",  # 下载链接
        "type": "lora",
        "strength_model": 0.8,
        "strength_clip": 1.0
    }
}

# 模型目录配置
MODEL_DIRS = {
    "checkpoints": "models/checkpoints",  # 基础模型目录
    "loras": "models/loras",  # LoRA模型目录
    "vae": "models/vae",  # VAE模型目录
    "embeddings": "models/embeddings"  # 文本嵌入模型目录
}

# 模型版本信息
VERSION_INFO = {
    "last_updated": "2024-03-20",
    "compatible_comfyui_version": "1.0.0",
    "notes": "请确保将模型文件放置在正确的目录中"
}

def get_model_path(model_type: str, model_name: str) -> str:
    """
    获取模型文件的完整路径
    
    Args:
        model_type: 模型类型 ('checkpoint' 或 'lora')
        model_name: 模型名称
        
    Returns:
        str: 模型文件的完整路径
    """
    if model_type == "checkpoint":
        return f"{MODEL_DIRS['checkpoints']}/{BASE_MODELS[model_name]['filename']}"
    elif model_type == "lora":
        return f"{MODEL_DIRS['loras']}/{LORA_MODELS[model_name]['filename']}"
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

def get_model_info(model_type: str, model_name: str) -> dict:
    """
    获取模型信息
    
    Args:
        model_type: 模型类型 ('checkpoint' 或 'lora')
        model_name: 模型名称
        
    Returns:
        dict: 模型信息字典
    """
    if model_type == "checkpoint":
        return BASE_MODELS[model_name]
    elif model_type == "lora":
        return LORA_MODELS[model_name]
    else:
        raise ValueError(f"Unsupported model type: {model_type}") 