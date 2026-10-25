# Authentication · AudicLabs

Source URL: https://docs.audiclabs.com/docs/authentication

Platform
Authentication
Every API is reached through the gateway at
https://api.audiclabs.com/v1/{service}/{endpoint}
with an access token.
Access tokens
Create tokens in the console under
API keys
. A token looks like
mw_live_
followed by 32 characters and is shown once; only a hash is stored, so a lost token is replaced, not recovered. Keep tokens on your server, never in browser or mobile code.
Sending the token
Use either header. They are equivalent.
Authorization: Bearer mw_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Scopes
Each token carries scopes that decide what it can call:
Scope
Allows
*
Every published API.
noise-suppressor:*
Every Noise Suppressor endpoint.
noise-suppressor:denoise
Only POST /denoise.
noise-suppressor:denoise-batch
Only POST /denoise/batch.
noise-suppressor:stream
Only the WS /stream streaming endpoint.
tts:*
Every Text to Speech endpoint.
tts:speech
Only POST /tts/speech.
tts:stream
Only the WS /tts/stream streaming endpoint.
stt:*
Every Speech to Text endpoint.
stt:transcriptions
Only POST /stt/transcriptions.
stt:stream
Only the WS /stt/stream live endpoint.
diarization:*
Every Speaker Diarization endpoint.
diarization:diarize
Only POST /diarization/diarize.
Give each integration the narrowest scope it needs, and one token per integration, so you can revoke one without breaking the others.
WebSockets from a browser
Browsers cannot send headers on a WebSocket. For
streaming
from a web page, your server exchanges its token for a single-use ticket at
POST
https://api.audiclabs.com/v1/tickets
and the page connects with
?ticket=
. A ticket lasts 60 seconds, opens one session on one endpoint, needs the same scope as the endpoint, and stops working when its token is revoked.
A missing, unknown, revoked or expired token returns
401
; a valid token without the scope returns
403
. See
Errors
.
Previous
Models & health
Next
Errors
