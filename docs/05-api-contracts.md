# FrameFind — API Contracts

**Project:** FrameFind  
**Stage:** Stage 1 — MVP  
**Status:** Backend specification aligned with current FastAPI implementation  
**Base Path:** `/api/v1`

---

## 1. Overview & Conventions

This document specifies the HTTP API contracts for FrameFind. It serves as the authoritative interface contract between the FastAPI backend and client applications (React frontend, API consumers).

### 1.1 Base URL & Routing Structure

All API routes are prefixed under `/api/v1`.

```text
https://api.framefind.com/api/v1
```

Route modules are organized as follows:

| Route Prefix | Tag | Description |
|---|---|---|
| `/api/v1/auth` | Authentication | Google OAuth authentication, session validation, logout |
| `/api/v1/events` | Events | Event lifecycle, photo upload, scanning trigger, selfie search |
| `/api/v1/invitations` | Invitations | Invitation link resolution, preview, and retrieval |
| `/api/v1/photos` | Photos | Direct photo retrieval and deletion (deferred/stub) |

### 1.2 Authentication & Session Management

FrameFind uses **Cookie-based JWT Authentication** for API requests:

- Upon successful Google OAuth callback, the backend issues an `access_token` cookie.
- **Cookie Attributes:** `HttpOnly=True`, `SameSite=Lax`, `Max-Age=1800` (30 minutes), `Path=/`.
- Frontend requests must send requests with credentials included (`credentials: "include"` in `fetch` / `withCredentials: true` in `axios`).
- JavaScript cannot read the token directly.
- The `sub` claim of the JWT contains the FrameFind User UUID (`users.id`).
- When authentication fails or the cookie is missing/expired, endpoints protected by `get_current_user` return `401 Unauthorized`:
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

### 1.3 Standard Response Formats & Error Handling

- **Successful Responses:** Standard JSON payloads matching Pydantic schemas, or standard redirects (307) for OAuth entrypoints.
- **Client & Server Errors:** Standard FastAPI error envelope:
  ```json
  {
    "detail": "Descriptive error message"
  }
  ```
- **Validation Errors (422 Unprocessable Entity):** FastAPI automatic validation envelope:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "field_name"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

### 1.4 Common Data Types

- **UUIDs:** Lowercase canonical 36-character string format (e.g., `1dcad11b-91f3-406f-bdc2-c8b6adefae63`).
- **Dates:** ISO-8601 calendar date format `YYYY-MM-DD` (e.g., `2026-11-17`).
- **Timestamps:** ISO-8601 UTC timestamp format `YYYY-MM-DDTHH:MM:SSZ`.

---

## 2. Authentication Endpoints (`/api/v1/auth`)

### 2.1 Initiate Google OAuth Login

Redirects the user to Google's OAuth 2.0 consent screen requesting `openid`, `userinfo.email`, `userinfo.profile`, and `drive.file` scopes.

- **Method:** `GET`
- **Route:** `/api/v1/auth/google/login`
- **Authentication:** None (Public)
- **Request Parameters:** None

#### Response

- **Status Code:** `307 Temporary Redirect`
- **Headers:**
  - `Location`: `https://accounts.google.com/o/oauth2/auth?...`
  - `Set-Cookie`: `oauth_state=<state_token>; Max-Age=300; Path=/; SameSite=Lax`

---

### 2.2 Google OAuth Callback

Handles redirect back from Google OAuth consent flow, exchanges authorization code for Google credentials, provisions user records and Drive folders, and issues FrameFind JWT cookie.

- **Method:** `GET`
- **Route:** `/api/v1/auth/google/callback`
- **Authentication:** State cookie validation (`oauth_state`)
- **Query Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `code` | string | Yes | OAuth 2.0 authorization code from Google |
  | `state` | string | Yes | CSRF state token issued during login initiation |

#### Response

