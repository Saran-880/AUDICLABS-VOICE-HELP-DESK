# Rate limits & quotas · AudicLabs

Source URL: https://docs.audiclabs.com/docs/rate-limits

Platform
Rate limits & quotas
Requests are limited per minute and paid for with prepaid credits on your workspace.
Plans
Plan
Requests / minute
Credits
Pay as you go
120
Prepaid: 1,000 credits for $10. New accounts start with 0.
Enterprise
Custom
Custom volume, agreed with AudicLabs.
Credits
Endpoint
Credits per call
POST /denoise
1
POST /denoise/batch
1
WS /stream
1 per session
GET /models, /sample, /health
0
Buy credits in the console under Billing. When they run out, calls return
402 quota_exhausted
(close code
4402
for streaming) until you add more. Credits do not expire.
Response headers
Header
Meaning
RateLimit-Limit
Requests allowed per minute for this token.
RateLimit-Remaining
Requests left in the current window.
RateLimit-Reset
Seconds until the window resets.
Retry-After
On 429 only: seconds to wait before retrying.
X-Request-Id
Correlates the call with the gateway request log.
X-Gateway-Upstream-Ms
Time the model service took, in milliseconds.
X-NS-Stats / X-NS-Batch
Noise Suppressor processing stats for single and bulk calls.
Size limits
One file up to 100 MB per
/denoise
call. Up to 25 files and 200 MB per
/denoise/batch
call. Larger requests return
413 payload_too_large
. A streaming session counts as one request, lasts up to 60 minutes and takes frames up to 1 MB each.
Text to Speech: a JSON body up to 1 MB per
/tts/speech
call (the console allows 5,000 characters per clip). Speech to Text: one file up to 100 MB per
/stt/transcriptions
call; a live
/stt/stream
session counts as one request, takes frames up to 2 seconds of audio and closes after 30 s without audio. Requests can run for up to 5 minutes (TTS) and 10 minutes (STT) before the gateway times out.
Speaker Diarization: one file up to 200 MB and 4 hours of audio per
/diarization/diarize
call; requests can run for up to 15 minutes. When every worker is busy the call returns
503
with
Retry-After
.
Previous
Errors
Next
Architecture
