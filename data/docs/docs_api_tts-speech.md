# Generate speech · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/tts-speech

Text to Speech · API
Generate speech
Turn text into speech and get the audio back.
POST
https://api.audiclabs.com/v1/tts/speech
Request
Send JSON. Costs 1 credit per call. Needs the
tts:speech
scope.
model
string
required
Always
audic-tts-1
.
input
string
required
The text to speak.
voice
string
required
A voice id from
GET /voices
, e.g.
voice_bilal_en
.
speed
number
optional
Optional. Speaking rate;
1.0
is normal.
language
string
optional
Optional. A code from
GET /languages
. Defaults to the voice's language.
response_format
string
optional
Optional. Audio format of the result. Default
mp3
.
stream
boolean
optional
Optional. Default
true
: the MP3 is sent in pieces as it is generated, so playback can start after about a second.
false
returns the whole file at once. See
Generate speech (streaming)
.
Example
curl -o hello.mp3 https://api.audiclabs.com/v1/tts/speech \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"audic-tts-1","input":"Hello from AudicLabs.","voice":"voice_bilal_en"}'
Response
200
with the audio as
audio/mpeg
. A short sentence takes about one to three seconds.
Errors use the standard format, see
Errors
. A missing or unknown
model
returns
400
or
404
with the accepted value in the message; an unknown voice returns
400
.
Previous
Guide
Next
Generate speech (streaming)
