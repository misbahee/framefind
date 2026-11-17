# FrameFind — Project Overview

**Project:** FrameFind  
**Stage:** Stage 1 — MVP  
**Status:** Backend substantially implemented; frontend not started.

## 1. Product Summary

FrameFind is an event-based photo discovery platform that allows event participants to find photographs containing their faces using a selfie.

Event organizers upload event photographs through FrameFind. The original photographs are stored in the organizer's Google Drive. Participants join events through invitation links and search for their photographs by uploading a selfie.

FrameFind uses face detection and facial embeddings to identify matching photographs.

## 2. Problem Statement

Finding individual photographs among hundreds or thousands of event photographs can be difficult and time-consuming.

Participants often have to manually browse large photo collections to find photographs of themselves.

FrameFind aims to simplify this process by allowing participants to search for their photographs using facial recognition.

## 3. Target Users

### Event Organizers

Users responsible for creating events and uploading photographs.

They can:
- Create events.
- Upload event photographs.
- Initiate face processing.
- Monitor photo-processing status.
- Share event invitation links.

### Event Participants

Users who attend an event and want to find photographs containing their faces.

They can:
- Join events through invitation links.
- Upload a selfie.
- Search for matching photographs.
- View matching event photographs.

A user can be both an event organizer and a participant in different events.

## 4. Core Product Workflow

1. User signs in using Google.
2. FrameFind creates the required Google Drive folders.
3. Organizer creates an event.
4. Organizer uploads event photographs.
5. Organizer manually initiates photo scanning.
6. Background workers detect faces and generate facial embeddings.
7. Participants join through reusable invitation links.
8. Participants upload a selfie.
9. FrameFind searches for matching facial embeddings within the selected event.
10. Participants view matching photographs through FrameFind.

## 5. Core Product Principles

- Original event photographs remain in the organizer's Google Drive.
- PostgreSQL stores application metadata and facial embeddings.
- pgvector is used for vector similarity search.
- Selfies are temporary search inputs and are not permanently stored.
- Google OAuth credentials remain on the backend.
- Participants can only access events they own or have joined.
- Original photographs are delivered through authorized backend endpoints.
- Each detected face receives an individual embedding.

## 6. MVP Scope

The first release focuses on:

- Google authentication.
- Event creation and listing.
- Google Drive integration.
- Event photo uploads.
- Background face processing.
- Facial embedding storage.
- Event invitations and membership.
- Selfie-based photo search.
- Authorized photograph viewing.
- Event and photo management.

## 7. Out of Scope

The following are excluded from Stage 1:

- Participant My Gallery.
- Saving photographs to participants' Google Drive.
- Multiple event administrators.
- Participant approval and management.
- Public event discovery.
- Social features.
- Photographer-specific accounts.
- Advanced event editing.
- Bulk photo downloads.
- Similarity scores displayed to participants.
- Kafka, Kubernetes, microservices and GPU infrastructure.

## 8. Technology Overview

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | FastAPI |
| Database | PostgreSQL |
| Vector Search | pgvector |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | Google OAuth, JWT HttpOnly cookie |
| Photo Storage | Google Drive |
| Background Processing | Celery |
| Message Broker | Redis |
| Face Detection | InsightFace SCRFD |
| Face Embeddings | ArcFace |
| Package Management | uv |

## 9. Project Objective

Deliver a working end-to-end application that allows event organizers to upload photographs and participants to discover photographs containing their faces through selfie-based facial recognition.