- **Status Code:** `307 Temporary Redirect`
- **Headers:**
  - `Location`: `{BACKEND_URL}/docs` (Stage 1 redirect target; redirects to frontend in production)
  - `Set-Cookie`: `access_token=<jwt>; HttpOnly; Max-Age=1800; Path=/; SameSite=Lax`
  - `Set-Cookie`: `oauth_state=; Max-Age=0; Path=/` (Deletes state cookie)

#### Error Responses

- `400 Bad Request`: State mismatch or missing `oauth_state` cookie.
  ```json
  {
    "detail": "Invalid OAuth state"
  }
  ```
- `500 Internal Server Error`: Google credential exchange or Drive folder initialization failure.

---

### 2.3 Get Current Authenticated User

Retrieves identity details for the authenticated session.

- **Method:** `GET`
- **Route:** `/api/v1/auth/me`
- **Authentication:** Required (User session cookie)
- **Request Parameters:** None

#### Success Response (`200 OK` - `UserResponse`)

```json
{
  "id": "1dcad11b-91f3-406f-bdc2-c8b6adefae63",
  "email": "organizer@example.com",
  "name": "Alex Organizer",
  "google_profile_photo": "https://lh3.googleusercontent.com/a/default-user"
}
```

#### Error Responses

- `401 Unauthorized`: Session missing or expired.

---

### 2.4 Logout

Terminates the authenticated user session by clearing the JWT access token cookie.

- **Method:** `POST`
- **Route:** `/api/v1/auth/logout`
- **Authentication:** None (Safe to call unconditionally)
- **Request Parameters:** None

#### Success Response (`204 No Content`)

- **Headers:**
  - `Set-Cookie`: `access_token=; Max-Age=0; Path=/`

---

## 3. Event Management Endpoints (`/api/v1/events`)

### 3.1 Create Event

Creates a new event, provisions a dedicated Google Drive subfolder inside the organizer's `FrameFind/Events/` directory, generates a reusable invitation token, and stores event metadata.

- **Method:** `POST`
- **Route:** `/api/v1/events`
- **Authentication:** Required
- **Request Headers:** `Content-Type: application/json`

#### Request Body (`EventCreate`)

