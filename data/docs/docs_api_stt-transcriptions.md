# Transcribe audio · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/stt-transcriptions

Speech to Text · API
Transcribe audio
Turn a recording into text.
POST
https://api.audiclabs.com/v1/stt/transcriptions
Request
Send
multipart/form-data
with your file. Costs 1 credit per call. Needs the
stt:transcriptions
scope.
file
file
required
The audio or video to transcribe. Any common format, up to 100 MB.
model
string
optional
Optional.
audic-stt-1
.
language
string
optional
Optional. A code from
GET /languages
, e.g.
en-US
. Leave it out to detect the language.
prompt
string
optional
Optional. Names or terms to steer spelling, e.g. AudicLabs.
response_format
string
optional
Optional. Default
json
.
Example
curl https://api.audiclabs.com/v1/stt/transcriptions \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -F file=@meeting.mp3 \
  -F language=en-US
Response
200
with JSON:
{ "text": "Hello from AudicLabs. The tunnel to the GPU server is working." }
Errors use the standard format, see
Errors
. A file that is not readable audio returns
422
with
invalid_audio
.
Previous
Guide
Next
Transcribe live (streaming)
