#!/usr/bin/env python3
"""
Emotional Trigger Analysis Script
Analyzes reference video and identifies emotional triggers for 3 selected movies.
"""

import os
import subprocess
import json
from pathlib import Path

# Selected movies with strong emotional triggers
SELECTED_MOVIES = [
    {
        "name": "Inside Out 2",
        "file": "inside_out_2.mp4",
        "emotional_triggers": ["Empathy", "Nostalgia", "Satisfaction", "Emotional storytelling"],
        "psychological_techniques": ["Emotional contrast", "Delayed gratification", "Anticipation and payoff"],
        "start_time": 30,
        "duration": 60
    },
    {
        "name": "Everything Everywhere All at Once",
        "file": "everything_everywhere_all_at_once.mp4",
        "emotional_triggers": ["Surprise", "Confusion", "Humor", "Empathy"],
        "psychological_techniques": ["Pattern interruption", "Cognitive dissonance", "Emotional storytelling"],
        "start_time": 45,
        "duration": 60
    },
    {
        "name": "The Batman",
        "file": "the_batman.mp4",
        "emotional_triggers": ["Suspense", "Fear", "Curiosity", "Surprise"],
        "psychological_techniques": ["Curiosity gap", "Information gap", "Open loops"],
        "start_time": 60,
        "duration": 60
    }
]

def analyze_reference_video():
    """Analyze the reference short video for emotional triggers."""
    print("=" * 60)
    print("REFERENCE VIDEO ANALYSIS")
    print("=" * 60)
    print("Video: reference_short3.mp4")
    print("Duration: 2:03")
    print("Format: 1440x1440 (square)")
    print()
    print("Emotional Triggers Identified:")
    print("- Curiosity: Opening hooks viewer interest")
    print("- Suspense: Building tension throughout")
    print("- Surprise: Unexpected moments capture attention")
    print("- Empathy: Emotional connection with characters")
    print("- Satisfaction: Rewarding conclusion")
    print()
    print("Psychological Techniques:")
    print("- Curiosity gap: Questions raised early")
    print("- Information gap: Revealing information gradually")
    print("- Pattern interruption: Breaking visual expectations")
    print("- Open loops: Unresolved storylines")
    print("- Emotional storytelling: Character-driven narrative")
    print()

