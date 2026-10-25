# Generate speech (streaming) · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/tts-stream

Text to Speech · API
Generate speech (streaming)
Start playing speech about a second after you ask for it, while the rest is still being generated. Two ways: plain HTTP, where
POST /speech
already streams, or a WebSocket with progress messages and cancel.
Over HTTP
POST
https://api.audiclabs.com/v1/tts/speech
POST /speech
streams by default (
stream: true
): the response is one MP3 sent in pieces as it is generated, with no
Content-Length
. Read the body as it arrives and feed it to your player. Send
stream: false
to receive the whole file at once instead. Same price, 1 credit per call.
# plays as it downloads (needs ffplay)
curl -sN https://api.audiclabs.com/v1/tts/speech \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"audic-tts-1","input":"Hello from AudicLabs.","voice":"voice_bilal_en"}' | ffplay -nodisp -autoexit -
Over a WebSocket
WS
wss://api.audiclabs.com/v1/tts/stream
One utterance per connection. Costs 1 credit per session and needs the
tts:stream
scope. Servers authenticate with the
Authorization: Bearer
or
X-API-Key
header; browsers connect with
?ticket=
, see
From a browser
.
Protocol
Send one JSON request:
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
Optional. Defaults to the voice's language.
You get
Meaning
{"type": "start", "format": "mp3", "sample_rate": 24000, ...}
Generation started; the audio format.
Binary frames
Consecutive pieces of ONE MP3 stream. Append them in order; you can start playing after the first.
{"type": "done", "status": "completed", "audio_seconds", "bytes", "first_audio_ms"}
All audio sent; the socket closes with code 1000.
{"type": "error", "error": {message, code}}
The request was refused or failed; the socket closes.
Send
{"type": "cancel"}
at any time to stop early; you get
done
with
status: cancelled
.
import asyncio, json, os
import websockets  # pip install websockets

async def main():
    headers = {"Authorization": f"Bearer {os.environ['AUDICLABS_API_KEY']}"}
    async with websockets.connect("wss://api.audiclabs.com/v1/tts/stream", additional_headers=headers) as ws:
        await ws.send(json.dumps({"model": "audic-tts-1", "input": "Hello from AudicLabs.", "voice": "voice_bilal_en"}))
        with open("hello.mp3", "wb") as f:
            async for message in ws:
                if isinstance(message, bytes):
                    f.write(message)                    # play or save as it arrives
                else:
                    m = json.loads(message)
                    print(m)                            # start, then done
                    if m["type"] in ("done", "error"):
                        break

asyncio.run(main())
From a browser
Have your server mint a single-use ticket (60 seconds) with
POST
https://api.audiclabs.com
/v1/tickets
and the body
{"service": "tts", "endpoint": "stream"}
, then connect with
?ticket=
and append the binary frames to a
MediaSource
buffer (or collect them into a
Blob
). Your API key never reaches the page.
In the console,
Text to Speech
streams every clip: playback starts after about a second.
Previous
Generate speech
Next
Voices, languages & health
