# Text to Speech · AudicLabs

Source URL: https://docs.audiclabs.com/docs/text-to-speech

Text to Speech
Text to Speech
Turn text into natural speech with the
audic-tts-1
model. Use it in the console or call it from code; both run on the AudicLabs GPU cluster and return MP3.
In the console
Open
Text to Speech
, type or paste up to 5,000 characters, pick a voice and a speed, and press
Generate speech
(or Ctrl / ⌘ + Enter). Playback starts after about a second, while the rest is still being generated; when it finishes you can download the MP3, and every clip is kept in your history. Press ▶ next to a voice to hear a free sample first. Each clip costs 1 credit.
Voices
Voice id
Name
Language
voice_bilal_en
Bilal
English
voice_enjood_ar
Enjood
afb (Emirati)
voice_priya_en_in
Priya
English (Indian)
voice_arjun_en_in
Arjun
English (Indian)
voice_saikiran_en_in
Saikiran
English (Indian)
This table is the live catalogue; new voices appear here as they are onboarded. From code, use
GET /voices
and pass a
voice_id
. Every voice can speak every language; the language shown is that of its reference recording.
Settings
Setting
What it does
Voice
Who speaks. Required.
Speed
Speaking rate from 0.5× to 2×; 1× is the voice's natural pace.
Language
Optional. Defaults to the voice's language. The model accepts the codes listed by GET /languages.
Write numbers, dates and abbreviations the way they should be read aloud ("twelve percent", "A B C") for the most natural result.
API reference
Generate speech
POST /speech · text in, MP3 out.
Generate speech (streaming)
Streamed HTTP or WS /stream · play while it is generated.
Voices, languages & health
GET /voices, /languages and /health.
Previous
Health
Next
Generate speech
