# Remove noise (bulk) · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/denoise-batch

Noise Suppressor · API
Remove noise (bulk)
Clean up to 25 files in one request and get them back as a ZIP.
POST
https://api.audiclabs.com/v1/noise-suppressor/denoise/batch
Request
Send
multipart/form-data
and repeat the
files
field once per file. Everything else is handled for you. 1 credit per call; up to 200 MB per request. Needs the
noise-suppressor:denoise-batch
scope.
files
file, repeated
required
1 to 25 audio or video files, up to 100 MB each.
model
string
optional
Optional, applied to every file. One of
audic-1
to
audic-5
, see
Models
. Leave it out to use Audic 2.
Example
curl -OJ https://api.audiclabs.com/v1/noise-suppressor/denoise/batch \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -F files=@call-1.wav \
  -F files=@call-2.mp3 \
  -F files=@interview.m4a
Response
audiclabs.ns.batch.zip
holds every cleaned file plus
manifest.json
. Each file is named
audiclabs.ns.<file name>.wav
; a repeated name gets a number (
audiclabs.ns.call.1.wav
) so nothing is overwritten.
{
  "model": "audic-2",
  "files": 3,
  "succeeded": 3,
  "failed": 0,
  "processing_s": 7.9,
  "items": [
    {
      "index": 0,
      "input": "call-1.wav",
      "status": "ok",
      "output": "audiclabs.ns.call-1.wav",
      "bytes": 312364,
      "stats": { "duration_s": 9.77, "processing_s": 2.61, "rtf": 0.27 }
    }
  ]
}
One bad file never fails the batch: it is listed in the manifest with
"status": "error"
and its message, and the rest are processed. The
X-NS-Batch
header summarises files, succeeded, failed and processing time.
More than 25 files returns
413
. See
Errors
for the full list.
Previous
Remove noise
Next
Remove noise (streaming)
