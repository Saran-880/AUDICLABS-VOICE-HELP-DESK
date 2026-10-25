# Quickstart · AudicLabs

Source URL: https://docs.audiclabs.com/docs/quickstart

Get started
Quickstart
Create a key, send a noisy recording, get clean speech back. About two minutes.
1. Create an API key
Sign in to the
console
, add credits under
Billing
(new accounts start with 0; 1,000 credits cost $10), then create a key under
API keys
. Keys start with
mw_live_
and are shown once, so store it somewhere safe, then export it:
export AUDICLABS_API_KEY="mw_live_..."
2. Send your first request
Upload a recording to the Noise Suppressor. Any common format and sample rate works.
curl -OJ https://api.audiclabs.com/v1/noise-suppressor/denoise \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -F file=@meeting.wav
No recording to hand? Download the test clip first with
GET /sample
, see
Sample clip
.
3. Go further
Pick a model for your quality and speed needs in
Models
, clean many files at once with the
bulk endpoint
, clean live audio in real time with
streaming
, or try everything interactively in the
API explorer
.
The same key works for every API: turn text into speech with
Text to Speech
and transcribe recordings with
Speech to Text
.
Previous
Overview
Next
Models
