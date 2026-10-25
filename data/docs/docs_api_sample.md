# Sample clip · AudicLabs

Source URL: https://docs.audiclabs.com/docs/api/sample

Noise Suppressor · API
Sample clip
A short noisy 16 kHz speech recording (WAV, about 10 seconds) for trying the API.
GET
https://api.audiclabs.com/v1/noise-suppressor/sample
Free to call. Returns
audio/wav
.
curl https://api.audiclabs.com/v1/noise-suppressor/sample \
  -H "Authorization: Bearer $AUDICLABS_API_KEY" \
  -o sample.wav
Previous
List models
Next
Health
