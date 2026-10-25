# Speech to Text · AudicLabs

Source URL: https://docs.audiclabs.com/docs/speech-to-text

Speech to Text
Speech to Text
Transcribe recordings in 40 languages with the
audic-stt-1
model, with automatic language detection. Use it in the console or call it from code; both run on the AudicLabs GPU cluster.
In the console
Open
Speech to Text
, upload a file or record from your microphone, and press
Transcribe
. Copy the transcript or download it as a text file. Each file costs 1 credit.
Choose
Live
to transcribe as you speak: the words appear while you talk, and Stop gives the final transcript. Each live session costs 1 credit. Files and live sessions are kept in your history.
Settings
Setting
What it does
Language
Detect automatically (default), or set it for faster and more accurate results.
Vocabulary hint
Optional. Names and terms to spell correctly, e.g. AudicLabs, Riyadh.
Languages
Tier
Languages
Ready
English (US, UK), Spanish (US, ES), French (FR, CA), Italian, Portuguese (BR, PT), Dutch, German, Turkish, Russian, Arabic, Hindi, Japanese, Korean, Vietnamese, Ukrainian
Broad
Polish, Swedish, Czech, Norwegian Bokmål, Danish, Bulgarian, Finnish, Croatian, Slovak, Chinese (Mandarin), Hungarian, Romanian, Estonian
Adaptation
Greek, Lithuanian, Latvian, Maltese, Slovenian, Hebrew, Thai, Norwegian Nynorsk
The live list with codes is at
GET /languages
.
Inputs: WAV, MP3, M4A/AAC, FLAC, OGG/Opus, WebM, AMR and the audio track of common video files, up to 100 MB. Clean noisy audio first with the
Noise Suppressor
for better accuracy.
API reference
Transcribe audio
POST /transcriptions · audio in, text out.
Transcribe live (streaming)
WS /stream · words as they are spoken.
Models, languages & health
GET /models, /languages and /health.
Previous
Voices, languages & health
Next
Transcribe audio
