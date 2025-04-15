# 儿童故事生成器

这是一个基于 AI 的儿童故事生成器，可以根据用户输入生成包含角色、场景和图片的完整故事。

## 功能特点

- 智能角色设计：根据用户描述生成独特的角色特征
- 故事生成：自动创建有趣的故事大纲和场景
- 图片生成：为每个场景生成对应的图片
- 教育意义：每个故事都包含积极的教育意义

## 技术栈

- Python 3.8+
- Flask (Web 框架)
- ComfyUI (AI 图片生成)
- 其他依赖见 requirements.txt

## 安装说明

1. 克隆项目到本地：
```bash
<<<<<<< HEAD
git clone [项目地址]
cd [项目目录]
=======
git clone https://github.com/linyouliliyi/dta.git
cd dta
>>>>>>> 62c234f55903773672c0f8f59f534bf45f6e8f86
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 确保 ComfyUI 服务已启动：
```bash
# 默认地址为 http://localhost:8188
# 确保 ComfyUI 已正确配置并运行
```

## 使用说明

1. 启动应用：
```bash
python app.py
```

2. 访问应用：
- 本地访问：打开浏览器访问 `http://127.0.0.1:5000`
- 默认只能在本地访问，如需外部访问需要修改配置

3. 使用方法：
- 在输入框中描述你想要的角色特征
- 点击生成按钮
- 等待系统生成完整的故事和图片
- 查看生成的结果

## 项目结构

```
.
├── app.py              # Flask 应用主文件
├── requirements.txt    # 项目依赖
├── static/            # 静态文件目录
│   └── images/        # 生成的图片存储目录
├── templates/         # HTML 模板
│   └── index.html    # 主页面模板
└── agents/           # AI 代理模块
    ├── art_designer.py    # 图片生成代理
    ├── character_designer.py  # 角色设计代理
    └── story_creator.py   # 故事生成代理
```

## 注意事项

1. 确保 ComfyUI 服务正常运行
2. 生成图片可能需要一些时间，请耐心等待
3. 建议使用现代浏览器访问应用
4. 默认配置仅支持本地访问

## 常见问题

1. 图片生成失败
   - 检查 ComfyUI 服务是否正常运行
   - 确认网络连接正常
   - 查看日志输出获取具体错误信息

2. 应用无法访问
   - 确认应用是否正常启动
   - 检查端口 5000 是否被占用
   - 确保防火墙设置允许访问

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。


