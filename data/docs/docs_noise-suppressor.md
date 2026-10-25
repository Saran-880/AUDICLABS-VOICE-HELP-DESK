# Noise Suppressor · AudicLabs

Source URL: https://docs.audiclabs.com/docs/noise-suppressor

Noise Suppressor
Noise Suppressor
Remove background noise from speech: street, fans, keyboards, crowds. Clean whole files (standalone) or live audio as it happens (streaming), in the console or from code; every path runs the same Audic models.
Two modes
Mode
Use it for
API
Standalone
Audio you already have: a file, a recording, a batch of files. You send the whole file and get the whole cleaned file back.
POST /denoise
Streaming
Live audio: calls, meetings, a microphone. You send small frames as they are captured and hear them cleaned a fraction of a second later.
WS /stream
In the console
Open
Noise Suppressor
and pick a mode at the top.
Standalone
Upload a file, record from your microphone (a live waveform shows your input) or load the built-in sample. Pick a model, set the noise reduction limit and format, and press
Remove noise
. The original and cleaned audio play side by side.
Streaming
Choose
Microphone
or
File
(a file is played in real time, as if it were live), pick a model and press
Start streaming
. Level meters show the original and the cleaned signal as they flow, with the delay and real-time factor. Under
Listen to
, switch between the original and the cleaned audio while it runs; use headphones with a microphone. Press
Stop
to get both recordings to replay and download. You can also
open Streaming directly
.
History
Every run, file or streaming session, is saved to your history with its settings and stats, including failed runs. Expand a run to replay or download the original and the cleaned audio, or delete it. History is private to your account.
Settings
Setting
What it does
Model
Which Audic model runs, Audic 1 to Audic 5. Audic 2 by default. See Models.
Noise reduction limit
How much noise to remove. The default removes as much as possible; a lower limit keeps more room tone.
Output format
WAV (default) or FLAC.
Standalone results are named after your file:
meeting.m4a
comes back as
audiclabs.ns.meeting.wav
, at the sample rate you uploaded. Streaming returns audio at the model's rate (16 kHz, or 48 kHz for Audic 5).
Inputs: WAV, FLAC and OGG natively; MP3, M4A, WebM, Opus and most other formats are converted on the server. Up to 100 MB per file.
API reference
Remove noise
POST /denoise · clean one file.
Remove noise (bulk)
POST /denoise/batch · up to 25 files, returns a ZIP.
Remove noise (streaming)
WS /stream · live audio in, cleaned audio out, in real time.
List models
GET /models · ids, rates and availability.
Health
GET /health · status for monitoring.
Previous
APIs
Next
Remove noise
