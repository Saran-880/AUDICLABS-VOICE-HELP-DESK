# Speaker Diarization · AudicLabs

Source URL: https://docs.audiclabs.com/docs/speaker-diarization

Speaker Diarization
Speaker Diarization
Find who spoke when. The
audic-diar-1
model splits a conversation into speaker turns, up to 8 speakers, in recordings of any length, and labels speakers
speaker_1
,
speaker_2
, … in order of first appearance. Use it in the console or call it from code; both run on the AudicLabs GPU cluster.
In the console
Open
Speaker Diarization
, upload a file or record from your microphone, and press
Find speakers
. You get a timeline with one lane per speaker, each speaker's share of the talk time and the full segment list; click any segment to play it. Download the result as JSON, RTTM or CSV. Each file costs 1 credit.
Settings
Setting
API field
What it does
Join short pauses
merge_gap
Joins a speaker's consecutive segments separated by a pause up to this many seconds, when nobody else spoke in between. The API default is 0 (segments exactly as detected); the console uses 0.5 s.
Sensitivity
threshold
How sure the model must be that someone is speaking, 0.05 to 0.95. Lower finds quieter speech, higher keeps only confident speech. Default 0.5.
Reading the results
Speaker labels are consistent within one recording:
speaker_2
is the same voice wherever it appears in that file. They are not identities and do not carry across recordings. When two people talk at once, both get a segment for the overlap.
Inputs: WAV, MP3, M4A/AAC, FLAC, OGG/Opus, WebM, AMR and the audio track of common video files, up to 200 MB and 4 hours. Diarize first, then send each segment to
Speech to Text
to build a speaker-labelled transcript.
API reference
Diarize audio
POST /diarize · audio in, speaker segments out.
Models & health
GET /models and /health.
Previous
Models, languages & health
Next
Diarize audio
