# FrameFind — Development Status

**Project:** FrameFind  
**Stage:** Stage 1 — MVP  
**Last documented implementation state:** November 2026

## 1. Project Overview

The backend foundation has been substantially implemented using FastAPI.

The React frontend has been designed at a high level but has not yet been implemented.

The remaining work focuses on completing backend functionality, validating API contracts, implementing the frontend and integrating both systems.

## 2. Backend Implementation Status

### 2.1 Implemented

| Component | Functionality |
|---|---|
| Project setup | FastAPI application structure |
| Database | PostgreSQL integration |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | Google OAuth |
| Session management | JWT in HttpOnly cookie |
| User management | User creation and retrieval |
| Google Drive | Folder creation and photo uploads |
| Events | Event creation, listing and retrieval |
| Invitations | Invitation links and event joining |
| Photo upload | Single-file upload through FastAPI |
| Photo metadata | Store and retrieve photo records |
| Background processing | Celery + Redis |
| Face detection | InsightFace SCRFD |
| Embeddings | ArcFace, 512-dimensional vectors |
| Vector storage | PostgreSQL + pgvector |
| Scan initiation | Manual scanning with row-level locking |
| Task retries | Bounded Celery retry policy |
| Embedding persistence | Idempotent persistence |
| Selfie search | Event-scoped cosine similarity search |

### 2.2 Incomplete Backend Functionality

| Component | Remaining work |
|---|---|
| Photo viewing | Implement authorized photo streaming from Google Drive |
| Photo deletion | Implement Drive deletion and database cleanup |
| Event deletion | Implement owner authorization and complete cleanup |
| Event readiness | Transition event to READY after initial processing |
| CORS | Configure frontend/backend communication |
| OAuth callback | Redirect to the frontend |
| Drive authorization | Implement status checking and reconnection |
| Token refresh | Handle expired Google access tokens during API operations |
| Failed photo recovery | Provide a mechanism to retry failed processing |
| Stale task recovery | Detect abandoned PROCESSING records |
| CSRF | Protect state-changing cookie-authenticated requests |
| Upload validation | Add file size and content-type validation |
| API security | Remove drive_file_id from public responses |
| Logging | Replace debug print statements with proper logging |

### 2.3 Known Bugs

- Syntax error documented in `photo_search.py` involving a stray `,j` character.
- Event search is blocked because the event READY transition is missing.
- OAuth callback currently redirects to the backend Swagger documentation instead of the frontend.

These issues must be verified and corrected before end-to-end testing.

## 3. Frontend Implementation Status

**Technology:** React + Vite + JavaScript

**Status:** Not started.

### 3.1 Event Owner Experience

| Feature | Status |
|---|---|
| Landing page | Design pending |
| Google authentication UI | Design pending |
| Onboarding | Design pending |
| Owner dashboard | Design pending |
| Event listing | Design pending |
| Create event | Design pending |
| Event workspace | Design pending |
| Photo upload interface | Design pending |
| Processing status interface | Design pending |
| Invitation link interface | Design pending |

### 3.2 Participant Experience

| Feature | Status |
|---|---|
| Invitation preview | Design pending |
| Event joining | Design pending |
| Selfie upload | Design pending |
| Search interface | Design pending |
| Search results | Design pending |
| Photo viewer | Design pending |

### 3.3 Frontend Development Order

1. Landing page.
2. Authentication and onboarding.
3. Owner dashboard.
4. Create event.
5. Event workspace.
6. Participant invitation and joining.
7. Selfie search.
8. Search results and photo viewer.

The Event Owner Experience should be implemented before the Participant Experience.

## 4. Architecture and Documentation Status

| Deliverable | Status |
|---|---|
| Original PRD | Available |
| Frontend design decisions | Available |
| Project overview | To be finalized |
| Feature inventory | To be finalized |
| System architecture diagram | Pending |
| Database diagram | Pending |
| API contracts document | Pending |
| GitHub Issues | Pending |
| GitHub Project Board | Pending |

## 5. Immediate Engineering Priorities

The following work should be addressed before full frontend integration.

1. Verify and fix the selfie search syntax error.
2. Implement the event READY status transition.
3. Implement authorized photograph viewing.
4. Configure CORS and verify cookie-based authentication.
5. Correct the OAuth callback redirect.
6. Remove internal Google Drive identifiers from public responses.
7. Implement upload validation.
8. Address CSRF protection.
9. Implement safe photo and event deletion.

Drive reconnection, stale-task recovery and manual failed-photo recovery should also be evaluated and scheduled according to the agreed MVP requirements.

## 6. Definition of Done — Stage 1

Stage 1 is complete when:

- Users can authenticate using Google.
- Required Google Drive folders are created.
- Organizers can create events and upload photographs.
- Uploaded photographs can be processed in the background.
- Face embeddings are stored successfully.
- Events become searchable after initial scanning.
- Participants can join events through invitation links.
- Participants can search using a selfie.
- Search results contain matching photographs.
- Authorized users can view original photographs.
- Event and photo deletion work safely.
- The React frontend supports the complete user journey.
- Backend and frontend integration tests pass.
- Security and production-readiness requirements are addressed.

## 7. Guiding Development Principle

Implement one clearly defined task at a time.

Every task should have:

- A documented objective.
- Clear acceptance criteria.
- Relevant architecture and API references.
- Appropriate tests.
- Documentation updates where necessary.

New ideas discovered during development should be evaluated and added to the backlog rather than introduced randomly into the current implementation.