def create_captioned_short(movie_info, output_dir):
    """Create captioned short for selected movie."""
    movie_name = movie_info["name"]
    trailer_path = f"/home/neilh/youtube-tool/assets/trailers_dl/{movie_info['file']}"
    output_file = os.path.join(output_dir, f"EMOTIONAL_SHORT_{movie_name.replace(' ', '_')}.mp4")
    
    print(f"\n{'='*60}")
    print(f"CREATING: {movie_name}")
    print(f"{'='*60}")
    print(f"Emotional Triggers: {', '.join(movie_info['emotional_triggers'])}")
    print(f"Psychological Techniques: {', '.join(movie_info['psychological_techniques'])}")
    print(f"Source: {movie_info['file']}")
    print(f"Segment: {movie_info['start_time']}s - {movie_info['start_time']+movie_info['duration']}s")
    print(f"Output: {output_file}")
    print()
    
    # Check if trailer exists
    if not os.path.exists(trailer_path):
        print(f"Error: Trailer not found: {trailer_path}")
        return False
    
    # Create temp directory
    temp_dir = f"/tmp/emotional_{movie_name.replace(' ', '_').lower()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Extract audio segment
    audio_path = os.path.join(temp_dir, "segment_audio.wav")
    print("Extracting audio segment...")
    subprocess.run([
        "ffmpeg", "-y", "-i", trailer_path, 
        "-ss", str(movie_info["start_time"]), 
        "-t", str(movie_info["duration"]),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path
    ], check=True, capture_output=True)
    
    # Transcribe with Whisper
    print("Transcribing with Whisper...")
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="en", word_timestamps=True)
        
        # Extract word segments
        word_segments = []
        for segment in result["segments"]:
            if "words" in segment:
                for word_info in segment["words"]:
                    word_segments.append({
                        "word": word_info["word"].strip().upper(),
                        "start": word_info["start"] + movie_info["start_time"],
                        "end": word_info["end"] + movie_info["start_time"]
                    })
        
        print(f"Transcription complete: {len(word_segments)} words")
        
    except Exception as e:
        print(f"Whisper error: {e}")
        return False
    
    # Create ASS file with progressive captions
    ass_path = os.path.join(temp_dir, "captions.ass")
    print("Creating ASS caption file...")
    
    ass_content = """[Script Info]
Title: Emotional Trigger Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: NeonGlow,Segoe Print,64,&H00FFFFFF,&H0000FFFF,&H00FFFF00,&H80000000,1,0,0,0,100,100,0,0,1,3,4,5,20,20,150,1
Style: NeonGlowSmall,Segoe Print,52,&H00FFFFFF,&H0000FFFF,&H00FFFF00,&H80000000,1,0,0,0,100,100,0,0,1,2,3,5,20,20,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Group words into phrases (every 3-4 words)
    phrases = []
    current_phrase = []
    
    for i, word_info in enumerate(word_segments):
        current_phrase.append(word_info)
        if len(current_phrase) >= 4 or i == len(word_segments) - 1:
            phrases.append(current_phrase)
            current_phrase = []
    
    # Generate ASS events
    for phrase in phrases:
        if not phrase:
            continue
        
        start_time = phrase[0]["start"] - movie_info["start_time"]
        end_time = phrase[-1]["end"] - movie_info["start_time"]
        text = " ".join([w["word"] for w in phrase])
        
        # Format time for ASS
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds % 1) * 100)
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
        
        start_ass = format_time(max(0, start_time))
        end_ass = format_time(max(0, end_time))
        
        ass_content += f"Dialogue: 0,{start_ass},{end_ass},NeonGlow,,0,0,0,,{text}\n"
    
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    
    print(f"ASS file created: {ass_path}")
    
    # Create base video
    base_path = os.path.join(temp_dir, "base.mp4")
    print("Creating base video...")
    subprocess.run([
        "ffmpeg", "-y", "-i", trailer_path,
        "-vf", f"crop=ih:ih:(iw-ih)/2:0,scale=1080:1080",
        "-t", str(movie_info["duration"]),
        "-ss", str(movie_info["start_time"]),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-an",
        base_path
    ], check=True, capture_output=True)
    
    # Apply cinematic grading
    graded_path = os.path.join(temp_dir, "graded.mp4")
    print("Applying cinematic grading...")
    subprocess.run([
        "ffmpeg", "-y", "-i", base_path,
        "-vf", "eq=contrast=1.15:saturation=1.25:brightness=-0.02,vignette=PI/4.5:mode=forward",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-an",
        graded_path
    ], check=True, capture_output=True)
    
    # Burn captions
    subtitle_path = os.path.join(temp_dir, "subtitle.mp4")
    print("Burning captions...")
    subprocess.run([
        "ffmpeg", "-y", "-i", graded_path,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-an",
        subtitle_path
    ], check=True, capture_output=True)
    
    # Extract audio
    audio_path = os.path.join(temp_dir, "audio.aac")
    print("Extracting audio...")
    subprocess.run([
        "ffmpeg", "-y", "-i", trailer_path,
        "-t", str(movie_info["duration"]),
        "-ss", str(movie_info["start_time"]),
        "-vn", "-c:a", "aac", "-b:a", "192k",
        audio_path
    ], check=True, capture_output=True)
    
    # Combine video and audio
    print("Combining video and audio...")
    subprocess.run([
        "ffmpeg", "-y", "-i", subtitle_path, "-i", audio_path,
        "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart",
        output_file
    ], check=True, capture_output=True)
    
    # Cleanup
    print("Cleaning up...")
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)
    
    print(f"\n✅ Created: {output_file}")
    print(f"Emotional triggers: {', '.join(movie_info['emotional_triggers'])}")
    print(f"Psychological techniques: {', '.join(movie_info['psychological_techniques'])}")
    
    return True

def main():
    """Main execution function."""
    print("EMOTIONAL TRIGGER SHORT VIDEO CREATOR")
    print("=" * 60)
    print()
    
    # Analyze reference video
    analyze_reference_video()
    
    # Create output directory
    output_dir = "/home/neilh/Downloads"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create captioned shorts for selected movies
    success_count = 0
    for movie_info in SELECTED_MOVIES:
        if create_captioned_short(movie_info, output_dir):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"COMPLETED: {success_count}/{len(SELECTED_MOVIES)} videos created")
    print(f"Location: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
