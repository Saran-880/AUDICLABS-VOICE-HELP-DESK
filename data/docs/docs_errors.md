# Errors · AudicLabs

Source URL: https://docs.audiclabs.com/docs/errors

Platform
Errors
Gateway errors share one JSON shape, so your code can branch on
error.type
.
{
  "error": {
    "type": "scope_denied",
    "message": "This token is not scoped for 'noise-suppressor:denoise'.",
    "request_id": "req_01J7Z..."
  }
}
Every response, success or error, carries
X-Request-Id
. Include it when you contact support.
Error types
Type
Status
What happened
missing_token
401
No Authorization or X-API-Key header.
invalid_token
401
The token is not recognised. Check for truncation or an old copy.
invalid_ticket
401
A WebSocket ticket that is unknown, expired, already used or for another endpoint. Ask for a new one.
key_revoked / key_expired
401
The token was revoked or has expired. Create a new one.
ip_not_allowed
403
The token is restricted to other IP addresses.
scope_denied
403
The token is valid but not scoped for this endpoint.
plan_forbids_service
403
Your plan does not include this service.
service_not_found / endpoint_not_found
404
Check the URL: /v1/{service}/{endpoint}.
quota_exhausted
402
The workspace has used its monthly credits.
payload_too_large
413
The upload is larger than the endpoint allows.
rate_limited
429
Too many requests. Wait for the Retry-After header, then retry.
upstream_unavailable / upstream_timeout
502 / 504
The model service is restarting or slow. Retry with backoff.
circuit_open
503
The service is failing repeatedly and is paused briefly. Retry after a short wait.
WebSocket sessions
A WebSocket cannot carry an HTTP status, so a refused or failed session receives the same error body as one JSON message,
{"type": "error", "error": {...}}
, and then closes with code 4000 plus the status above:
4401
,
4403
,
4429
and so on. See
streaming errors
.
Model errors
Problems with the request itself, such as an unknown
model
or an unreadable file, come from the model service as
400
or
422
with a
detail
message:
{ "detail": "Unknown model 'audic-9'. Use an id from GET /models." }
Retrying
Retry
429
,
502
,
503
and
504
with exponential backoff. Do not retry
4xx
errors other than
429
; fix the request instead.
Previous
Authentication
Next
Rate limits & quotas
