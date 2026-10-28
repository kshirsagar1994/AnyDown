# AnyDown — Task Backlog

## Priorities
- **P0:** Required for a safe MVP.
- **P1:** Important after core flow.
- **P2:** Later enhancement.
- **Blocked:** Requires platform policy/API review or external approval.

## Phase 0 — Project Setup
- [x] **P0** Create monorepo folders for frontend, backend, docs, and tests.
- [x] **P0** Add `.gitignore`, `.env.example`, dependency manifests, and formatting/lint configuration.
- [x] **P0** Add local development instructions and health checks.
- [x] **P0** Configure Docker and container orchestration (`docker-compose.yml`, Dockerfiles).
- [x] **P0** Create threat model and platform-policy review checklist.

## Phase 1 — Frontend MVP
- [x] **P0** Build responsive AnyDown landing page with modern Tailwind CSS styling.
- [x] **P0** Add URL input, instant client platform detection, clipboard paste, and Analyze action.
- [x] **P0** Implement all 11 UX states: idle, validating, analyzing, complete, no-format, format selected, preparing, downloading, completed, failed, cancelled.
- [x] **P0** Build media metadata/results card (thumbnail, duration, author, platform badge, source link).
- [x] **P0** Build format selector using API-returned formats only (video MP4, audio MP3, image JPG).
- [x] **P0** Add accessible animated progress bar and live status message via Server-Sent Events.
- [x] **P0** Add completed auto-download trigger, direct manual download button, failed retry, and cancellation states.
- [x] **P1** Add platform capability matrix page (`/platforms`), terms (`/terms`), privacy (`/privacy`), and DMCA takedown (`/copyright`).

## Phase 2 — Backend Foundation
- [x] **P0** Create FastAPI app with versioned `/api/v1` routes.
- [x] **P0** Add typed Pydantic v2 schemas for analysis, formats, jobs, platform capabilities, and errors.
- [x] **P0** Implement hostname allowlist and safe URL validation.
- [x] **P0** Prevent SSRF, unsafe redirects, internal IP access (RFC 1918, loopback, link-local, cloud metadata), and DNS rebinding.
- [x] **P0** Add structured logging with secret and query redaction.
- [x] **P0** Add rate limits, request timeouts, and input-size limits.
- [x] **P0** Add health/readiness endpoints (`/api/v1/health`).
- [x] **P0** Add API tests for invalid and unsupported URLs.

## Phase 3 — Jobs and Progress
- [x] **P0** Define job state machine (`queued -> downloading -> converting -> completed | failed | cancelled`).
- [x] **P0** Implement in-memory job coordination store with thread-safe queue.
- [x] **P0** Implement analysis job lifecycle and session cache.
- [x] **P0** Implement download job lifecycle and cancellation.
- [x] **P0** Implement SSE progress streaming endpoint (`/api/v1/downloads/{job_id}/events`) with heartbeat pings and immediate state replay.
- [x] **P0** Add timeouts, file-size limits, and cleanup.

## Phase 4 — File Handling
- [x] **P0** Create safe temporary storage service with path traversal defenses.
- [x] **P0** Sanitize filenames and enforce correct MIME types.
- [x] **P0** Validate file magic numbers before delivery (`ftyp` for MP4, `ID3` for MP3, `\xFF\xD8\xFF` for JPG, `\x89PNG` for PNG).
- [x] **P0** Implement secure file endpoint (`/api/v1/downloads/{job_id}/file`) with attachment disposition.
- [x] **P0** Ensure automated 15-minute lifecycle cleanup of expired storage.
- [x] **P0** Add tests for MP4, MP3, JPEG, and PNG output validation.

## Phase 5 — Platform Adapters
- [x] **P0** Define common `BaseAdapter` interface and capability registry.
- [x] **P0** Implement `MockAdapter` for deterministic development/testing.
- [x] **P0** Implement `YouTubeAdapter` with truthful format extraction and audio conversion.
- [x] **P0** Implement `InstagramAdapter` for public reels and video posts.
- [x] **P0** Implement `TikTokAdapter` for public videos and audio tracks.
- [x] **P0** Implement `TwitterAdapter` for public X/Twitter videos and images.
- [x] **P0** Implement `RedditAdapter` with stream merging via FFmpeg.
- [x] **P0** Implement `PinterestAdapter` for public pins and videos.
- [x] **P0** Implement `FacebookAdapter` for public videos.
- [x] **P0** Implement `SnapchatAdapter` for public spotlight/stories.
- [x] **P0** Implement `GenericSocialAdapter` for Threads, LinkedIn, Discord attachments, and Quora.
- [x] **P0** Publish platform capability table that reflects only verified functionality.
- [x] **P0** Ensure unsupported/private/blocked content returns a clear stable error code.

## Phase 6 — Legal, Privacy, and Abuse Prevention
- [x] **P0** Draft Terms of Service and acceptable-use policy (`/terms`).
- [x] **P0** Draft Privacy Policy and retention/deletion policy (`/privacy`).
- [x] **P0** Add copyright/abuse contact and takedown workflow (`/copyright`).
- [x] **P0** Add user-facing notice requiring rights/permission to download.
- [x] **P0** Document supported platforms and known limitations.

## Phase 7 — Testing and Deployment
- [x] **P0** Unit tests for URL validation, adapter matching, state transitions, and file validation (16/16 passing).
- [x] **P0** Security tests for SSRF, redirects, path traversal, and resource limits.
- [x] **P0** Next.js 15 production build passing with 0 errors.
- [x] **P0** Add production health checks and Docker orchestration.
