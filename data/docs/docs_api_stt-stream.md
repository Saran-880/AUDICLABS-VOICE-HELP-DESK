# Transcribe live (streaming) · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/stt-stream

Speech to Text · API
Transcribe live (streaming)
Transcribe speech as it is spoken over a WebSocket: send audio frames as they are captured and get the transcript so far after each one, then the final transcript when you stop. For recordings you already have, use
Transcribe audio
.
WS
wss://api.audiclabs.com/v1/stt/stream
Connect
Open a WebSocket to the address above. Costs 1 credit per session and needs the
stt:stream
scope. Servers authenticate with the
Authorization: Bearer
or
X-API-Key
header; browsers use a ticket, see
From a browser
.
Protocol
Send a JSON start message first. Every field is optional:
type
string
required
Always
start
.
language
string
optional
A code from
GET /languages
, e.g.
en-US
, or
auto
(default) to detect it.
sample_rate
integer
optional
Rate of the PCM you send. Default
16000
; other rates are converted for you.
chunk_ms
integer
optional
How often partial results update:
80
,
320
(default),
560
or
1120
. Lower is faster, higher is more accurate.
words
boolean
optional
Include word timings in the final message. Default
false
.
The service answers with
ready
; start sending audio after it:
{ "type": "ready", "session_id": "req_…", "model": "audic-stt-1", "language": "en-US", "chunk_ms": 320, "sample_rate": 16000 }
You send
You get
Binary frame
16-bit little-endian mono PCM at sample_rate, up to 2 seconds per frame (320 ms is typical). As the transcript grows you get {"type": "partial", "text", "delta", "audio_seconds", "lag_ms"}: the whole text so far, and the new part when it only extended.
{"type": "stop"}
Ends the session: you get {"type": "final", "text", "language", "audio_seconds"} (plus "words" when requested), then the socket closes with code 1000.
Errors arrive as
{"type": "error", "code", "message"}
followed by a close. A session closes after 30 s without audio (
idle_timeout
); gateway refusals (bad key, no credits, plan) arrive the same way with a close code of 4000 + the HTTP status, e.g.
4401
.
Example (server)
import asyncio, json, os, subprocess
import websockets  # pip install websockets

URL = "wss://api.audiclabs.com/v1/stt/stream"

async def main():
    # any audio file -> 16 kHz 16-bit mono PCM, streamed in 320 ms frames like a live microphone
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", "meeting.mp3", "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    headers = {"Authorization": f"Bearer {os.environ['AUDICLABS_API_KEY']}"}
    async with websockets.connect(URL, additional_headers=headers) as ws:
        await ws.send(json.dumps({"type": "start", "language": "en-US", "sample_rate": 16000}))
        print(json.loads(await ws.recv()))                  # ready

        async def send():
            step = 16000 * 2 * 320 // 1000
            for i in range(0, len(pcm), step):
                await ws.send(pcm[i:i + step])
                await asyncio.sleep(0.32)
            await ws.send(json.dumps({"type": "stop"}))

        sender = asyncio.create_task(send())
        async for message in ws:
            m = json.loads(message)
            if m["type"] == "partial":
                print("…", m["text"])
            elif m["type"] == "final":
                print("final:", m["text"])
                break
        await sender

asyncio.run(main())
From a browser
Browsers cannot set headers on a WebSocket. Have your server mint a single-use ticket, valid for 60 seconds, with
POST
https://api.audiclabs.com
/v1/tickets
and the body
{"service": "stt", "endpoint": "stream"}
, then connect with
?ticket=
. Your API key never reaches the page.
// server: const { ticket, url } = await (await fetch("https://api.audiclabs.com/v1/tickets", {
//   method: "POST", headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
//   body: JSON.stringify({ service: "stt", endpoint: "stream" }) })).json();

const ws = new WebSocket(`${url}?ticket=${ticket}`);
ws.onopen = () => ws.send(JSON.stringify({ type: "start", language: "auto", sample_rate: 16000 }));
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.type === "ready") startMicrophone();          // then ws.send(int16Frame.buffer) every 320 ms
  if (m.type === "partial") showLive(m.text);
  if (m.type === "final") showFinal(m.text);
};
// when the user stops: ws.send(JSON.stringify({ type: "stop" }));
Try it without code:
Speech to Text
→
Live
streams your microphone and shows the transcript as you speak.
Previous
Transcribe audio
Next
Models, languages & health
