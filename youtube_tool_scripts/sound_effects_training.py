#!/usr/bin/env python3
"""
Sound Effects Training Script
Demonstrates professional sound effect techniques for video editing.
"""

import os
import subprocess
import requests
from pathlib import Path

# Sound effect categories and descriptions
SOUND_EFFECTS = {
    "transitions": {
        "whoosh": "Smooth transition between scenes",
        "riser": "Builds tension before reveal",
        "impact": "Emphasizes dramatic moments",
        "hit": "Accents key visual moments"
    },
    "emphasis": {
        "boom": "Deep impact for major moments",
        "accent": "Highlights important points",
        "stinger": "Musical accent for transitions"
    },
    "atmosphere": {
        "ambient": "Creates environmental context",
        "wind": "Adds movement and energy",
        "crowd": "Adds scale and excitement"
    }
}

def download_sound_effects(output_dir):
    """Download free sound effects for training."""
    print("=" * 60)
    print("SOUND EFFECTS DOWNLOAD")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Free sound effect URLs (from Freesound.org - requires API key for production)
    # These are example URLs - in production, use licensed libraries
    sound_urls = {
        "whoosh_transition.wav": "https://freesound.org/data/previews/123/123456_7890123-lq.mp3",
        "riser_tension.wav": "https://freesound.org/data/previews/123/123457_7890124-lq.mp3",
        "impact_boom.wav": "https://freesound.org/data/previews/123/123458_7890125-lq.mp3",
        "hit_accent.wav": "https://freesound.org/data/previews/123/123459_7890126-lq.mp3",
        "ambient_wind.wav": "https://freesound.org/data/previews/123/123460_7890127-lq.mp3"
    }
    
    print("Note: These are example URLs. For production, use:")
    print("- Epidemic Sound (licensed)")
    print("- Artlist (licensed)")
    print("- SoundSnap (licensed)")
    print("- Freesound.org (requires API key)")
    print()
    
    # Create placeholder files for demonstration
    for filename in sound_urls.keys():
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            print(f"Creating placeholder: {filename}")
            # Create a simple sine wave as placeholder
            subprocess.run([
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=2",
                "-af", "volume=0.3",
                filepath
            ], check=True, capture_output=True)
    
    print(f"\nSound effects ready in: {output_dir}")

def add_sound_effects_to_video(input_video, output_video, sound_effects_dir):
    """Add professional sound effects to a video."""
    print("=" * 60)
    print("ADDING SOUND EFFECTS TO VIDEO")
    print("=" * 60)
    print(f"Input: {input_video}")
    print(f"Output: {output_video}")
    print(f"Sound Effects: {sound_effects_dir}")
    print()
    
    # Check if input exists
    if not os.path.exists(input_video):
        print(f"Error: Input video not found: {input_video}")
        return False
    
    # Get video duration
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", input_video
    ], capture_output=True, text=True)
    
    import json
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    print(f"Video duration: {duration:.2f} seconds")
    print()
    
    # Define sound effect placements (in seconds)
    # These would be customized based on video content
    sound_placements = [
        {"file": "whoosh_transition.wav", "time": 0.0, "volume": 0.5},
        {"file": "riser_tension.wav", "time": duration * 0.3, "volume": 0.4},
        {"file": "impact_boom.wav", "time": duration * 0.6, "volume": 0.6},
        {"file": "hit_accent.wav", "time": duration * 0.8, "volume": 0.5},
        {"file": "ambient_wind.wav", "time": 0.0, "volume": 0.2}  # Background throughout
    ]
    
    print("Sound Effect Placements:")
    for placement in sound_placements:
        print(f"  {placement['file']} at {placement['time']:.1f}s (volume: {placement['volume']})")
    print()
    
    # Build FFmpeg command with multiple audio inputs
    cmd = ["ffmpeg", "-y", "-i", input_video]
    
    # Add sound effect inputs
    for placement in sound_placements:
        sound_path = os.path.join(sound_effects_dir, placement["file"])
        if os.path.exists(sound_path):
            cmd.extend(["-i", sound_path])
    
    # Build filter complex
    filter_complex = ""
    audio_inputs = []
    
    # Original audio (input 0)
    filter_complex += "[0:a]volume=1.0[a0];"
    audio_inputs.append("[a0]")
    
    # Sound effects (inputs 1, 2, 3, etc.)
    for i, placement in enumerate(sound_placements):
        if i + 1 < len(cmd) // 2:  # Rough check if input exists
            filter_complex += f"[{i+1}:a]volume={placement['volume']},adelay={int(placement['time']*1000)}|{int(placement['time']*1000)}[a{i+1}];"
            audio_inputs.append(f"[a{i+1}]")
    
    # Mix all audio
    filter_complex += f"{''.join(audio_inputs)}amix=inputs={len(audio_inputs)}:duration=first:dropout_transition=2[aout]"
    
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_video
    ])
    
    print("Running FFmpeg command...")
    print(" ".join(cmd))
    print()
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Sound effects added successfully!")
        print(f"Output: {output_video}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error adding sound effects: {e}")
        return False

