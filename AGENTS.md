# AGENTS.md — Instructions for AI Coding Agents

## Mission
Build AnyDown as a secure, maintainable, responsive website for analyzing supported media URLs and downloading only content the user is authorized to access and save.

## Read First
Before coding, read:
1. `PROJECT_BRIEF.md`
2. `PRD.md`
3. `TECHNICAL_SPEC.md`
4. `TASK_BACKLOG.md`
5. `README.md`

If instructions conflict, prioritize security/legal requirements, then the technical specification, then the PRD, then implementation convenience. Ask for clarification before making a major product or architecture change.

## Non-Negotiable Rules
- Do not bypass DRM, paywalls, private-account controls, authentication, anti-bot systems, or platform rate limits.
- Do not collect or request passwords, session cookies, browser profiles, or platform tokens from users.
- Do not claim support for a platform/content type until the adapter is implemented, tested, and reviewed for policy compliance.
- Never fabricate format options or report a successful download before validating the output file.
- Prevent SSRF, path traversal, command injection, resource exhaustion, and unsafe redirects.
- Never place secrets in source code, logs, screenshots, tests, or documentation.
- Do not commit generated media, local environment files, cache folders, or downloaded user content.
- Use short-lived jobs/files and implement automatic cleanup.
- Preserve existing project conventions unless a documented reason requires a change.

## Coding Standards
- TypeScript: strict mode, typed API responses, avoid `any`, use accessible semantic HTML.
- Python: type hints, Pydantic request/response models, clear exception types, lintable code.
- Keep platform-specific logic in adapters; avoid large platform conditionals scattered through routes.
- Keep route handlers thin; business logic belongs in services.
- Use dependency injection for network clients, storage, queues, and adapters where practical.
- Use structured logs and stable public error codes.
- Make timeouts, size limits, concurrency, and retention configurable.
- Use argument arrays for subprocesses; never build shell commands from user input.
- Add tests with every behavior change.

## UI Requirements
- URL field with clear label and example placeholder.
- Analyze button with loading/disabled state.
- Results card with detected platform, permitted metadata, and actual formats.
- Format selector with media type, quality, container, and estimated size where available.
- Progress bar with accessible status text; use indeterminate progress if total size is unknown.
- Completed state with a clear Download file action and success message.
- Helpful error state with retry only where safe.
- Responsive layout, keyboard operation, visible focus, and reduced-motion support.

## API and Job Requirements
- Validate URL before any outbound request.
- Check host allowlist and every redirect.
- Use opaque IDs and enforce job/file access.
- Keep state transitions valid and progress monotonic.
- Validate final file type and size before exposing the file.
- Ensure cleanup happens on success, failure, cancellation, and expiry.

## Definition of Done
A task is done only when:
- Acceptance criteria are met.
- Tests are added/updated and pass, or failures are clearly reported.
- Security and policy implications have been considered.
- Documentation and `.env.example` remain accurate.
- No secrets or temporary user media are committed.
