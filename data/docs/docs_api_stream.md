# Remove noise (streaming) · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/stream

Noise Suppressor · API
Remove noise (streaming)
Clean live audio in real time over a WebSocket: send audio frames as they are captured and get cleaned frames back a fraction of a second later. For files you already have, use
Remove noise
instead.
WS
wss://api.audiclabs.com/v1/noise-suppressor/stream
Connect
Open a WebSocket to the address above. Costs 1 credit per session, and needs the
noise-suppressor:stream
scope. All query parameters are optional:
sample_rate
integer
optional
Sample rate of the audio you send,
8000
to
192000
. Default
16000
. Send your capture rate (a browser microphone is usually
48000
); it is converted for you.
format
string
optional
f32
(default) or
s16
: the PCM encoding of every binary frame, in both directions.
model
string
optional
One of
audic-1
to
audic-5
, see
Models
. Leave it out to use Audic 2. Audic 1 has the lowest latency; Audic 5 streams full-band 48 kHz.
ticket
string
optional
Browsers only: a single-use ticket instead of a header, see
From a browser
.
Servers authenticate with the usual
Authorization: Bearer
or
X-API-Key
header, see
Authentication
.
Protocol
The first message is JSON. It tells you the rate the cleaned audio comes back at, which is the model's rate (16 kHz for Audic 1 to 4, 48 kHz for Audic 5):
{
  "type": "ready",
  "model": "audic-2",
  "input_sample_rate": 48000,
  "output_sample_rate": 16000,
  "frame_shift_samples": 160,
  "format": "f32"
}
You send
You get
Binary frame
Mono little-endian PCM at sample_rate, in format. 10 to 100 ms per frame works well; 20 ms is typical. Cleaned PCM comes back as binary frames, in order, in the same format.
flush
Text command. Send it after your last frame: the rest of the cleaned audio arrives, then {"type": "flushed", "processed_s", "rtf"}. The session stays open.
reset
Text command. Starts a new utterance on the same session: {"type": "reset"}.
stats
Text command. {"type": "stats", "processed_s", "rtf"}: seconds processed so far and the real-time factor.
Cleaned audio lags the input by the model's look-ahead plus your frame size, typically well under a second. Close the socket when you are done.
Example
Stream a WAV file in real time and save the cleaned result, the way a live source would send it:
import asyncio, json, os

import numpy as np
import soundfile as sf
import websockets  # pip install websockets numpy soundfile

URL = "wss://api.audiclabs.com/v1/noise-suppressor/stream"


async def main():
    audio, sr = sf.read("meeting.wav", dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)  # mono
    headers = {"Authorization": f"Bearer {os.environ['AUDICLABS_API_KEY']}"}
    async with websockets.connect(f"{URL}?sample_rate={sr}", additional_headers=headers) as ws:
        ready = json.loads(await ws.recv())
        cleaned = []

        async def receive():
            async for msg in ws:
                if isinstance(msg, bytes):
                    cleaned.append(np.frombuffer(msg, np.float32))
                elif json.loads(msg)["type"] == "flushed":
                    return

        reader = asyncio.create_task(receive())
        frame = sr // 50  # 20 ms
        for i in range(0, len(audio), frame):
            await ws.send(audio[i:i + frame].tobytes())
            await asyncio.sleep(0.02)  # real time, like a microphone
        await ws.send("flush")
        await reader

    sf.write("audiclabs.ns.meeting.wav", np.concatenate(cleaned), ready["output_sample_rate"])


asyncio.run(main())
From a browser
A browser cannot set headers on a WebSocket, and your token must never reach a web page. Instead, your server trades its token for a
ticket
: valid for 60 seconds, for one session on one endpoint, and only once. The page connects with
?ticket=
.
POST
https://api.audiclabs.com/v1/tickets
// e.g. POST /ns-ticket on your backend
const r = await fetch("https://api.audiclabs.com/v1/tickets", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${process.env.AUDICLABS_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ service: "noise-suppressor", endpoint: "stream" }),
});
return Response.json(await r.json(), { status: r.status });
// -> { "ticket": "wst_…", "expires_in": 60, "url": "wss://api.audiclabs.com/v1/noise-suppressor/stream", ... }
The
Noise Suppressor
's Streaming mode in the console works exactly this way.
Limits and billing
Limit
Value
Cost
1 credit per session, charged when the session opens. A session counts as one request toward rate limits and quotas.
Session length
Up to 60 minutes; the session then closes normally (code 1000). Reconnect to continue.
Frame size
Up to 1 MB per frame.
Ticket
60 seconds, one session, one endpoint. Revoking the token also revokes its tickets.
Errors
A refused or failed session receives one JSON message in the standard
error format
(inside
{"type": "error", ...}
), then a close code of 4000 plus the HTTP status the same error would have:
Close code
Meaning
1000
Normal close, including the 60-minute session limit.
4400
Invalid settings, such as an unknown model.
4401
Missing or invalid token, or an unknown, expired or used ticket (invalid_ticket).
4402
Credits or monthly quota used up.
4403
Token lacks the noise-suppressor:stream scope, is revoked or expired, or the plan excludes the service.
4404
No such streaming endpoint.
4413
A frame larger than 1 MB.
4429
Rate limited.
4503 / 4504
The service is unavailable or did not answer in time. Retry with backoff.
Tip
Only realtime sources need streaming. If you have the whole recording,
Remove noise
is simpler and runs faster than real time.
Previous
Remove noise (bulk)
Next
List models