def create_sound_effect_timeline(video_path, output_dir):
    """Create a sound effect timeline for professional editing."""
    print("=" * 60)
    print("SOUND EFFECT TIMELINE CREATION")
    print("=" * 60)
    print(f"Video: {video_path}")
    print(f"Output: {output_dir}")
    print()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ], capture_output=True, text=True)
    
    import json
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    
    print(f"Video duration: {duration:.2f} seconds")
    print()
    
    # Create timeline markers
    timeline = {
        "video": video_path,
        "duration": duration,
        "sound_effects": [
            {
                "timestamp": 0.0,
                "type": "transition",
                "description": "Opening whoosh",
                "volume": 0.5,
                "fade_in": 0.1,
                "fade_out": 0.2
            },
            {
                "timestamp": duration * 0.2,
                "type": "atmosphere",
                "description": "Ambient wind bed",
                "volume": 0.2,
                "fade_in": 1.0,
                "fade_out": 1.0
            },
            {
                "timestamp": duration * 0.4,
                "type": "emphasis",
                "description": "Impact moment",
                "volume": 0.6,
                "fade_in": 0.05,
                "fade_out": 0.3
            },
            {
                "timestamp": duration * 0.6,
                "type": "transition",
                "description": "Scene transition riser",
                "volume": 0.4,
                "fade_in": 0.5,
                "fade_out": 0.1
            },
            {
                "timestamp": duration * 0.8,
                "type": "emphasis",
                "description": "Final accent",
                "volume": 0.5,
                "fade_in": 0.1,
                "fade_out": 0.5
            }
        ],
        "music_cues": [
            {
                "timestamp": 0.0,
                "type": "intro",
                "description": "Opening theme",
                "volume": 0.3
            },
            {
                "timestamp": duration * 0.5,
                "type": "climax",
                "description": "Emotional peak",
                "volume": 0.4
            },
            {
                "timestamp": duration * 0.9,
                "type": "outro",
                "description": "Resolution theme",
                "volume": 0.3
            }
        ]
    }
    
    # Save timeline as JSON
    timeline_path = os.path.join(output_dir, "sound_effect_timeline.json")
    import json
    with open(timeline_path, "w") as f:
        json.dump(timeline, f, indent=2)
    
    print(f"Timeline created: {timeline_path}")
    print()
    print("Sound Effect Timeline:")
    for effect in timeline["sound_effects"]:
        print(f"  {effect['timestamp']:.1f}s: {effect['description']} ({effect['type']})")
    print()
    print("Music Cues:")
    for cue in timeline["music_cues"]:
        print(f"  {cue['timestamp']:.1f}s: {cue['description']} ({cue['type']})")
    
    return timeline_path

def main():
    """Main execution function."""
    print("SOUND EFFECTS TRAINING SCRIPT")
    print("=" * 60)
    print()
    
    # Setup directories
    sound_effects_dir = "/tmp/sound_effects"
    output_dir = "/home/neilh/Downloads/sound_effects_training"
    
    # Step 1: Download/prepare sound effects
    download_sound_effects(sound_effects_dir)
    
    # Step 2: Create sound effect timeline for reference video
    reference_video = "/tmp/reference_short3.mp4"
    if os.path.exists(reference_video):
        timeline_path = create_sound_effect_timeline(reference_video, output_dir)
        
        # Step 3: Add sound effects to reference video (demonstration)
        output_video = os.path.join(output_dir, "reference_with_effects.mp4")
        add_sound_effects_to_video(reference_video, output_video, sound_effects_dir)
    
    print(f"\n{'='*60}")
    print("TRAINING COMPLETE")
    print(f"{'='*60}")
    print(f"Sound effects directory: {sound_effects_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Timeline file: {timeline_path if 'timeline_path' in locals() else 'N/A'}")
    print()
    print("Next steps:")
    print("1. Review the timeline JSON for editing reference")
    print("2. Customize sound effect placements for your videos")
    print("3. Use professional sound libraries for production")
    print("4. Practice A/B testing with and without effects")

if __name__ == "__main__":
    main()
