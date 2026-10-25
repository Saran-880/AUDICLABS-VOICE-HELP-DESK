# Models · AudicLabs

Source URL: https://docs.audiclabs.com/docs/models

Get started
Models
The Audic models: noise suppression (Audic 1 to Audic 5, with Audic 2 by default) and the speech models
audic-tts-1
,
audic-stt-1
and
audic-diar-1
.
Catalogue
Model
Id
Rate
Best for
Audic 1
audic-1
16 kHz
Real-time and high-volume jobs; the fastest, about 10× realtime.
Audic 2
audic-2
16 kHz
The default for most speech; balanced quality and speed.
Audic 3
audic-3
16 kHz
Cleaner output when you can spend a little more time.
Audic 4
audic-4
16 kHz
The best 16 kHz quality, about 2× realtime.
Audic 5
audic-5
48 kHz
Full-band audio for broadcast, podcasts and music beds.
Every model accepts any input sample rate. Files come back at the rate you sent; streaming returns audio at the model's rate (Audic 1 has the lowest streaming delay). To use one other than Audic 2, add its id as the optional
model
field. The live list is always at
GET /models
.
Choosing a model
Start with Audic 2. Move to Audic 1 if you need speed or process large volumes, to Audic 3 or Audic 4 if residual noise is audible, and to Audic 5 when the source is full-band (44.1 or 48 kHz) and you want to keep high frequencies.
Speech models
Model
API
What it does
audic-tts-1
Text to Speech
Natural speech from text with a growing voice catalogue (English, Arabic, Indian English). MP3 out.
audic-stt-1
Speech to Text
Transcription in 40 languages with automatic language detection.
audic-diar-1
Speaker Diarization
Who spoke when: up to 8 speakers, recordings of any length.
Each runs on the AudicLabs GPU cluster.
model
is required for Text to Speech and optional for the others.
Upcoming
Audic 6 (48 kHz) and Audic 7 and Audic 8 (8 kHz telephony) are listed by
GET /models
with
available: false
, and become usable without any change on your side once they are installed.
Previous
Quickstart
Next
APIs
