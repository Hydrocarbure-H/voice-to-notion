import argparse
import datetime
import os
import requests
from pydub import AudioSegment
import speech_recognition as sr
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def transcribe_audio_segment(audio_segment, segment_index):
    """
    Transcribe a given audio segment using Google Speech Recognition API.

    @param audio_segment: The audio segment to transcribe.
    @param segment_index: The index of the segment.
    @return: Transcription text of the audio segment.
    """
    temp_file = f"segment_{segment_index}.wav"
    audio_segment.export(temp_file, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_file) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="fr-FR")

    os.remove(temp_file)  # Clean up the temporary file
    return text


def call_openai_api(transcription_text):
    """
    Call OpenAI GPT-4 API to summarize the transcription text.

    @param transcription_text: The complete transcription text.
    @return: The summarized text with important points and action items.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Voici la transcription d'une réunion entre plusieurs personnes, "
                    "issue d'un enregistrement dictaphone. "
                    "Fais un résumé de ce qu'il faut retenir avec les points "
                    "important en gras, et une liste des actions à faire suite à cette réunion. "
                    "Ces actions peuvent être des actions exprimées dans le texte ou des actions que tu suggères. "
                    "Ta réponse ne doit contenir que le résultat attendu, pas de phrase de présentation ou de conclusion. "
                    "Voici le texte : {transcription_text}"
                ),
            }
        ],
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"]


def add_to_notion(page_title, content):
    """
    Add a new page to a Notion database with the provided title and content.

    @param page_title: The title of the page to be created.
    @param content: The content of the page.
    @return: The response from the Notion API.
    """
    notion_api_url = "https://api.notion.com/v1/pages"
    database_id = os.getenv("NOTION_DATABASE_ID")
    api_key = os.getenv("NOTION_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "parent": {"database_id": database_id},
        "properties": {"title": {"title": [{"text": {"content": page_title}}]}},
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content}}]
                },
            }
        ],
    }

    response = requests.post(notion_api_url, headers=headers, json=data)
    return response.json()


def main(input_file):
    # Convert m4a to wav using pydub
    audio = AudioSegment.from_file(input_file)
    audio.export("reccord.wav", format="wav")

    # Split the audio into 2-minute segments
    segment_duration = 2 * 60 * 1000  # 2 minutes in milliseconds
    audio_segments = [
        audio[i : i + segment_duration] for i in range(0, len(audio), segment_duration)
    ]

    full_transcription = []

    print("Processing...")
    # Transcribe each segment
    for index, segment in enumerate(audio_segments):
        print(f"Transcribing segment {index + 1}...")
        transcription = transcribe_audio_segment(segment, index)
        full_transcription.append(transcription)

    # Combine all transcriptions
    complete_transcription = "\n".join(full_transcription)

    # Call OpenAI GPT-4 API with the complete transcription
    print("Calling OpenAI API...")
    final_output = call_openai_api(complete_transcription)

    # Title: date DD/MM/YYYY à HH:MM
    try:
        page_title = datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
    except Exception as e:
        page_title = "Réunion"

    print("Adding to Notion...")
    response = add_to_notion(page_title, final_output)
    
    # Remove the temporary wav file
    os.remove("reccord.wav")

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file and add the summary to Notion."
    )
    parser.add_argument(
        "input_file", type=str, help="The path to the input audio file (m4a format)."
    )
    args = parser.parse_args()

    main(args.input_file)
