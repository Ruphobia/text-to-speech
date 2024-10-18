#!/usr/bin/python3.11
import io
import tornado.ioloop
import tornado.web
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# --- Global Settings ---
PLAYBACK_SPEED = 1.5  # Speed of the playback, 1.0 is normal speed
PITCH_LOWERING = 0.5  # Amount to lower the pitch, 1.0 means no pitch change
BASS_BOOST_DB = 12  # dB increase for bass boost
LOW_PASS_FILTER_FREQ = 20000  # Frequency threshold for low-pass filter (higher = more bass)
DISTORTION_GAIN_DB = 3  # dB gain to simulate distortion
APPLY_REVERB = True  # True to apply reverb, False to disable
REVERB_DELAY_MS = 100  # Reverb delay in milliseconds
REVERB_POSITION_MS = 100  # Position offset for reverb overlay
HIGHPASS_FILTER_FREQ = 2000  # Frequency threshold for high-pass filter (higher = crisper)
TREBLE_BOOST_DB = 6  # Treble boost to add sharpness

class SpeechHandler(tornado.web.RequestHandler):
    def post(self):
        text = self.get_argument("text", None)

        if not text:
            self.set_status(400)
            self.write({"error": "No text provided"})
            return

        # Synthesize and process the speech, and play it directly
        synthesize_and_play_speech(text)
        self.write({"status": "Speech played successfully"})

def synthesize_and_play_speech(text):
    # Create a TTS object and save the audio to an in-memory buffer
    tts = gTTS(text=text, lang='en', slow=True)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    # Load the audio from the buffer using pydub
    audio_segment = AudioSegment.from_file(audio_buffer, format="mp3")

    # Speed up the speech
    faster_audio = audio_segment.speedup(playback_speed=PLAYBACK_SPEED)

    # Lower the pitch
    lower_pitch = faster_audio._spawn(faster_audio.raw_data, overrides={
        "frame_rate": int(faster_audio.frame_rate * PITCH_LOWERING)
    }).set_frame_rate(faster_audio.frame_rate)

    # Apply bass boost
    bass_boost = lower_pitch.low_pass_filter(LOW_PASS_FILTER_FREQ)
    bass_boost = bass_boost + BASS_BOOST_DB  # Boost bass

    # Apply distortion gain
    distorted = bass_boost + DISTORTION_GAIN_DB  # Add gain for distortion

    # Normalize the volume to avoid clipping
    normalized = distorted.normalize()

    # Apply reverb if enabled
    final_output = normalized
    if APPLY_REVERB:
        reverb = final_output + AudioSegment.silent(duration=REVERB_DELAY_MS)
        final_output = reverb.overlay(final_output, position=REVERB_POSITION_MS)

    # Apply high-pass filter to crisp up the audio
    crisp_audio = final_output.high_pass_filter(HIGHPASS_FILTER_FREQ)

    # Boost treble to add sharpness
    crisp_audio = crisp_audio + TREBLE_BOOST_DB

    # Play the final altered audio directly
    play(crisp_audio)

def make_app():
    return tornado.web.Application([
        (r"/synthesize", SpeechHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server started on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
