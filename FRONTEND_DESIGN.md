# FrameFind — Frontend Design Decisions

**Stage:** Stage 1 / MVP  
**Frontend:** React + Vite + JavaScript  
**Status:** Initial design decisions

---

## 1. Design approach

FrameFind will have two distinct user experiences within the same application:

1. **Event Owner Experience** — for creating events, uploading photographs, managing scans and sharing invitations.
2. **Participant Experience** — for joining events, uploading selfies and viewing matching photographs.

Both experiences use the same FrameFind backend and authentication system.

We will design and implement the Event Owner Experience first, followed by the Participant Experience.

The interface must remain simple and focused on the Stage 1 PRD. Features outside the MVP should not be added prematurely.

## 2. Visual design direction

The chosen visual direction is a premium photography SaaS interface.

### Design characteristics

- Light theme.
- Warm off-white backgrounds.
- Dark charcoal typography.
- Deep violet / indigo as the primary accent colour.
- Clean, modern sans-serif typography.
- Subtle borders and restrained shadows.
- Rounded cards without excessive use of rounded containers.
- Generous whitespace.
- Large, high-quality event photographs.
- Minimal and intuitive navigation.

### Design inspiration

Relivo will be used as a reference for the event photography experience.

The intention is to take inspiration from its photography-led presentation and event-gallery experience, not to copy its interface.

FrameFind should maintain its own visual identity.

## 3. Development approach

We will follow an incremental design and implementation process.

1. Design the required pages in Stitch.
2. Review and refine the generated designs.
3. Establish consistent design patterns and reusable components.
4. Implement the pages using React and Vite.
5. Connect the frontend to the existing FastAPI backend.
6. Add functionality based on actual UI requirements.

We will initially use mock data where necessary so that frontend development does not depend on every backend feature being complete.

We will not implement all pages and functionality simultaneously.

## 4. Milestone 1 — Event Owner Experience

The first milestone covers four primary page groups.

### Page 1 — Landing Page

Purpose: Introduce FrameFind and allow users to start using the application.

Sections:

- Navigation bar.
- FrameFind logo and branding.
- Hero section explaining the product.
- Primary Google sign-in / Get Started action.
- How FrameFind works.
- Main product benefits.
- Privacy explanation.
- Footer.

The landing page should communicate the central concept:

Event organisers upload photographs, and participants find their photographs using a selfie.

### Page 2 — Authentication and Onboarding

Authentication:

- Sign in with Google.
- Google OAuth loading state.
- Authentication failure state.
- Returning-user flow.
- First-time-user flow.

Google Drive onboarding:

- Welcome screen.
- Explain why Google Drive access is required.
- Connect Google Drive action.
- Successful connection state.
- Connection failure or reconnection state.

Google access and refresh tokens must never be exposed to the frontend.

### Page 3 — Owner Dashboard

Purpose: Give users an overview of their events.

Required elements:

- Application navigation.
- User profile information.
- Events owned by the user.
- Events joined by the user.
- Create Event action.
- Event cards containing:
  - Event name.
  - Event date.
  - Event status.
  - Relevant event information.

Required states:

- Loading.
- Empty events list.
- Events available.
- API error.

### Page 4 — Create Event

Event creation form:

- Event name (required).
- Event date (required).
- Location (optional).
- Description (optional).

Actions:

- Create event.
- Cancel / go back.
- Validation errors.
- Creation loading state.
- Creation success or failure feedback.

## 5. Milestone 2 — Event Workspace

This will be designed after Milestone 1.

The event workspace will contain three primary tabs:

1. Overview.
2. Photos.
3. Settings.

### Overview

- Event information.
- Total uploaded photographs.
- Processing statistics.
- Invitation link.
- Copy invitation link action.

### Photos

- Upload photographs.
- Display uploaded photographs.
- Display individual processing statuses.
- Start scanning action.
- Scanning progress.
- Failed photo information.

Photo processing statuses:

- PENDING
- PROCESSING
- COMPLETED
- FAILED

### Settings

- Display event information.
- Delete event action when backend deletion functionality is implemented.

## 6. Milestone 3 — Participant Experience

This will be designed after the owner experience.

Primary pages:

1. Invitation preview.
2. Event joining.
3. Selfie search.
4. Search results.

### Invitation Preview

- Event name.
- Date.
- Location.
- Description.
- Join event action.
- Already joined state.

### Selfie Search

- Event information.
- Selfie upload.
- Image preview.
- Search action.
- Searching/loading state.
- No face detected error.
- Multiple faces detected error.
- Invalid image error.

### Search Results

- Matching photograph grid.
- Paginated results.
- Full-size photo viewer.
- Previous / next navigation.
- No matching photographs state.
- Search again action.

Photographs will be retrieved through authorised FastAPI endpoints. Google Drive file IDs will remain internal.

## 7. Navigation

### Owner navigation

The authenticated owner interface will use a minimal navigation structure.

Proposed sections:

- Dashboard.
- Events.
- Profile / Account menu.

The detailed navigation layout will be finalised during dashboard design.

### Participant navigation

The participant experience will use a simpler, task-focused layout.

Participants should not see owner management navigation.

## 8. Out-of-scope features

The following features are excluded from the Stage 1 frontend:

- Participant My Gallery.
- Saving photographs to participant Google Drive.
- Participant management interface.
- Participant approval or removal.
- Photographer accounts.
- Multiple event administrators.
- Public event discovery.
- Social features such as likes and comments.
- Advanced event editing.
- Similarity scores displayed to participants.
- Bulk photo downloads.
- Advanced analytics dashboard.

These features should not be included in the initial Stitch designs.

## 9. Important design principles

- Design complete interaction states, not just static pages.
- Include empty, loading, success and error states.
- Use modals only when necessary.
- Prefer inline feedback and toast notifications for simple actions.
- Maintain consistent typography, colours, spacing and components.
- Keep the participant experience simple.
- Do not design functionality that is not supported by the Stage 1 PRD.
- Keep the implementation incremental and avoid unnecessary abstractions.

## 10. Immediate development plan

| Order | Deliverable | Status |
|---|---|---|
| 1 | Landing page design | Next |
| 2 | Authentication and onboarding design | Next |
| 3 | Dashboard design | Pending |
| 4 | Create event design | Pending |
| 5 | Review and refine designs | Pending |
| 6 | React implementation | Pending |
| 7 | Backend integration | Pending |

After Milestone 1, proceed to the Event Workspace and then the Participant Experience.

---

**Guiding principle:** Build the smallest complete Stage 1 user experience first. Add further functionality only when the product requires it.