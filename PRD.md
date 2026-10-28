# AnyDown — Product Requirements Document (PRD)

## 1. Purpose
Define product behavior and acceptance criteria for AnyDown, a responsive website that analyzes supported media URLs and offers lawful downloads in available formats.

## 2. Users and Use Cases
- A user wants to download a video they own or are authorized to save.
- A user wants an available audio export from permitted content.
- A user wants to save an image in its original or supported image format.
- A user wants to know which resolutions/formats are genuinely available before starting a download.

## 3. Functional Requirements

### FR-01: URL Input
- Provide a labeled URL input and an Analyze button.
- Accept only `https` URLs by default (or controlled `http` for local mock fixtures in test environments).
- Trim whitespace and reject malformed URLs.
- Display a helpful message for empty, malformed, unsupported, or disallowed URLs.
- Do not accept arbitrary local paths, IP literals, internal network addresses, or non-web protocols.

**Acceptance criteria**
- Empty input does not trigger a network request.
- Invalid URL displays an inline error.
- Keyboard users can submit the form and access errors.

### FR-02: Platform Detection
- Detect the platform from a maintained allowlist of hostnames.
- Normalize known short links only through safe, controlled redirects.
- Reject lookalike domains and unsupported hosts.
- Show the detected platform and supported capabilities.

**Acceptance criteria**
- `youtube.com`, `youtu.be`, and approved YouTube short-link hosts map to the YouTube adapter.
- A lookalike such as `youtube.example.invalid` is not treated as YouTube.
- Unknown platforms receive an unsupported-platform message.

### FR-03: Analysis
- Create an analysis job and return metadata only when legally and technically accessible.
- Show title, creator, thumbnail, duration, and media type only if available and permitted.
- Show a loading indicator and allow the user to cancel when practical.
- Never claim analysis succeeded if the adapter did not return valid results.

**Acceptance criteria**
- Loading, success, empty, unsupported, and failure states are represented.
- Analysis response contains a list of actual available formats, which may be empty.
- No quality options are fabricated.

### FR-04: Format and Quality Selection
- Display only formats returned by the platform adapter.
- Video examples: MP4 at 360p, 720p, 1080p, 1440p (2K), or 2160p (4K), only when available.
- Audio examples: MP3 export where allowed; optionally preserve original audio format if transcoding is unavailable.
- Images: JPG or PNG where supported. Convert to JPG only when the conversion is supported and appropriate.
- Clearly indicate estimated size when known and whether conversion is required.

**Acceptance criteria**
- User cannot select a format not in the analysis response.
- UI labels actual resolution and file type.
- Conversion failure does not produce a falsely labeled file.

### FR-05: Download Job
- Create a short-lived download job for a selected format.
- Return a job ID and status.
- Support progress updates using Server-Sent Events (SSE), WebSocket, or polling. Prefer SSE for a simple one-way progress stream.
- Allow cancellation where the worker and platform adapter support it.
- Set limits for duration, file size, concurrency, and temporary storage.

**Acceptance criteria**
- Progress is displayed as a percentage only when a reliable total is known; otherwise use an indeterminate progress indicator.
- Progress never shows 100% before the file is finalized.
- Job reaches `completed`, `failed`, or `cancelled`.
- Temporary files are deleted according to the retention policy.

### FR-06: File Delivery
- Return the correct MIME type and safe filename.
- Suggested mappings:
  - MP4: `video/mp4`
  - MP3: `audio/mpeg`
  - JPEG: `image/jpeg`
  - PNG: `image/png`
- Use a server-generated filename; sanitize titles and remove path separators/control characters.
- Send `Content-Disposition: attachment`.
- Do not expose filesystem paths or internal storage URLs.

**Acceptance criteria**
- Downloaded file opens in a compatible media viewer.
- Extension and MIME type match the actual file.
- File response uses authorization/job ownership checks if jobs are not public.

### FR-07: Errors and Feedback
- Provide user-safe messages for unsupported content, access denied, removed/private content, rate limiting, unavailable formats, timeout, conversion error, storage limit, and internal failure.
- Do not reveal stack traces, cookies, tokens, or internal service addresses.
- Provide Retry only for retryable failures.

### FR-08: Accessibility and Responsive Design
- Work on mobile, tablet, and desktop.
- Use semantic labels, keyboard navigation, visible focus, sufficient contrast, and screen-reader announcements for status/progress.
- Respect reduced-motion preferences.

### FR-09: Legal and Trust
- Publish Terms of Service, Privacy Policy, copyright/abuse contact, and acceptable-use guidance.
- Explain that users must have rights or permission to download content.
- Do not offer DRM, paywall, login, private-content, or anti-bot bypasses.
- Review each platform's current terms and official API rules before enabling an adapter.

## 4. Platform Capability Matrix (Initial, Not a Promise of Support)

| Platform | Candidate content | MVP requirement |
|---|---|---|
| YouTube | Videos/audio | Implement only a reviewed, permitted access path; show actual formats |
| Snapchat | Profile images, stories, posts | Enable only through permitted/public or authorized access |
| Instagram | Stories, posts, reels, images, video/audio | No private-account or login-control bypass |
| Facebook | Stories, posts, images, video/audio | Respect permissions and API restrictions |
| LinkedIn | Posts, images, video/audio | Respect member privacy and platform restrictions |
| X | Posts, images, video/audio | Use only permitted access methods |
| TikTok | Posts, stories where supported, images/video/audio | No access-control or anti-bot bypass |
| Pinterest | Pins, images, videos | Use permitted access and available formats |
| Reddit | Posts, images, videos/audio | Respect Reddit rules and content rights |
| Threads | Posts, images, video/audio | Enable only where access is permitted |
| Discord | Attachments in accessible channels | Do not access private channels or collect credentials |
| Quora | Posts/images/video/audio where available | Enable only if permitted and technically supported |

The word “stories” is not a universal platform content type. A platform adapter must declare its actual supported content types. Never advertise a feature until it is verified.

## 5. Non-Functional Requirements
- Security: SSRF prevention, strict host allowlist, MIME validation, size limits, safe process invocation.
- Performance: return an initial analysis response promptly (< 2.5 seconds); use asynchronous workers for long tasks.
- Availability: graceful degradation if an adapter or worker is down.
- Privacy: minimum retention and redacted logs.
- Maintainability: adapter-based platform integration and typed API contracts.
- Observability: structured logs, metrics, correlation IDs, and alerts without secrets.
- Cost control: per-IP/user rate limits, queue limits, worker concurrency limits, maximum file size and duration.

## 6. UX States
1. **Idle**: Empty state ready for input.
2. **Validating URL**: Client/server side format & platform verification.
3. **Analyzing**: Requesting metadata and available streams.
4. **Analysis Complete**: Displaying thumbnail, title, author, duration, and format grid.
5. **No Available Formats**: Content found but no downloadable media stream is lawful/available.
6. **Format Selected**: User has highlighted a target resolution/file container.
7. **Preparing Download**: Server queuing and initializing download/merge job.
8. **Downloading**: Active download with determinate percentage or indeterminate progress.
9. **Completed**: Working file download triggered with direct download fallback button.
10. **Failed**: Human-readable error message with safe retry option.
11. **Cancelled**: User manually stopped download or analysis.

## 7. MVP Release Criteria
- Core journey works end to end for each explicitly enabled adapter.
- Automated unit, integration, API, security, and UI tests pass.
- Legal and platform policy review is complete.
- Logs do not contain credentials or sensitive URLs.
- Deployment has configured timeouts, file limits, cleanup, and health checks.
