# Diarization models & health · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/diarization-models

Speaker Diarization · API
Models & health
Free lookups for checking the model and monitoring the service.
List models
GET
https://api.audiclabs.com/v1/diarization/models
curl https://api.audiclabs.com/v1/diarization/models -H "Authorization: Bearer $AUDICLABS_API_KEY"
Health
GET
https://api.audiclabs.com/v1/diarization/health
Service readiness, for monitoring. Free. Returns
200
with
"status": "ready"
, the current queue depth and throughput, or
503
while the model is loading.
Previous
Diarize audio
Next
Authentication
