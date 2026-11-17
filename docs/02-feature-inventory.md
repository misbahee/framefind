# FrameFind — Feature Inventory

**Project:** FrameFind  
**Stage:** Stage 1 — MVP

## 1. Feature Classification

Features are classified into:

- **MVP:** Required for the first working release.
- **Future:** Important functionality planned for later development.
- **Optional:** Enhancements that are not essential.
- **Out of Scope:** Explicitly excluded from Stage 1.

## 2. MVP Features

### 2.1 Authentication and User Management

| Feature | Description | User |
|---|---|---|
| Google OAuth | Authenticate using Google | All users |
| User profile | Retrieve authenticated user information | All users |
| JWT authentication | Maintain application authentication using HttpOnly cookies | All users |
| Logout | Clear the authentication cookie | All users |
| Drive folder setup | Automatically create required FrameFind folders | All users |

### 2.2 Event Management

| Feature | Description | User |
|---|---|---|
| Create event | Create an event with name, date, location and description | Organizer |
| List events | Display owned and joined events | All users |
| Event details | Retrieve event information | All authorized users |
| Event ownership | Associate each event with one owner | System |

### 2.3 Photo Management

| Feature | Description | User |
|---|---|---|
| Upload photographs | Upload event photographs to organizer's Google Drive through FastAPI | Organizer |
| List photographs | Retrieve event photograph metadata | Authorized users |
| Photo processing status | Display PENDING, PROCESSING, COMPLETED and FAILED states | Organizer |
| Delete photograph | Remove photograph and associated application data | Organizer |
| View photograph | Retrieve original photograph through authorized backend streaming | Authorized users |

### 2.4 Face Processing

| Feature | Description | User |
|---|---|---|
| Initiate scanning | Manually start processing uploaded photographs | Organizer |
| Face detection | Detect individual faces in photographs | System |
| Embedding generation | Generate 512-dimensional ArcFace embeddings | System |
| Embedding persistence | Store embeddings in PostgreSQL using pgvector | System |
| Background processing | Process photographs using Celery workers | System |
| Retry handling | Retry failed processing tasks within configured limits | System |
| Event readiness | Make an event searchable after initial scanning finishes | System |

### 2.5 Invitations and Membership

| Feature | Description | User |
|---|---|---|
| Invitation generation | Generate a reusable event invitation link | Organizer |
| Invitation preview | Retrieve event information using an invitation token | Participant |
| Join event | Join an event through its invitation link | Participant |
| Membership validation | Prevent duplicate event memberships | System |

### 2.6 Selfie-Based Search

| Feature | Description | User |
|---|---|---|
| Selfie upload | Upload a selfie for searching | Participant |
| Face validation | Require exactly one face in the selfie | System |
| Embedding generation | Generate an embedding for the uploaded selfie | System |
| Similarity search | Search embeddings within the selected event | System |
| Result deduplication | Return each matching photograph only once | System |
| Search results | Display matching photographs | Participant |

## 3. Important Future Features

These features are not required for the initial MVP but may be considered later.

- Cursor-based pagination for search results.
- Vector index configuration based on measured workloads.
- Transactional outbox for reliable Celery task dispatch.
- Stale processing task detection and recovery.
- Manual recovery and retry interface for failed photographs.
- Improved Google Drive authorization status and reconnection.
- Advanced processing monitoring.
- Multiple event administrators.
- Participant management.

## 4. Optional Enhancements

- Advanced event analytics.
- Improved photo gallery interactions.
- Additional performance optimizations.
- More advanced search result navigation.

## 5. Out of Scope — Stage 1

- Participant My Gallery.
- Saving photographs into participants' Google Drive.
- Public event discovery.
- Global user search.
- Social feeds, likes, comments and messaging.
- Photographer-specific accounts.
- Participant approval and removal.
- Invitation revocation and regeneration.
- Multiple event administrators.
- Advanced event editing.
- Direct browser-to-Google-Drive uploads.
- Bulk photo downloads.
- Similarity scores displayed to users.
- Kafka, Kubernetes and microservices.
- GPU infrastructure.

## 6. Feature Dependencies

| Feature | Dependencies |
|---|---|
| Event creation | Authentication, Google Drive integration |
| Photo upload | Authentication, event ownership, Google Drive |
| Face processing | Photo upload, Celery, Redis, InsightFace |
| Event readiness | Completion tracking for photo processing |
| Invitation joining | Authentication, invitation token |
| Selfie search | Event membership, completed embeddings, face recognition |
| Photo viewing | Photo metadata, Google Drive credentials, event authorization |
| Photo deletion | Event ownership, Google Drive, database cleanup |
| Event deletion | Event ownership, photo deletion, background task safety |

## 7. Prioritization Principle

The initial release should prioritize the complete organizer-to-participant journey.

Features should not be added merely because they are technically interesting.

Any newly identified feature must be evaluated against the MVP scope before implementation.