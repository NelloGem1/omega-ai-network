#!/usr/bin/env python3
"""Create progressive word reveal captions with neon glow."""
import os
import subprocess
import sys
import whisper

# Configuration
TRAILER_PATH = os.path.expanduser("~/youtube-tool/assets/trailers_dl/everything_everywhere_all_at_once.mp4")
OUTPUT_DIR = os.path.expanduser("~/Downloads")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "KINETIC_CAPTION_Test.mp4")
TEMP_DIR = "/tmp/kinetic_caption"
WHISPER_MODEL = "base"
START_TIME = 45
DURATION = 60

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ensure temp directory exists before use
def ensure_temp_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)

def run_cmd(cmd, description):
    """Run command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

def extract_segment_audio(trailer_path, output_path, start_time, duration):
    """Extract only the segment we need."""
    cmd = [
        "ffmpeg", "-y",
        "-i", trailer_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]
    run_cmd(cmd, f"Extracting audio segment")

def transcribe_with_word_timestamps(audio_path):
    """Transcribe with word-level timestamps."""
    print(f"\n{'='*60}")
    print("TRANSCRIBING WITH WORD-LEVEL TIMESTAMPS")
    print(f"{'='*60}")
    
    model = whisper.load_model(WHISPER_MODEL)
    
    # Use word_timestamps=True for word-level timing
    result = model.transcribe(audio_path, language="en", word_timestamps=True)
    
    # Extract word-level segments
    word_segments = []
    for segment in result["segments"]:
        if "words" in segment:
            for word_info in segment["words"]:
                word_segments.append({
                    "word": word_info["word"].strip().upper(),  # Convert to UPPERCASE
                    "start": word_info["start"] + START_TIME,
                    "end": word_info["end"] + START_TIME
                })
        else:
            # Fallback to segment-level if word timestamps not available
            text = segment["text"].strip().upper()  # Convert to UPPERCASE
            words = text.split()
            duration = segment["end"] - segment["start"]
            word_duration = duration / len(words) if words else 0
            
            for i, word in enumerate(words):
                word_start = segment["start"] + START_TIME + (i * word_duration)
                word_end = word_start + word_duration
                word_segments.append({
                    "word": word,
                    "start": word_start,
                    "end": word_end
                })
    
    print(f"\nTranscription complete: {len(word_segments)} words")
    print("\nSample words with timestamps:")
    for i, word in enumerate(word_segments[:10], 1):
        print(f"  {i}. [{word['start']:.1f}s - {word['end']:.1f}s] {word['word']}")
    
    return word_segments

def format_time(seconds):
    """Format seconds to ASS time format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def create_progressive_ass(word_segments, output_path, start_time, duration):
    """Create ASS file with UPGRADED progressive word reveal and color cycling."""
    
    # Group words into dynamic phrases (phrase-by-phrase with dynamic replacement)
    phrases = []
    current_phrase = []
    
    for i, word_info in enumerate(word_segments):
        word = word_info["word"]
        
        # Start new phrase on punctuation or speaker change indication
        if word.endswith(('.', '!', '?')) or (current_phrase and word_info["start"] - current_phrase[-1]["end"] > 0.3):
            if current_phrase:
                phrases.append(current_phrase)
            current_phrase = [word_info]
        else:
            current_phrase.append(word_info)
    
    if current_phrase:
        phrases.append(current_phrase)
    
    # Further split long phrases into 1-3 word chunks for kinetic effect
    short_phrases = []
    for phrase in phrases:
        if len(phrase) <= 3:
            short_phrases.append(phrase)
        else:
            # Split into chunks of 2-3 words
            chunk_size = 2 if len(phrase) % 2 == 0 else 3
            for i in range(0, len(phrase), chunk_size):
                chunk = phrase[i:i+chunk_size]
                if chunk:
                    short_phrases.append(chunk)
    
    # Color palette for cycling (emphasis-based coloring)
    # Red/Pink: Emphasis, intensity, important statements
    # Yellow: Attention, key information, important words
    # Blue: Contrast, explanatory dialogue, variation
    # Green: Visual variation and selective emphasis
    # Purple: Contrast and visual distinction
    colors = ["CaptionRed", "CaptionYellow", "CaptionBlue", "CaptionGreen", "CaptionPurple"]
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("""[Script Info]
Title: Kinetic Typography Captions - Professional Style
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CaptionRed,Anton,72,&H000000FF,&H000000FF,&H000000FF,&H80000000,1,0,0,0,100,100,2,0,1,4,6,5,20,20,180,1
Style: CaptionYellow,Anton,72,&H0000FFFF,&H0000FFFF,&H00FFAA00,&H80000000,1,0,0,0,100,100,2,0,1,4,6,5,20,20,180,1
Style: CaptionBlue,Anton,72,&H00FF00FF,&H00FF00FF,&H00FF00FF,&H80000000,1,0,0,0,100,100,2,0,1,4,6,5,20,20,180,1
Style: CaptionGreen,Anton,72,&H0000FF00,&H0000FF00,&H0000FF00,&H80000000,1,0,0,0,100,100,2,0,1,4,6,5,20,20,180,1
Style: CaptionPurple,Anton,72,&H00FF00FF,&H00FF00FF,&H00FF00FF,&H80000000,1,0,0,0,100,100,2,0,1,4,6,5,20,20,180,1
Style: HookHeader,Arial Black,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,0,8,20,20,80,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
        
        # Add hook header (first 5 seconds)
        hook_start = "0:00:00.00"
        hook_end = format_time(min(5, duration))
        hook_text = "POV: THE DESERT AWAITS YOUR DESTINY"
        f.write(f"Dialogue: 0,{hook_start},{hook_end},HookHeader,,0,0,0,,👁️ {hook_text}\n")
        
        # Add progressive captions with EMOTION-BASED color selection
        # Colors based on dialogue intensity and emphasis:
        # Red/Pink: Emphasis, intensity, important statements
        # Yellow: Attention, key information, important words
        # Blue: Contrast, explanatory dialogue, variation
        # Green: Visual variation and selective emphasis
        # Purple: Contrast and visual distinction
        for phrase_idx, phrase in enumerate(short_phrases):
            if not phrase:
                continue
            
            # Get phrase timing
            phrase_start = phrase[0]["start"] - start_time
            phrase_end = phrase[-1]["end"] - start_time
            
            # Skip if outside duration
            if phrase_start < 0 or phrase_start >= duration:
                continue
            
            # Clamp to duration
            phrase_start = max(0, phrase_start)
            phrase_end = min(duration, phrase_end + 0.05)  # Very brief overlap for smooth transition
            
            # Format times
            start_ass = format_time(phrase_start)
            end_ass = format_time(phrase_end)
            
            # Select color based on phrase characteristics
            phrase_text = " ".join([w["word"] for w in phrase]).upper()
            phrase_length = len(phrase_text)
            has_punctuation = any(p in phrase_text for p in ['!', '?'])
            has_exclamation = '!' in phrase_text
            
            # Color selection logic:
            # Red/Pink: Emphasis, intensity, important statements (!, ?, short punchy phrases)
            # Yellow: Attention, key information, important words (longer phrases)
            # Blue: Contrast, explanatory dialogue, variation (medium phrases)
            # Green: Visual variation and selective emphasis (questions)
            # Purple: Contrast and visual distinction (statements)
            
            if has_exclamation or (has_punctuation and phrase_length < 20):
                color_style = "CaptionRed"  # High intensity
            elif has_punctuation and phrase_length < 30:
                color_style = "CaptionGreen"  # Questions/emphasis
            elif phrase_length > 40:
                color_style = "CaptionYellow"  # Key information
            elif phrase_length > 25:
                color_style = "CaptionBlue"  # Explanatory
            else:
                color_style = "CaptionPurple"  # Visual distinction
            
            # Build kinetic typography text with emphasis scaling
            animated_text = ""
            for i, word_info in enumerate(phrase):
                word = word_info["word"]
                word_start = word_info["start"] - start_time
                word_end = word_info["end"] - start_time
                
                # Escape special characters
                word_escaped = word.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
                
                # Calculate word duration for animation
                word_duration = max(0.05, word_end - word_start)
                fade_duration = min(3, word_duration * 30)  # Very quick fade
                
                # Emphasis scaling for important words (short words, punctuation)
                is_important = len(word) <= 3 or any(p in word for p in ['!', '?'])
                scale_factor = 1.1 if is_important else 1.0
                
                # Create word with pop-in scale and fade effect
                # Scale from 90% to 100% with quick ease-out
                if is_important:
                    word_tag = f"{{\\fad(30,{fade_duration})\\t(0,100,\\fscx{int(scale_factor*100)}\\fscy{int(scale_factor*100)})\\t(30,100,\\fscx100\\fscy100)}}{word_escaped} "
                else:
                    word_tag = f"{{\\fad(30,{fade_duration})\\t(0,100,\\fscx105\\fscy105)\\t(30,100,\\fscx100\\fscy100)}}{word_escaped} "
                animated_text += word_tag
            
            # Add dialogue event with emotion-based color style
            f.write(f"Dialogue: 0,{start_ass},{end_ass},{color_style},,0,0,0,,{animated_text}\n")
    
    print(f"Kinetic Typography ASS file created: {output_path}")
    print(f"Total phrases: {len(short_phrases)}")
    print(f"Color system: Emotion-based (Red=Emphasis, Yellow=Attention, Blue=Contrast, Green=Variation, Purple=Distinction)")

def create_progressive_video(video_path, ass_path, output_path, start_time, duration):
    """Create video with progressive word reveal captions."""
    print(f"\nCreating video from {start_time}s for {duration}s")
    
    # Create square crop
    base_video = os.path.join(TEMP_DIR, "base.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", "crop=ih:ih:(iw-ih)/2:0,scale=1080:1080",
        "-t", str(duration),
        "-ss", str(start_time),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        base_video
    ]
    run_cmd(cmd, "Creating base video")
    
    # Apply cinematic grading
    graded_video = os.path.join(TEMP_DIR, "graded.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", base_video,
        "-vf", "eq=contrast=1.15:saturation=1.25:brightness=-0.02,vignette=PI/4.5:mode=forward",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        graded_video
    ]
    run_cmd(cmd, "Applying cinematic grading")
    
    # Burn progressive subtitles
    subtitle_video = os.path.join(TEMP_DIR, "subtitle.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", graded_video,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        subtitle_video
    ]
    run_cmd(cmd, "Burning progressive captions")
    
    # Extract audio
    audio_path = os.path.join(TEMP_DIR, "audio.aac")
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-t", str(duration),
        "-ss", str(start_time),
        "-vn",
        "-c:a", "aac", "-b:a", "192k",
        audio_path
    ]
    run_cmd(cmd, "Extracting audio")
    
    # Combine video and audio
    cmd = [
        "ffmpeg", "-y",
        "-i", subtitle_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path
    ]
    run_cmd(cmd, "Combining video and audio")

def main():
    print("=" * 60)
    print("PROGRESSIVE WORD REVEAL CAPTION CREATOR")
    print("=" * 60)
    print(f"Trailer: {TRAILER_PATH}")
    print(f"Segment: {START_TIME}s - {START_TIME+DURATION}s")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    # Check if trailer exists
    if not os.path.exists(TRAILER_PATH):
        print(f"Error: Trailer not found: {TRAILER_PATH}")
        sys.exit(1)
    
    # Extract audio segment
    audio_path = os.path.join(TEMP_DIR, "segment_audio.wav")
    extract_segment_audio(TRAILER_PATH, audio_path, START_TIME, DURATION)
    
    # Transcribe with word timestamps
    word_segments = transcribe_with_word_timestamps(audio_path)
    
    # Ensure temp directory exists
    ensure_temp_dir()
    
    # Create progressive ASS file
    ass_path = os.path.join(TEMP_DIR, "progressive.ass")
    create_progressive_ass(word_segments, ass_path, START_TIME, DURATION)
    
    # Create video with progressive captions
    create_progressive_video(TRAILER_PATH, ass_path, OUTPUT_FILE, START_TIME, DURATION)
    
    # Cleanup
    print("\n" + "=" * 60)
    print("CLEANING UP")
    print("=" * 60)
    for f in os.listdir(TEMP_DIR):
        os.remove(os.path.join(TEMP_DIR, f))
    os.rmdir(TEMP_DIR)
    
    print(f"\nProgressive Caption Video created: {OUTPUT_FILE}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
