# Architecture · AudicLabs

Source URL: https://docs.audiclabs.com/docs/architecture

AudicLabs · production system
One studio, one gateway, every API.
AudicLabs is the customer-facing studio. Middleware is the governed front door for published APIs, handling identity, metering, permissions, documentation and upstream health while studio tools such as the Noise Suppressor keep their own product experience.
User / customer
Browser, SDK or API client
HTTPS
AudicLabs Studio
Next.js app + auth
workspace / API keys
API Explorer / product UI
console.audiclabs.com
Noise Suppressor
Audic noise suppression models
studio tool, via the gateway
Middleware gateway
tokens · scopes · quotas
credits · logs · health
api.audiclabs.com
Data services
Cloud SQL Postgres
Registered
upstreams
Noise
suppressor
TTS · STT · Diar (GPU)
Future APIs
studio tool
catalog route
metered proxy
health
01 / request flows
How traffic travels
Studio tools
Noise Suppressor, Text to Speech, Speech to Text and Speaker Diarization: the studio validates the user session and sends each request through the Middleware gateway with the workspace token, so every call is authenticated, metered and logged like a customer call. TTS, STT and diarization run on the GPU cluster, reached by the gateway over a private WireGuard link.
Accounts and data
Accounts, workspaces and keys live in Cloud SQL Postgres, reached from the app server over TLS with the instance CA pinned.
New catalog service
Register an upstream and endpoint in Middleware; the live catalog makes it appear in the API Explorer without a frontend deployment.
02 / adding services
What changes when an API is added
Adding a service is a Middleware configuration change. The service becomes visible to AudicLabs when it is active, has enabled endpoints, and the workspace token or plan has the matching scope.
1.
Register the upstream base URL, authentication and health path.
2.
Add endpoint schemas, content types, pricing and scopes.
3.
Grant the workspace token or plan access.
4.
Middleware probes the service and publishes the catalog.
5.
AudicLabs fetches the catalog and renders the endpoint form automatically.
A dedicated branded workflow still requires a AudicLabs code integration. Arbitrary registered services are immediately available through the API Explorer.
03 / operations
Status and health monitoring
The public status page probes the studio, the database, the Middleware gateway, the Noise Suppressor, and Text to Speech, Speech to Text and Speaker Diarization on the GPU host. Middleware independently probes every active registered upstream.
Public status
The public page reports Middleware health as an aggregate such as “2/2 upstreams up”. Machine monitoring is available at
/api/status
.
Individual service detail
The Middleware admin console shows each service row, health state and manual probe at
api.audiclabs.com
/admin
.
04 / verified links
Production surfaces
AudicLabs
Studio
·
Docs
·
Status
·
Status JSON
Middleware
Gateway
·
Admin
·
Docs
·
Health
·
OpenAPI
Source
GitHub repository
·
v2_integration branch
Staging
No separate staging hostname is configured or verified in the current deployment, so no staging URL is shown here.
Previous
Rate limits & quotas
