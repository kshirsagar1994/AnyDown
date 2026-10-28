# AnyDown 🚀

AnyDown is a responsive, modern web application for analyzing supported media URLs and downloading available, authorized media in user-selected formats (MP4 video, MP3 audio, JPG/PNG image).

## Core Architecture
- **Frontend:** Next.js (App Router), React 19, TypeScript, Tailwind CSS, Lucide icons.
- **Backend:** FastAPI (Python 3.12+), Pydantic v2, SSE progress streaming.
- **Media Engine:** `yt-dlp` python integration and `FFmpeg` for permitted transcoding and container validation.
- **Security:** Strict SSRF prevention (DNS resolution check, private/loopback/link-local IP block), hostname allowlist, filename sanitization, container magic-number validation, and rate limiting.

## Supported Platforms (Permitted Public Content)
- **YouTube:** Videos (up to 4K when available) and Audio extraction (MP3)
- **Instagram:** Public Reels, Posts, and Videos
- **TikTok:** Public Videos and Audio
- **X (Twitter):** Public Videos and Images
- **Reddit:** Public Videos with synchronized audio and images
- **Pinterest:** Public Pins and Videos
- **Facebook:** Public Videos
- **Snapchat:** Public Spotlight/Story media
- **LinkedIn:** Public Video and Image posts
- **Discord & Quora:** Publicly shared direct CDN media and answers

## Project Structure
```text
AnyDown/
├── frontend/             # Next.js App Router application
├── backend/              # FastAPI REST API & worker services
├── docs/                 # Architecture, security, and compliance documentation
├── .env.example          # Environment configuration template
├── PROJECT_BRIEF.md      # Project overview and requirements
├── PRD.md                # Product Requirements Document
├── TECHNICAL_SPEC.md     # Technical Specification & API Contract
├── TASK_BACKLOG.md       # Implementation tasks and milestones
└── README.md             # This file
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- FFmpeg installed and available on system PATH

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to use AnyDown.
