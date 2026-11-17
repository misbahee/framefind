# React & Frontend Engineering — Study Roadmap

**Goal:** Become comfortable architecting and building the FrameFind frontend using React, without spending unnecessary time on basic frontend concepts.

**Learning approach:** Diagnostic-first, concept-focused and project-oriented.

---

## 1. Diagnostic Assessment

Before studying a topic, assess existing knowledge.

- [ ] JavaScript fundamentals
- [ ] React components, props and state
- [ ] Context API and prop drilling
- [ ] React hooks
- [ ] API integration
- [ ] Basic CRUD operations
- [ ] Component composition

**Rule:** If understanding is sufficient, skip the topic. If there are gaps, cover only the missing concepts.

## 2. Advanced React Concepts

### 2.1 Rendering and Reconciliation
- React render and commit phases
- Virtual DOM and reconciliation
- Component re-rendering
- State updates and batching
- How React determines what needs updating
- Parent and child re-render behaviour
- React Fiber at a conceptual level

### 2.2 Hooks — Advanced Usage
- `useEffect` dependency behaviour
- Effect cleanup
- Stale closures
- Race conditions
- `useRef` vs `useState`
- `useMemo` and `useCallback`
- When memoization is useful
- `React.memo`
- Custom hooks

### 2.3 Component Architecture
- Component composition
- Separation of concerns
- Reusable components
- Container vs presentation components
- Component boundaries
- Error boundaries
- Strict Mode behaviour

## 3. State Management

**Priority: High**

### 3.1 Understanding State
- Local component state
- Shared state
- Global state
- Server state vs client state
- Context API limitations
- When global state is actually necessary

### 3.2 Redux
- Why Redux exists
- Store
- Actions
- Reducers
- Dispatch
- Unidirectional data flow
- Middleware
- Redux Toolkit overview
- Async operations and Redux Thunk
- Redux DevTools

### 3.3 Zustand
- Store creation
- State updates
- Selectors
- Subscriptions
- Actions
- Async operations
- Zustand vs Redux vs Context

### 3.4 State Management Decisions
- When to use `useState`
- When to use Context
- When to use Zustand
- When Redux makes sense
- Avoiding unnecessary global state

**Practical exercise:** Build a small application with authentication state and shared UI state using Context and Zustand.

**Note:** Redux and Zustand are learning topics. We will select the actual FrameFind solution based on requirements rather than automatically adding both.

## 4. TanStack Query

**Priority: Very High**

This is a new area to study because API integration alone does not cover server-state management.

### 4.1 Fundamentals
- What server state means
- Why API data needs a separate management strategy
- Queries and query keys
- Query lifecycle
- Loading, error and success states

### 4.2 Caching
- Query caching
- Cache lifetime
- Stale data
- `staleTime`
- `gcTime`
- Background refetching
- Cache invalidation

### 4.3 Mutations
- Creating and updating data
- Deleting data
- Mutation lifecycle
- Success and error handling
- Query invalidation after mutations
- Optimistic updates

### 4.4 Advanced Concepts
- Dependent queries
- Query retries
- Pagination
- Infinite queries
- Refetching strategies
- Query cancellation

**Practical exercise:** Build an event dashboard that fetches events, creates an event, updates cached data and handles API failures.

## 5. Frontend Architecture

**Priority: High**

### 5.1 Routing
- React Router
- Nested routes
- Dynamic routes
- `useNavigate`
- `useParams`
- `Outlet`
- Protected routes
- Authentication-aware navigation

### 5.2 Authentication
- Authentication vs authorization
- JWT-based authentication
- HttpOnly cookies
- `credentials: "include"`
- Authentication state initialization
- Login and logout flows
- Session expiration
- Route protection
- CORS and CSRF fundamentals

### 5.3 API Architecture
- Centralized API client
- Fetch API
- Request and response handling
- Error handling
- API service modules
- Separation of API logic from components
- Environment variables

### 5.4 Forms
- Controlled components
- Form validation
- Form submission lifecycle
- React Hook Form
- Reusable form components
- Handling API validation errors

### 5.5 File Handling
- File input
- `FormData`
- Multipart requests
- Image previews using object URLs
- Object URL cleanup
- Upload progress
- File validation
- Upload error handling

## 6. FrameFind Implementation Preparation

Apply the concepts to actual product requirements.

### Authentication
- Google OAuth flow
- Authentication state
- Session initialization
- Logout
- Protected routes

### Event Management
- Fetch owned and joined events
- Create events
- Event details
- Loading and error states
- Cache invalidation

### Photo Management
- Upload photos
- Image previews
- Upload states
- Photo listing
- Processing statuses
- Scan initiation

### Participant Experience
- Invitation preview
- Join event
- Selfie upload
- Face search
- Search results
- Photo viewer

### Application Architecture
- Feature-based folder structure
- Reusable UI components
- API service layer
- Authentication provider
- TanStack Query integration
- Route organisation

---

## 7. Topics to Skim or Defer

| Topic | Approach |
|---|---|
| JSX and basic components | Diagnostic check |
| Props and basic state | Diagnostic check |
| Context API basics | Diagnostic check |
| Basic CRUD | Skip if proficient |
| Basic JavaScript | Diagnostic check |
| MobX | Brief comparison |
| Webpack and Babel internals | Conceptual overview |
| Firebase CRUD | Skip for FrameFind |
| Advanced animations | Defer |
| Deep Redux internals | Only if needed |
| TypeScript | Introduce after React fundamentals |

---

## 8. Learning Sequence

1. Diagnostic assessment
2. Advanced React rendering concepts
3. Advanced hooks and component architecture
4. State management architecture
5. Redux fundamentals
6. Zustand implementation
7. TanStack Query
8. React Router and application routing
9. Authentication architecture
10. API architecture and error handling
11. Forms and file handling
12. FrameFind frontend implementation

---

## 9. Readiness Checklist

Before starting the main FrameFind implementation, I should be able to:

- [ ] Explain React's rendering and reconciliation process.
- [ ] Understand state updates, batching and stale closures.
- [ ] Use effects correctly and handle cleanup.
- [ ] Explain Context limitations.
- [ ] Understand Redux and Zustand architecture.
- [ ] Distinguish server state from client state.
- [ ] Use TanStack Query queries and mutations.
- [ ] Handle caching and query invalidation.
- [ ] Implement nested and protected routes.
- [ ] Understand HttpOnly cookie authentication.
- [ ] Build a centralized API client.
- [ ] Handle forms and API validation errors.
- [ ] Upload files using `FormData`.
- [ ] Handle loading, error, empty and success states.

---

## 10. Teaching Method

For every topic:

1. Start with a diagnostic question.
2. Check existing understanding.
3. Explain only missing concepts.
4. Explore internal behaviour and trade-offs.
5. Implement a small practical example.
6. Connect the concept to FrameFind.
7. Move forward when understanding is sufficient.

**Important constraints:**
- Avoid repeating concepts already understood.
- Prioritize architecture and practical engineering.
- Avoid unnecessary theoretical depth.
- Don't learn libraries just for the sake of learning them.
- Introduce tools when there is a clear engineering reason.
- Keep FrameFind as the final practical application.

**Final objective:** Build FrameFind with a sound React architecture, appropriate state management, reliable API integration and maintainable components — without spending time mastering frontend topics that aren't relevant to the project.