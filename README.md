<div align="center">
  <h1>🎙️ Voice Recognition with Pyannote</h1>
  <p>
    <em>Advanced speaker diarization and voice recognition with a beautiful web interface</em>
  </p>
  
  <p>
    <a href="https://pypi.org/project/pyannote.audio/" target="_blank">
      <img src="https://img.shields.io/pypi/v/pyannote-audio?color=blue&label=pyannote.audio" alt="PyPI Version">
    </a>
    <a href="https://www.python.org/downloads/" target="_blank">
      <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python Version">
    </a>
    <a href="https://github.com/psf/black" target="_blank">
      <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
    </a>
    <a href="https://opensource.org/licenses/MIT" target="_blank">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
    </a>
  </p>
  
  <p>
    <a href="#features-✨">Features</a> •
    <a href="#demo-🎥">Demo</a> •
    <a href="#installation-⚙️">Installation</a> •
    <a href="#usage-🚀">Usage</a> •
    <a href="#api-documentation-📚">API</a> •
    <a href="#contributing-🤝">Contributing</a>
  </p>
</div>

<div align="center">
  <img src="https://user-images.githubusercontent.com/yourusername/your-repo/main/screenshots/demo.gif" alt="Voice Recognition Demo" width="90%">
</div>

## Features ✨

<div align="left">

🎯 **Speaker Diarization** - Automatically identify and separate different speakers in audio recordings

🎨 **Web Interface** - Intuitive and responsive web UI for easy interaction

🔊 **Audio Preview** - Listen to your uploaded audio files directly in the browser

⚙️ **Customizable Parameters** - Fine-tune speaker detection with advanced settings

📱 **Mobile Responsive** - Works seamlessly on desktop and mobile devices

⚡ **FastAPI Backend** - High-performance API built with FastAPI for quick responses

📊 **Interactive Results** - Visual timeline of speaker segments with timestamps

</div>

## Demo 🎥

[![Watch the demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://youtu.be/YOUR_VIDEO_ID)

*Click the image above to watch a demo video*

## Prerequisites 📋

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher
- pip (Python package manager)
- ffmpeg (for audio processing)
- A Hugging Face account with access to Pyannote models

### Installing FFmpeg

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Windows (using Chocolatey)
```bash
choco install ffmpeg
```

## Installation ⚙️

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice2text.git
   cd voice2text
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root and add your Hugging Face token:
   ```env
   # .env
   HUGGINGFACE_TOKEN=your_huggingface_token_here
   ```

### Getting Your Hugging Face Token

1. Sign up or log in to [Hugging Face](https://huggingface.co/)
2. Go to your [Access Tokens](https://huggingface.co/settings/tokens) page
3. Create a new token or use an existing one
4. Accept the terms and conditions for these models:
   - [pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization)
   - [pyannote/segmentation](https://huggingface.co/pyannote/segmentation)
5. Copy the token and paste it into your `.env` file

## Usage 🚀

### Starting the Application

1. **Navigate to the app directory**
   ```bash
   cd app
   ```

2. **Start the FastAPI server**
   ```bash
   uvicorn main:app --reload
   ```
   The `--reload` flag enables auto-reload during development.

3. **Access the web interface**
   Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

### Using the Web Interface

1. **Upload an audio file**
   - Click the "Choose File" button to select an audio file (WAV, MP3, etc.)
   - The file will be previewed in the built-in audio player

2. **Configure speaker settings (optional)**
   - Set the exact number of speakers (if known)
   - Or set minimum/maximum speaker counts
   - Leave all fields blank for automatic detection

3. **Process the audio**
   - Click "Process Audio" to start diarization
   - The processing time depends on the audio length and your hardware

4. **View results**
   - Speaker segments will be displayed with timestamps
   - Each speaker is assigned a unique color for easy identification
   - Hover over segments to see detailed timing information

### Command Line Interface (CLI)

You can also use the application via the command line:

```bash
# Process a single file
python -m app.cli process audio_file.wav --output results.json

# Process all files in a directory
python -m app.cli process-dir audio_directory/ --output results/
```

## API Documentation 📚

The application provides a RESTful API for programmatic access:

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check
```
GET /health
```
Check if the API is running and the model is loaded.

**Response**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "processing": false
}
```

#### 2. Process Audio
```
POST /transcribe
```
Process an audio file with speaker diarization.

**Parameters**
- `audio_file` (required): The audio file to process
- `num_speakers` (optional): Exact number of speakers
- `min_speakers` (optional): Minimum number of speakers
- `max_speakers` (optional): Maximum number of speakers

**Example Request**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/transcribe?min_speakers=2&max_speakers=4' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'audio_file=@meeting_recording.wav;type=audio/wav'
```

**Response**
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 2.34,
      "speaker": "SPEAKER_00",
      "text": null
    },
    {
      "start": 2.5,
      "end": 5.67,
      "speaker": "SPEAKER_01",
      "text": null
    }
  ],
  "full_text": "",
  "processing_time": 8.45
}
```

## Project Structure 🏗️

```
voice2text/
├── app/
│   ├── __init__.py         # Package initialization
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   │   ├── diarization.py  # Speaker diarization service
│   │   └── audio.py        # Audio processing utilities
│   ├── static/             # Frontend assets
│   │   ├── css/
│   │   ├── js/
│   │   └── index.html
│   └── tests/              # Test suite
│       ├── __init__.py
│       └── test_api.py
├── .env.example           # Example environment variables
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt       # Python dependencies
└── setup.py               # Package configuration
```

## Contributing 🤝

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   Click the "Fork" button at the top right of the repository page.

2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/voice2text.git
   cd voice2text
   ```

3. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**
   - Follow the existing code style
   - Write tests for new features
   - Update documentation as needed

5. **Run tests**
   ```bash
   python -m pytest
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Add your commit message here"
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   Go to the original repository and click "New Pull Request".

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- [Pyannote.audio](https://github.com/pyannote/pyannote-audio) for the amazing speaker diarization models
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance web framework
- [Tailwind CSS](https://tailwindcss.com/) for the utility-first CSS framework
- [Hugging Face](https://huggingface.co/) for hosting the pre-trained models

## Support ❤️

If you find this project useful, please consider giving it a ⭐️ on GitHub!

For support, please [open an issue](https://github.com/yourusername/voice2text/issues) on GitHub.

---

<div align="center">
  Made with ❤️ by Your Name
</div>

## License 📄

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for full details.

**Copyright © 2025 Prasad Nimantha Madusanka Ukwatta Hewage**

---

<div align="center">
  Made with ❤️ by Prasad Nimantha
</div>
