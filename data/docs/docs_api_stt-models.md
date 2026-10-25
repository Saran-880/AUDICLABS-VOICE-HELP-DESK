# Models, languages & health · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/stt-models

Speech to Text · API
Models, languages & health
Free lookups for building a language picker and monitoring the service.
List models
GET
https://api.audiclabs.com/v1/stt/models
curl https://api.audiclabs.com/v1/stt/models -H "Authorization: Bearer $AUDICLABS_API_KEY"
List languages
GET
https://api.audiclabs.com/v1/stt/languages
Every language code with its name and support tier:
ready
,
broad
or
adaptation
.
auto
detects the language.
{
  "object": "list",
  "data": [
    { "code": "auto", "name": "Automatic detection", "tier": "auto" },
    { "code": "en-US", "name": "English (United States)", "tier": "ready", "enabled": true },
    { "code": "ar-AR", "name": "Arabic", "tier": "ready", "enabled": true },
    { "code": "hi-IN", "name": "Hindi", "tier": "ready", "enabled": true }
  ]
}
Health
GET
https://api.audiclabs.com/v1/stt/health
Service readiness, for monitoring. Free. Returns
200
with
"status": "ready"
, active sessions and the language count.
Previous
Transcribe live (streaming)
Next
Guide
