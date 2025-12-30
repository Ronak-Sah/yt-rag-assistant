from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import xml.etree.ElementTree as ET
# Test with a video known to have captions
test_url = "https://www.youtube.com/watch?v=j5168Ug7DvA"  # "Me at the zoo" - first YouTube video

try:
    transcript = YouTubeTranscriptApi.get_transcript("jNQXAC9IVRw")
    print(f"Success! Transcript length: {len(transcript)}")
    # join text segments and print first 200 characters for readability
    text = " ".join(item.get("text", "") for item in transcript)
    print(f"First 200 chars: {text[:200]}")
except TranscriptsDisabled:
    print("Transcripts are disabled for this video.")
except NoTranscriptFound:
    print("No transcript could be found for this video.")
except ET.ParseError as e:
    print(f"Failed to parse transcript XML: {e}")
except Exception as e:
    print(f"Error fetching transcript: {e}")
    print(f"Error: {e}")