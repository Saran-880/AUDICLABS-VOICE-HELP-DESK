# List models · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/models

Noise Suppressor · API
List models
Every Audic model with its sample rate, description and whether it is installed.
GET
https://api.audiclabs.com/v1/noise-suppressor/models
Free to call.
Example
curl https://api.audiclabs.com/v1/noise-suppressor/models \
  -H "Authorization: Bearer $AUDICLABS_API_KEY"
Response
{
  "models": [
    {
      "id": "audic-2",
      "label": "Audic 2 · Balanced",
      "sample_rate": 16000,
      "description": "Balanced quality and speed. Recommended default.",
      "available": true,
      "size_mb": 10.2
    }
  ],
  "default": "audic-2"
}
See
Models
for guidance on choosing one.
Previous
Remove noise (streaming)
Next
Sample clip
