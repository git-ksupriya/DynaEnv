# DynaWrite
A spatial communication environment for live group discussions and brainstorming.

DynaWrite explores an alternative to the conventional chat interface: instead of
messages accumulating into a permanent chronological stream, conversations are
represented spatially and can evolve over time.

**Live Demo:** https://dynawrite.onrender.com/

**Repository:** https://github.com/git-ksupriya/DynaEnv

## What it does

- Multiple participants can communicate through a shared canvas.
- Messages from different browsers appear in real time.
- Messages are grouped based on semantic similarity/context.
- Messages gradually fade instead of remaining permanently visible.
- Participants can visually distinguish different users.
- Longer messages are contained within scrollable elements to avoid overlap.
- The system is designed to eventually support persistent/pinned context and
  AI-assisted conversation management.

## Why

Most digital conversations treat every message as equally persistent.

In real conversations, this isn't the case. Some things are temporary,
some become important, and some context needs to remain available long after
the original exchange.

DynaWrite is an experiment in whether a communication interface can reflect
this more naturally.

## Current Architecture

At a high level:

Browser
  ↓
WebSocket connection
  ↓
backend
  ↓
Message processing
  ↓
Semantic embedding / context grouping
  ↓
Shared conversation state

The current prototype uses embeddings to determine the contextual relationship
between messages. The backend also manages message expiry and communication
between connected clients.

## Running locally

### Requirements

- Python 3.x
- pip
- Node.js and npm

### Installation

```bash
git clone https://github.com/git-ksupriya/DynaEnv.git
cd DynaEnv

pip install -r requirements.txt

Terminal 1: 
uvicorn backend.main:app --reload

Terminal 2:
cd frontend
npm run dev
