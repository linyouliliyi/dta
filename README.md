# Children's Story Generator

A web application that generates personalized children's stories with AI-generated illustrations. This project uses multiple AI models to create unique stories based on character descriptions provided by users.

## Features

- Character creation based on user descriptions
- AI-generated story creation
- Scene-by-scene illustration generation
- Interactive storybook creation
- Real-time progress tracking
- Beautiful and child-friendly UI

## Technical Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript, TailwindCSS
- AI Models:
  - Character and Story Generation: Local LLM (via API)
  - Image Generation: ComfyUI with Stable Diffusion
- PDF Generation: ReportLab

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd children-story-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up ComfyUI:
- Install ComfyUI locally
- Ensure it's running on port 8188
- Install required models and LoRAs:
  - Base model: sd_xl_base_1.0.safetensors
  - LoRA: COOLKIDS_MERGE_V2.5.safetensors

5. Set up Local LLM:
- Install and run a local LLM (e.g., llama.cpp)
- Ensure it's running on port 1234

## Project Structure

```
.
├── app.py                 # Main Flask application
├── agents/               # AI agent implementations
│   ├── art_designer.py   # Image generation
│   ├── book_maker.py     # PDF generation
│   ├── character_designer.py  # Character creation
│   ├── prompt_engineer.py     # Prompt optimization
│   └── story_creator.py       # Story generation
├── models/               # Data models
│   ├── character.py     # Character model
│   └── story.py         # Story model
├── static/              # Static files
│   └── images/         # Generated images
├── templates/           # HTML templates
│   └── index.html      # Main UI
├── utils/              # Utility functions
│   └── prompt_templates.py  # Prompt templates
└── output/             # Generated storybooks
    └── books/          # PDF files
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Enter a character description in the text area and click "Generate Story"

4. Wait for the story generation process to complete:
   - Character creation
   - Story generation
   - Image generation
   - Storybook creation

5. View and download your generated storybook

## Development

### Adding New Features

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes

3. Test your changes:
```bash
python -m pytest tests/
```

4. Commit and push:
```bash
git add .
git commit -m "Add your feature description"
git push origin feature/your-feature-name
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- ComfyUI for image generation
- Local LLM for story generation
- TailwindCSS for UI components
- Flask for web framework


