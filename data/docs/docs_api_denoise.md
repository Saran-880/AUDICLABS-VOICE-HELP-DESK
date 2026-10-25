# Remove noise · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/denoise

Noise Suppressor · API
Remove noise
Clean one audio or video file and get the cleaned audio back.
POST
https://api.audiclabs.com/v1/noise-suppressor/denoise
Request
Send
multipart/form-data
with your file. Everything else is handled for you. Costs 1 credit per call. Needs the
noise-suppressor:denoise
scope.
file
file
required
The audio or video to clean. Any common format and sample rate, up to 100 MB.
model
string
optional
Optional. One of
audic-1
to
audic-5
, see
Models
. Leave it out to use Audic 2.
Example
curl -OJ https://api.audiclabs.com/v1/noise-suppressor/denoise \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -F file=@meeting.wav
curl -OJ
saves the result under the name the API sends, so
meeting.wav
comes back as
audiclabs.ns.meeting.wav
.
Response
200
with the cleaned audio (
audio/wav
, at the sample rate you uploaded) as an attachment named
audiclabs.ns.<your file name>.wav
. Processing stats are in the
X-NS-Stats
header:
{
  "model": "audic-2",
  "model_sample_rate": 16000,
  "input_sample_rate": 16000,
  "output_sample_rate": 16000,
  "duration_s": 9.769,
  "processing_s": 3.725,
  "rtf": 0.381
}
Errors use the standard format, see
Errors
. An unknown model returns
400
.
Previous
Guide
Next
Remove noise (bulk)
