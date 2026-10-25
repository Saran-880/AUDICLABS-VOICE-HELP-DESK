# Health · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/health

Noise Suppressor · API
Health
Service status, version and installed models. Free; use it for uptime monitoring.
GET
https://api.audiclabs.com/v1/noise-suppressor/health
curl https://api.audiclabs.com/v1/noise-suppressor/health \
  -H "Authorization: Bearer $AUDICLABS_API_KEY"
Response
{
  "status": "ok",
  "version": "1.0.0",
  "models_available": ["audic-1", "audic-2", "audic-3", "audic-4", "audic-5"],
  "loaded": ["audic-2"],
  "auth_required": true
}
For the whole platform, including the gateway and database, use the public
status page
or its JSON feed at
/api/status
.
Previous
Sample clip
Next
Guide
