# Voices, languages & health · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/tts-voices

Text to Speech · API
Voices, languages & health
Free lookups for building a voice picker and monitoring the service.
List voices
GET
https://api.audiclabs.com/v1/tts/voices
Every voice you can use, with its id, name, language and dialect. Free.
curl https://api.audiclabs.com/v1/tts/voices -H "Authorization: Bearer $AUDICLABS_API_KEY"
List languages
GET
https://api.audiclabs.com/v1/tts/languages
Every language code the model accepts in the
language
field, with its name. Free.
Health
GET
https://api.audiclabs.com/v1/tts/health
Service readiness, for monitoring. Free. Returns
200
with
"status": "ready"
when the model is loaded.
Previous
Generate speech (streaming)
Next
Guide
