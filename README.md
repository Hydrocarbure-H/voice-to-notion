# voice-to-notion
Reccord your meeting, get a transcript and ToDo lists powered by AI and add it to your Notion.

# Transcribe and Summarize Meeting Notes

This project transcribes an audio file, summarizes the transcription using OpenAI's GPT-4 API, and adds the summary to a Notion database.

## Features
- Converts audio files from m4a to wav format.
- Splits audio into 2-minute segments for transcription.
- Uses Google Speech Recognition API to transcribe audio segments.
- Uses OpenAI's GPT-4 API to summarize the transcription.
- Adds the summarized notes to a specified Notion database.

## Installation

### Prerequisites
- Python 3.6 or higher
- An OpenAI API key
- A Notion API key
- Notion Database ID

### Dependencies
Install the required Python packages using pip:

```bash
pip install pydub SpeechRecognition requests python-dotenv
```

### Environment Variables

Create a `.env` file in the root directory of your project and add the following environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

## Usage

1. **Prepare your audio file**: Ensure you have an audio file that you want to transcribe and summarize.

2. **Run the script**:

   ```
   python voice-to-notion.py path_to_your_audio_file.m4a
   ```
