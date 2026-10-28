# AnyDown — Technical Specification

## 1. Architecture
Recommended architecture:
- **Frontend:** Next.js App Router, React, TypeScript, Tailwind CSS.
- **API:** FastAPI, Python 3.12+, Pydantic v2.
- **Queue/cache:** Redis with in-memory fallback for local development/single-instance worker coordination.
- **Workers:** asynchronous worker processes or async background tasks for analysis, downloading, and conversion.
- **Media tools:** `yt-dlp` python engine & `FFmpeg` for permitted format conversion and audio/video stream merging.
- **Storage:** short-lived temporary storage with strict lifecycle deletion and path sanitization.
- **Progress:** Server-Sent Events (SSE) for job progress with fallback polling.
- **Deployment:** frontend and API decoupled or unified reverse-proxy; worker-capable host for media jobs.

## 2. High-Level Flow
1. Browser sends URL to `POST /api/v1/analyze`.
2. API validates syntax, scheme, hostname, redirects, and adapter capability (blocking SSRF and private ranges).
3. API creates an analysis job and fetches metadata/formats using an approved method.
4. API returns metadata and actual available formats.
5. Browser submits selected `format_id` to create a download job `POST /api/v1/downloads`.
6. Worker obtains permitted media, optionally converts/merges it via FFmpeg, validates output MIME, and updates progress.
7. Browser listens to SSE (`GET /api/v1/downloads/{job_id}/events`) or polls job status.
8. Browser receives a short-lived download endpoint when complete.
9. Worker/storage cleanup removes temporary files after a defined retention period.

## 3. Repository Layout
```text
anydown/
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   ├── terms/page.tsx
│   │   ├── privacy/page.tsx
│   │   ├── copyright/page.tsx
│   │   └── platforms/page.tsx
│   ├── components/
│   │   ├── UrlBar.tsx
│   │   ├── ResultsCard.tsx
│   │   ├── FormatSelector.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── StatusBanner.tsx
│   │   └── PlatformMatrix.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── types/
│   │   └── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.ts
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py
│   │   │   ├── downloads.py
│   │   │   ├── platforms.py
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   ├── downloads.py
│   │   │   └── platform.py
│   │   ├── services/
│   │   │   ├── adapters/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── mock.py
│   │   │   │   ├── youtube.py
│   │   │   │   ├── instagram.py
│   │   │   │   ├── tiktok.py
│   │   │   │   ├── twitter.py
│   │   │   │   ├── reddit.py
│   │   │   │   ├── pinterest.py
│   │   │   │   ├── facebook.py
│   │   │   │   ├── discord.py
│   │   │   │   └── generic.py
│   │   │   ├── analysis_service.py
│   │   │   ├── download_service.py
│   │   │   ├── conversion_service.py
│   │   │   └── storage_service.py
│   │   └── main.py
│   └── tests/
│       ├── test_security.py
│       ├── test_url_validation.py
│       ├── test_adapters.py
│       ├── test_download_pipeline.py
│       └── test_api_routes.py
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── AGENTS.md
├── PROJECT_BRIEF.md
├── PRD.md
├── TECHNICAL_SPEC.md
├── TASK_BACKLOG.md
└── README.md
```

## 4. API Contract

### `POST /api/v1/analyze`
Request:
```json
{ "url": "https://example.com/public-media/123" }
```
Response:
```json
{
  "analysis_id": "opaque-id",
  "platform": "youtube",
  "content_type": "video",
  "metadata": {
    "title": "Example title",
    "creator": "Example creator",
    "thumbnail_url": "https://...",
    "duration_seconds": 120
  },
  "formats": [
    {
      "format_id": "format-720",
      "media_type": "video",
      "container": "mp4",
      "quality_label": "720p",
      "width": 1280,
      "height": 720,
      "estimated_size_bytes": 14500000,
      "requires_conversion": false
    }
  ],
  "warnings": []
}
```

### `POST /api/v1/downloads`
Request:
```json
{
  "analysis_id": "opaque-id",
  "format_id": "format-720"
}
```
Response:
```json
{
  "job_id": "opaque-job-id",
  "status": "queued",
  "events_url": "/api/v1/downloads/opaque-job-id/events"
}
```

### `GET /api/v1/downloads/{job_id}/events`
SSE events:
```text
event: progress
data: {"status":"downloading","percent":35,"message":"Downloading media stream"}

event: progress
data: {"status":"converting","percent":85,"message":"Finalizing MP4 container"}

event: completed
data: {"status":"completed","download_url":"/api/v1/downloads/opaque-job-id/file","filename":"example_title.mp4","file_size":14500000}
```

### `GET /api/v1/downloads/{job_id}/file`
- Streams finalized file with `Content-Disposition: attachment; filename="..."` and proper MIME (`video/mp4`, `audio/mpeg`, `image/jpeg`).

### `Supporting endpoints`
- `GET /api/v1/health`
- `GET /api/v1/platforms`
- `GET /api/v1/downloads/{job_id}`
- `DELETE /api/v1/downloads/{job_id}`

## 5. Security Requirements
- Strict hostname allowlist.
- SSRF prevention: resolve DNS, verify resolved IP does not belong to loopback, link-local, RFC 1918 private subnets, cloud metadata IPs (169.254.169.254), or IPv6 equivalents.
- Check redirects: each redirect target must also pass hostname and SSRF validation.
- Subprocess safety: call FFmpeg with argument lists `['ffmpeg', '-i', ...]`, never `shell=True`.
- Filename sanitization: remove path traversal characters (`..`, `/`, `\`), null bytes, shell metacharacters.
- File integrity: inspect output file magic numbers before serving (ensure MP4 starts with `ftyp`, MP3 has ID3/sync frame, JPG has SOI `\xFF\xD8`, PNG has `\x89PNG`).
- Strict rate limiting: configurable per IP.
