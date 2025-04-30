# Children's Story Generator

An AI-powered application that automatically creates children's stories with beautiful illustrations.

## Features

- Uses large language models to generate characters and storylines
- Creates high-quality illustrations using Stable Diffusion
- Automatically generates PDF storybooks
- Supports two character creation methods:
  - Random selection from [PolyU Storyworld Character Library](https://github.com/venetanji/polyu-storyworld)
  - Custom character creation with detailed traits
- Includes educational value in generated stories
- Real-time generation progress tracking
- View previously generated storybooks in output directory

## Requirements

- Python 3.8+
- ComfyUI (for image generation)
- LM Studio (for text generation)

## Installation

1. Clone the repository:
```bash
git clone [repository_url]
cd children-story-generator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure models:
   - Configure model paths in `config/models.py`
   - Ensure model files are placed in the correct directories:
     - Base models in `models/checkpoints/`
     - LoRA models in `models/loras/`

4. Download required models:
   - Base model: [Children's Book MIX_V1](https://drive.google.com/file/d/1GZGxQakaymBhD4bQVABVlRpMPg5bEskF/view?usp=sharing)
   - LoRA model: [Muertu 1.5丨Hand-drawn Fairy Tale World Children's Book Enhancement LoRA](https://drive.google.com/file/d/1hfaFc5KfJc_sWMk1WwqV1gsqQbm7ULBM/view?usp=drive_link)

## Configuration

1. ComfyUI Configuration:
   - Ensure ComfyUI service is running at `http://localhost:8188`
   - Workflow configuration file located at `workflows/default_workflow.json`
   - Default image dimensions: Initial 504x304, upscaled to 1000x600

2. LM Studio Configuration:
   - Ensure LM Studio service is running at `http://localhost:1234`
   - Use appropriate models for text generation

3. Directory Structure:
```
.
├── agents/                 # Agent classes
├── config/                 # Configuration files
├── models/                 # Model files
│   ├── checkpoints/       # Base models
│   ├── loras/            # LoRA models
│   ├── vae/              # VAE models
│   └── embeddings/       # Text embedding models
├── static/                # Static files
│   └── images/           # Generated images
├── templates/             # HTML templates
├── workflows/             # ComfyUI workflows
└── output/                # Output files
    └── books/            # Generated PDF storybooks
```

## Usage

1. Start the service:
```bash
python app.py
```

2. Access the application:
   - Open browser and visit `http://localhost:5000`
   - Choose character creation method:
     - Click "Use Polyu-Storyworld Characters" to select from PolyU Storyworld library
     - Click "Create Custom Character" to create your own
   - Optionally enter a story theme
   - Click "Generate Story" button

3. View results:
   - Generated images are saved in `static/images/`
   - Generated PDFs are saved in `output/books/`
   - Previously generated storybooks can be found in the output directory

## Character Creation

### Method 1: Using PolyU Storyworld Characters
- Click "Use Polyu-Storyworld Characters" to select a pre-made character
- Character source file will be displayed
- Characters are from [PolyU Storyworld](https://github.com/venetanji/polyu-storyworld)

### Method 2: Custom Character Creation
- Click "Create Custom Character"
- Fill in character details:
  - Name
  - Age
  - Appearance
  - Personality
  - Backstory

## Story Generation Process

1. Character Selection/Creation:
   - Progress indicator shows current step
   - Real-time status updates

2. Story Generation:
   - Creates engaging plot based on character
   - Generates multiple scenes

3. Image Generation:
   - Creates illustrations for each scene
   - Shows progress for each image

4. PDF Creation:
   - Combines story and images
   - Saves to output directory

## Important Notes

1. Ensure all services are running properly:
   - ComfyUI service
   - LM Studio service
   - Flask application

2. Model files:
   - Ensure model files are in correct directories
   - Verify model path configurations

3. Image generation:
   - Default resolution: 1000x600
   - Parameters can be adjusted in workflow configuration

## Troubleshooting

1. Images not displaying:
   - Check image paths
   - Verify image files exist
   - Check file permissions

2. Generation failures:
   - Verify services are running
   - Check log output
   - Verify model configurations

## Contributing

Feel free to submit Issues and Pull Requests.

## License

MIT License


