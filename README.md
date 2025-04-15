# 儿童故事创作器 (Children Story Creator)

这是一个使用 AI 技术自动生成儿童绘本故事的应用程序。它能够根据用户输入的角色描述，自动生成有趣的故事内容，并为每个场景生成配图，最终输出为精美的 PDF 绘本。

## 功能特点

- 角色设计：根据用户描述自动生成角色特征
- 故事创作：生成适合儿童阅读的趣味故事
- 场景配图：为每个故事场景生成配图
- PDF 生成：自动排版生成精美的 PDF 绘本

## 系统要求

- Python 3.8+
- Ollama (用于故事生成)
- ComfyUI (用于图片生成)

## 安装步骤

1. 克隆项目：
```bash
git clone https://github.com/linyouliliyi/dta.git
cd dta
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 安装 Ollama：
   - 访问 [Ollama 官网](https://ollama.ai/) 下载并安装
   - 启动 Ollama 服务：
   ```bash
   ollama serve
   ```
   - 下载 llama2 模型：
   ```bash
   ollama pull llama2
   ```

4. 安装 ComfyUI：
   - 访问 [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI) 下载并安装
   - 启动 ComfyUI 服务（默认端口 8188）

## 项目结构

```
children-story-creator/
├── agents/                # AI 代理模块
│   ├── character_designer.py  # 角色设计器
│   ├── story_creator.py      # 故事生成器
│   ├── art_designer.py      # 图片生成器
│   └── book_maker.py        # PDF 生成器
├── models/                # 数据模型
│   ├── character.py       # 角色模型
│   └── story.py          # 故事模型
├── utils/                # 工具函数
├── services/            # 外部服务接口
├── config.py           # 配置文件
├── main.py            # 主程序
└── requirements.txt    # 依赖列表
```

## 使用方法

1. 确保 Ollama 和 ComfyUI 服务都已启动

2. 运行主程序：
```bash
python main.py
```

3. 输入角色描述，例如：
```
我想创建一个喜欢探险的小猫角色，
它有着蓝色的毛发和大大的眼睛，
性格活泼开朗，喜欢帮助他人。
```

4. 程序会自动：
   - 生成角色特征
   - 创作故事内容
   - 为每个场景生成配图
   - 生成 PDF 绘本

5. 生成的绘本将保存在 `output/books` 目录下

## 配置说明

在 `config.py` 中可以修改以下配置：

```python
CONFIG = {
    "ollama": {
        "api_url": "http://localhost:11434",  # Ollama API 地址
        "model": "llama2"                     # 使用的模型
    },
    "comfyui": {
        "api_url": "http://localhost:8188"    # ComfyUI API 地址
    },
    "output_dir": "output"                    # 输出目录
}
```

## 注意事项

1. 确保 Ollama 和 ComfyUI 服务正常运行
2. 生成图片可能需要较长时间，请耐心等待
3. 建议使用 GPU 加速图片生成过程
4. 生成的 PDF 文件会自动保存在 output/books 目录下

## 常见问题

1. Ollama 服务无法启动
   - 检查端口 11434 是否被占用
   - 确保已正确安装 Ollama
   - 尝试重启 Ollama 服务

2. 图片生成失败
   - 检查 ComfyUI 服务是否正常运行
   - 确认 API 地址配置正确
   - 检查网络连接

3. PDF 生成失败
   - 确保已安装所有依赖
   - 检查输出目录权限
   - 确认图片文件存在且可访问

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

MIT License 