```json
{
  "name": "Tech Conference 2026",
  "date": "2026-11-20",
  "location": "Convention Center, Hall A",
  "description": "Annual developer summit and keynote presentations."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Name of the event (1–255 characters) |
| `date` | string (date) | Yes | Date of the event (`YYYY-MM-DD`) |
| `location` | string | No | Optional venue or physical location |
| `description` | string | No | Optional event description |

#### Success Response (`201 Created` - `EventResponse`)

```json
{
  "id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
  "name": "Tech Conference 2026",
  "date": "2026-11-20",
  "location": "Convention Center, Hall A",
  "description": "Annual developer summit and keynote presentations.",
  "drive_folder_id": "1A2B3C4D5E6F7G8H9I0J",
  "invitation_token": "q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6",
  "status": "CREATED"
}
```

---

### 3.2 List User Events

Lists all events where the authenticated user is either the **owner** or an accepted **member**.

- **Method:** `GET`
- **Route:** `/api/v1/events`
- **Authentication:** Required
- **Request Parameters:** None

#### Success Response (`200 OK` - `list[EventResponse]`)

```json
[
  {
    "id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
    "name": "Tech Conference 2026",
    "date": "2026-11-20",
    "location": "Convention Center, Hall A",
    "description": "Annual developer summit.",
    "drive_folder_id": "1A2B3C4D5E6F7G8H9I0J",
    "invitation_token": "q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6",
    "status": "READY"
  }
]
```

---

### 3.3 Get Event Details

Retrieves details for a specific event. The user must be the event owner or an existing member.

- **Method:** `GET`
- **Route:** `/api/v1/events/{event_id}`
- **Authentication:** Required
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Target Event UUID |

#### Success Response (`200 OK` - `EventResponse`)

```json
{
  "id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
  "name": "Tech Conference 2026",
  "date": "2026-11-20",
  "location": "Convention Center, Hall A",
  "description": "Annual developer summit.",
  "drive_folder_id": "1A2B3C4D5E6F7G8H9I0J",
  "invitation_token": "q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6",
  "status": "READY"
}
```

#### Error Responses

- `404 Not Found`: Event does not exist or caller does not have owner/member access.
  ```json
  {
    "detail": "Event not found"
  }
  ```

---

### 3.4 Join Event via Invitation Token

Allows an authenticated participant to join an event using the event's invitation token. This operation is idempotent.

- **Method:** `POST`
- **Route:** `/api/v1/events/{event_id}/join`
- **Authentication:** Required
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Event UUID to join |

#### Request Body (`EventJoinRequest`)

```json
{
  "invitation_token": "q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6"
}
```

#### Success Responses (`200 OK`)

- **Newly Joined:**
  ```json
  {
    "message": "Successfully joined event",
    "event_id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1"
  }
  ```
- **Already a Member or Owner:**
  ```json
  {
    "message": "Already joined",
    "event_id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1"
  }
  ```

#### Error Responses

- `403 Forbidden`: Token does not match the event's invitation token.
  ```json
  {
    "detail": "Invalid invitation"
  }
  ```
- `404 Not Found`: Event not found.
  ```json
  {
    "detail": "Event not found"
  }
  ```

---

### 3.5 Delete Event (Deferred / Stub)

Deletes an event, associated photos, face embeddings, memberships, and Google Drive assets.

- **Method:** `DELETE`
- **Route:** `/api/v1/events/{event_id}`
- **Authentication:** Required (Owner only)
- **Status in Stage 1:** Route declared; implementation deferred to post-MVP milestone.

---

## 4. Photo Upload, Scan & Search Endpoints (`/api/v1/events/{event_id}/...`)

### 4.1 Upload Event Photograph

Uploads an original photograph to the event's Google Drive folder through FastAPI and records a metadata row in PostgreSQL with `processing_status = 'PENDING'`.

- **Method:** `POST`
- **Route:** `/api/v1/events/{event_id}/photos`
- **Authentication:** Required (**Event Owner Only**)
- **Request Headers:** `Content-Type: multipart/form-data`
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Target Event UUID |
- **Form Data:**
  | Field | Type | Required | Description |
  |---|---|---|---|
  | `file` | binary / file | Yes | Image file (JPEG, PNG, HEIF/HEIC) |

#### Success Response (`201 Created` - `PhotoResponse`)

```json
{
  "id": "e3b0c442-98fc-1c14-9afb-4c7c56d78a91",
  "drive_file_id": "1XyZ9_aBcDeFgHiJkLmNoPqRsTuVw",
  "filename": "keynote_stage_01.jpg",
  "mime_type": "image/jpeg",
  "processing_status": "PENDING"
}
```

#### Error Responses

- `403 Forbidden`: Authenticated user is not the event owner.
  ```json
  {
    "detail": "Only the event owner can upload photos"
  }
  ```
- `404 Not Found`: Event does not exist.

---

### 4.2 List Event Photographs

Lists metadata for all photographs uploaded to an event. Accessible by event owners and members.

- **Method:** `GET`
- **Route:** `/api/v1/events/{event_id}/photos`
- **Authentication:** Required (Owner or Member)
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Target Event UUID |

#### Success Response (`200 OK` - `list[PhotoResponse]`)

```json
[
  {
    "id": "e3b0c442-98fc-1c14-9afb-4c7c56d78a91",
    "drive_file_id": "1XyZ9_aBcDeFgHiJkLmNoPqRsTuVw",
    "filename": "keynote_stage_01.jpg",
    "mime_type": "image/jpeg",
    "processing_status": "COMPLETED"
  },
  {
    "id": "f4c1d553-09ad-2d25-0bfc-5d8d67e89b02",
    "drive_file_id": "2AbC1_dEfGhIjKlMnOpQrStUvWx",
    "filename": "audience_crowd_02.jpg",
    "mime_type": "image/jpeg",
    "processing_status": "PROCESSING"
  }
]
```

#### Error Responses

- `404 Not Found`: Event not found or caller lacks membership/ownership.

---

### 4.3 Trigger Photo Processing Scan

Atomically claims up to 100 `PENDING` event photographs using database row-level locking (`FOR UPDATE SKIP LOCKED`), updates their status to `PROCESSING`, commits the batch, and dispatches Celery background worker tasks for face detection and embedding generation.

- **Method:** `POST`
- **Route:** `/api/v1/events/{event_id}/scan`
- **Authentication:** Required (**Event Owner Only**)
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Target Event UUID |

#### Success Response (`200 OK`)

```json
{
  "event_id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
  "photos_queued": 2,
  "photo_ids": [
    "e3b0c442-98fc-1c14-9afb-4c7c56d78a91",
    "f4c1d553-09ad-2d25-0bfc-5d8d67e89b02"
  ]
}
```

#### Error Responses

- `403 Forbidden`: Caller is not the event owner.
  ```json
  {
    "detail": "Only the event owner can scan"
  }
  ```
- `404 Not Found`: Event not found.

---

### 4.4 Search Event Photos Using Selfie

Accepts a single user selfie, extracts a 512-dimensional facial embedding in-memory, queries PostgreSQL using pgvector cosine distance (`<=>`), and returns matching photographs within the specified event.

- **Method:** `POST`
- **Route:** `/api/v1/events/{event_id}/search`
- **Authentication:** Required (Owner or Member)
- **Request Headers:** `Content-Type: multipart/form-data`
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Event UUID to search within |
- **Form Data:**
  | Field | Type | Required | Description |
  |---|---|---|---|
  | `selfie` | binary / file | Yes | Query selfie image (max size 10 MB) |

#### Success Response (`200 OK`)

```json
{
  "event_id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
  "total_matches": 2,
  "matches": [
    {
      "photo_id": "e3b0c442-98fc-1c14-9afb-4c7c56d78a91",
      "filename": "keynote_stage_01.jpg",
      "cosine_distance": 0.231456,
      "cosine_similarity": 0.768544
    },
    {
      "photo_id": "f4c1d553-09ad-2d25-0bfc-5d8d67e89b02",
      "filename": "audience_crowd_02.jpg",
      "cosine_distance": 0.412891,
      "cosine_similarity": 0.587109
    }
  ]
}
```

#### Error Responses

- `400 Bad Request`:
  - Uploaded file is empty:
    ```json
    { "detail": "Uploaded image is empty" }
    ```
  - Unrecognized or corrupted image format:
    ```json
    { "detail": "Invalid or unsupported image" }
    ```
  - No faces detected in selfie:
    ```json
    { "detail": "No face detected in the uploaded selfie" }
    ```
  - Multiple faces detected in selfie:
    ```json
    { "detail": "Please upload a selfie containing only one face" }
    ```
- `404 Not Found`: Event not found or caller lacks event access.
- `413 Payload Too Large`: Selfie size exceeds 10 MB limit (`MAX_SELFIE_SIZE`).
  ```json
  {
    "detail": "Selfie must be smaller than 10 MB"
  }
  ```

---

## 5. Invitation Endpoints (`/api/v1/invitations`)

### 5.1 Preview Invitation & Membership Status

Allows an authenticated user to inspect an invitation token before joining. Returns event details and whether the user is already a member or owner.

- **Method:** `GET`
- **Route:** `/api/v1/invitations/{invitation_token}`
- **Authentication:** Required
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `invitation_token` | string | Yes | 32-byte URL-safe invitation token |

#### Success Response (`200 OK` - `InvitationResponse`)

```json
{
  "event_id": "7b58c734-d2e1-4560-93a8-a3f2b801a1d1",
  "event_name": "Tech Conference 2026",
  "date": "2026-11-20",
  "location": "Convention Center, Hall A",
  "description": "Annual developer summit.",
  "already_joined": false
}
```

#### Error Responses

- `404 Not Found`: Invalid or unrecognized invitation token.
  ```json
  {
    "detail": "Invitation not found"
  }
  ```

---

### 5.2 Get Shareable Invitation Link

Retrieves the canonical frontend invitation URL for an event. Restricted to the event owner.

- **Method:** `GET`
- **Route:** `/api/v1/invitations/events/{event_id}/link`
- **Authentication:** Required (**Event Owner Only**)
- **Path Parameters:**
  | Parameter | Type | Required | Description |
  |---|---|---|---|
  | `event_id` | UUID | Yes | Target Event UUID |

#### Success Response (`200 OK` - `InvitationLinkResponse`)

```json
{
  "invite_url": "http://localhost:5173/join/q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6j7k8l9z0x1c2v3b4n5m6"
}
```

#### Error Responses

- `404 Not Found`: Event not found or caller is not the event owner.
  ```json
  {
    "detail": "Event not found"
  }
  ```

---

## 6. Individual Photo Operations (`/api/v1/photos` — Planned / Deferred)

These endpoints represent individual photo lifecycle operations. In the current Stage 1 baseline, route definitions exist in `app/api/v1/photo.py` as stubs.

### 6.1 View / Proxy Original Photo

Authorized photo viewing proxy that streams original image bytes from the owner's Google Drive to an authorized participant or owner without exposing internal Drive file IDs.

- **Method:** `GET`
- **Route:** `/api/v1/photos/{photo_id}`
- **Authentication:** Required (Event Owner or Member)
- **Status in Stage 1:** Stubbed (`pass`).

---

### 6.2 Delete Photo

Deletes the photo record from PostgreSQL, removes associated face embeddings, and deletes the file from the owner's Google Drive.

- **Method:** `DELETE`
- **Route:** `/api/v1/photos/{photo_id}`
- **Authentication:** Required (Event Owner Only)
- **Status in Stage 1:** Stubbed (`pass`).

---

## 7. Schema Reference Summary

### `UserResponse`
```json
{
  "id": "UUID",
  "email": "string",
  "name": "string",
  "google_profile_photo": "string | null"
}
```

### `EventCreate`
```json
{
  "name": "string",
  "date": "YYYY-MM-DD",
  "location": "string | null",
  "description": "string | null"
}
```

### `EventResponse`
```json
{
  "id": "UUID",
  "name": "string",
  "date": "YYYY-MM-DD",
  "location": "string | null",
  "description": "string | null",
  "drive_folder_id": "string",
  "invitation_token": "string",
  "status": "string (CREATED | PROCESSING | READY)"
}
```

### `EventJoinRequest`
```json
{
  "invitation_token": "string"
}
```

### `PhotoResponse`
```json
{
  "id": "UUID",
  "drive_file_id": "string",
  "filename": "string",
  "mime_type": "string",
  "processing_status": "string (PENDING | PROCESSING | COMPLETED | FAILED)"
}
```

### `InvitationResponse`
```json
{
  "event_id": "UUID",
  "event_name": "string",
  "date": "YYYY-MM-DD",
  "location": "string | null",
  "description": "string | null",
  "already_joined": "boolean"
}
```

### `InvitationLinkResponse`
```json
{
  "invite_url": "string"
}
```

---

## 8. Security & Data Protection Notes

1. **Token Isolation:** Google OAuth access and refresh tokens are stored protected in PostgreSQL and are never returned in any API response.
2. **Drive File ID Exposure:** In the current Stage 1 baseline, `PhotoResponse` includes `drive_file_id`. Prior to production deployment, `drive_file_id` should be omitted from public client responses, and clients should access photos exclusively through authorized FrameFind photo UUID endpoints.
3. **Ephemeral Selfie Processing:** Selfies sent to `/api/v1/events/{event_id}/search` are decoded in memory, processed into temporary vector embeddings, and immediately discarded. Selfies are never saved to disk, PostgreSQL, or Google Drive.
4. **Vector Search Scoping:** Face similarity queries are strictly scoped to the target event via `JOIN photos ON face_embeddings.photo_id = photos.id WHERE photos.event_id = :event_id`. Vector searches never cross event boundaries.
