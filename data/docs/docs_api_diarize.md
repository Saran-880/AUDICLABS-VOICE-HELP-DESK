# Diarize audio · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/diarize

Speaker Diarization · API
Diarize audio
Find who spoke when in one recording.
POST
https://api.audiclabs.com/v1/diarization/diarize
Request
Send
multipart/form-data
with your file. Costs 1 credit per call. Needs the
diarization:diarize
scope.
file
file
required
The recording. Any common audio or video format, up to 200 MB and 4 hours.
merge_gap
number
optional
Optional. Join a speaker's segments separated by a pause up to this many seconds, 0 to 5. Default
0
.
threshold
number
optional
Optional. Speech detection sensitivity, 0.05 to 0.95. Default
0.5
.
response_format
string
optional
Optional.
json
(default) or
rttm
.
Example
curl https://api.audiclabs.com/v1/diarization/diarize \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -F file=@meeting.wav \
  -F merge_gap=0.5
Response
200
with JSON. Speakers are numbered by first appearance; times are in seconds. Example: a 28.5 s, three-speaker call with
merge_gap=0.5
.
{
  "model": "audic-diar-1",
  "duration": 28.536,
  "num_speakers": 3,
  "speakers": [
    { "speaker": "speaker_1", "talk_time": 10.13 },
    { "speaker": "speaker_2", "talk_time": 5.79 },
    { "speaker": "speaker_3", "talk_time": 5.06 }
  ],
  "segments": [
    { "speaker": "speaker_1", "start": 0.23, "end": 1.29 },
    { "speaker": "speaker_1", "start": 2.24, "end": 3.69 },
    { "speaker": "speaker_1", "start": 4.3, "end": 7.3 },
    …
    { "speaker": "speaker_3", "start": 23.29, "end": 28.35 }
  ],
  "processing_ms": 615
}
Errors use the standard format, see
Errors
. A file that is not readable audio returns
422
with
invalid_audio
; a busy service returns
503
with a
Retry-After
header.
Previous
Guide
Next
Models & health
