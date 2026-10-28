# AnyDown — Project Brief

## 1. Project Overview
**Project name:** AnyDown  
**Project type:** Responsive web application  
**Purpose:** Let users paste a public content URL, analyze the media that is lawfully accessible, choose an available format/quality, and download the selected file with clear progress and completion feedback.

AnyDown is a media-link analysis and download interface intended for content users are authorized to download. Platform support depends on each platform's terms, technical access, and available official APIs. The product must not bypass authentication, paywalls, DRM, private-content controls, rate limits, or anti-bot protections.

## 2. Problem Statement
Users often need a simple workflow to identify available media formats and download content they own, have permission to use, or that a platform explicitly makes downloadable. The experience should be clear on desktop and mobile, show real available formats rather than invented options, and provide reliable progress/error states.

## 3. Core User Journey
1. User opens AnyDown.
2. User pastes a supported post, reel, video, story, pin, or profile URL into the URL field.
3. User selects **Analyze**.
4. The backend validates the URL and checks whether the platform and content type are supported.
5. AnyDown displays only the formats that are actually available and permitted, such as MP4 video qualities, MP3 audio, or JPG/PNG images.
6. User chooses a format/quality and selects **Download**.
7. AnyDown shows progress, then a success message and a working file download.
8. If analysis or download fails, the UI explains the reason and offers a safe retry where appropriate.

## 4. Initial Platform Scope
Potential platform adapters, subject to lawful access and platform terms:
- **YouTube:** video qualities such as 360p, 720p, 1080p, 2K, and 4K when genuinely available; audio export such as MP3 when permitted.
- **Snapchat, Instagram, Facebook, LinkedIn, X, TikTok, Pinterest, Reddit, Threads, Discord, and Quora:** public or user-authorized media only, where supported and permitted.
- Profile pictures, images, video posts, and story content should be treated as separate capabilities. Do not promise a capability until it has been tested against official API/platform rules.

### Platform Capability Overview

| Platform | Features Supported (Subject to Review) | Target Output Formats |
| :--- | :--- | :--- |
| **YouTube** | Video (360p, 720p, 1080p, 2K, 4K), Audio | MP4, MP3 |
| **Snapchat** | Public Spotlight/Stories (Videos & Images) | MP4, JPG |
| **Instagram** | Public Posts & Reels (Videos, Audio, Images) | MP4, MP3, JPG |
| **Facebook** | Public Videos & Posts | MP4, MP3, JPG |
| **LinkedIn** | Public Video Posts & Images | MP4, JPG |
| **X (Twitter)** | Public Video Posts & Images | MP4, MP3, JPG |
| **TikTok** | Public Videos & Sounds | MP4, MP3 |
| **Pinterest** | Public Pins (Images & Videos) | MP4, JPG |
| **Reddit** | Public Video Posts & Images | MP4, MP3, JPG |
| **Threads** | Public Posts & Media | MP4, JPG |
| **Discord** | Public CDN attachment URLs | MP4, MP3, JPG |
| **Quora** | Public Shared Answers Media | MP4, JPG |

## 5. Product Principles
- **Truthful format availability:** never show quality options that are not available.
- **User safety and rights:** users must have rights or permission to download the media.
- **Privacy:** do not store pasted URLs or media longer than needed; avoid logging tokens or private content.
- **Security:** validate URLs, block SSRF and private-network targets, and constrain downloads.
- **Accessibility:** keyboard support, visible focus, semantic controls, readable progress announcements.
- **Reliability:** clear loading, empty, unsupported, failure, cancellation, and completion states.
- **Mobile-first responsive UI.**

## 6. MVP Scope
- Landing page with URL input and Analyze button.
- URL/platform validation with strict SSRF protection.
- Platform capability registry and adapter interface.
- Analysis results with thumbnail/metadata where allowed.
- Available-format selection (strictly actual available streams).
- Download job and real-time progress indicator (SSE stream with fallback).
- MP4 video, MP3 audio, and JPG/PNG image output where supported.
- Download completion state and error handling.
- Terms of Service, Privacy Policy, Copyright/Abuse contact, and usage notice.
- Automated tests and deployment documentation.

## 7. Out of Scope for MVP
- Bypassing DRM, private accounts, login restrictions, paywalls, or anti-bot systems.
- Bulk scraping, account credential collection, or user session-cookie collection.
- Guaranteeing support for every platform or every content type.
- Permanent hosting of user-downloaded media.
- Mobile apps, browser extensions, and paid subscriptions unless later approved.

## 8. Success Metrics
- Analysis success rate for supported URLs.
- Median time from Analyze to available formats (< 2.5 seconds).
- Download completion rate.
- Percentage of jobs with clear and actionable errors.
- Crash/error rate and service availability.
- Privacy/security incidents: target zero.

## 9. Key Risks and Dependencies
- Platform terms and API restrictions can change.
- Some platforms do not provide public story/media download APIs.
- High-resolution video may require separate video/audio streams and server-side merging via FFmpeg.
- Serverless hosts may not support long-running downloads, FFmpeg, or large temporary files.
- Copyright, privacy, and data-protection obligations must be reviewed before launch.

## 10. Definition of Done
The MVP is ready when supported test URLs produce accurate available formats, downloads return the correct file extension and MIME type, progress/error states work, security tests pass, policy pages are published, and platform-specific permissions have been reviewed.
