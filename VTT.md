# VTT (Voice-to-Text) Project

## Background
Natural, hands-free conversation with OpenClaw is vital for flexible workflow, background interviews, and multimodal tasking. Voice-to-text (VTT) will enable user to interact with projects, capture logs, and drive workflows by spoken word.

## Scope & Goals
- Web-app-based UI, using desktop mic with push-to-talk
- Real-time transcription pipeline (Whisper CLI or API)
- Only project Q&A or explicit context is logged
- Temp audio file retention (30 days, auto-delete)
- English language support
- Minimal UI: live transcription feedback, simple review
- Expansion/future-proofing for mobile, TTS, etc.

## Phases
1. Requirements & UX: Confirm and capture specs, assign agents
2. Prototype UI & pipeline: dev-worker-claude + vision-worker
3. Transcript/project log: BOB manages filtering/final logging
4. Testing, cleanup automation, doc/demo

## Metadata
- Session: session:vtt
- Project file: VTT.md (synced with CW)
- Owner: BOB
- Start date: 2026-02-20

## Current Tasks
- [ ] Phase 1: Wireframe, API/flow planning (dev-worker-claude, vision-worker)
- [ ] Phase 2: Build/prototype
- [ ] Phase 3: Interview runtime and logging
