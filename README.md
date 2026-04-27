# Code Paste Bin with Syntax Highlighting

Build a fullstack pastebin service from scratch. Visitors paste code, choose a language, and receive a permanent shareable URL with full syntax highlighting. No login required — the app is entirely public.

## Stack

- **Backend**: Flask + SQLite (port 3001)

## Features

### Creating a Paste

The home page (`/`) is the paste creation form. It includes:

- A large code input area where the user types or pastes their code.
- A language selector dropdown with at minimum: Python, JavaScript, Go, Rust, SQL.
- An expiry setting with two modes:
  - **View-count expiry** — the paste is deleted after a specified number of views (burn-after-reading). Must support at least 1 to 100 views.
  - **Time-based expiry** — the paste expires after a chosen duration. Must include options for 10 seconds (for testing), 1 minute, 1 hour, 1 day, and 1 week. A "never" option must also be available.
- An optional password field. When filled, any visitor must supply the correct password before viewing the paste content.
- A submit button that creates the paste and redirects to the paste's view page.

Each paste is assigned a short random ID (e.g., 8 alphanumeric characters) that forms part of its URL.

### Viewing a Paste

**`/p/:id`** — the paste view page. It renders the stored code with syntax highlighting applied for the paste's chosen language. Line numbers are shown alongside every line of code. The highlighted code block must use a well-known highlighting library (e.g., highlight.js or Prism) — do not write a custom highlighter.

If the paste is password-protected and the user has not yet authenticated for this paste, the page must show only a password prompt. The paste content, language, and metadata must not be visible until the correct password is entered. On incorrect password, display an error. On success, show the full paste view for the remainder of the browser session (the user should not be asked for the password again if they navigate away and return in the same session).

If the paste has expired (either by view count or time), the page must show an expiry notice and nothing else.

If the paste ID does not exist, the page must show a not-found notice.

### Line Number Interaction

Each line number in the highlighted view is clickable. Clicking line number N must:
1. Highlight that line visually (e.g., a distinct background color on the entire line).
2. Update the URL hash to `#LN` (e.g., `#L7` for line 7).

When the page is loaded with a hash of the form `#LN`, line N must be highlighted automatically on load. Only one line can be highlighted at a time; clicking a different line removes the previous highlight.

### Raw Endpoint

`GET /raw/:id` — serves the paste's content as plain text. The response `Content-Type` must be `text/plain; charset=utf-8`. No HTML, no syntax highlighting — just the raw code string. If the paste requires a password, include the password as a query parameter `?password=...`. If the paste is expired or not found, return an appropriate HTTP status (`404` or `410`).

### Expiry Behavior

- **View-count expiry**: the view counter increments each time the paste view page (`/p/:id`) is successfully rendered to the user (i.e., after any password check passes). Once the limit is reached, the paste is considered expired and all further requests — including raw — must return the expiry state.
- **Time-based expiry**: calculated from the creation time. Once the wall-clock time has passed the expiry timestamp, the paste is considered expired.
- A paste with `"never"` expiry never expires.
- Expired pastes should not be purged from the database immediately; they must simply be treated as expired when accessed.

### Persistence

All paste data is stored in SQLite. The application must survive a server restart with all pastes intact.

---

## Pages

**`/`** — paste creation form.

**`/p/:id`** — paste view. Shows syntax-highlighted code with line numbers, expiry info, and a link to the raw endpoint. If password-protected and not yet unlocked, shows only the password gate. If expired, shows only the expiry notice.

---

## UI Requirements

Use these `data-testid` attributes exactly — the test harness depends on them.

### Creation form (`/`)

- `data-testid="code-input"` — the main code textarea
- `data-testid="language-select"` — language dropdown (`<select>`); option values must be lowercase: `"python"`, `"javascript"`, `"go"`, `"rust"`, `"sql"`
- `data-testid="expiry-type-select"` — dropdown to choose between `"views"` and `"time"` expiry modes
- `data-testid="expiry-views-input"` — number input for view-count limit (visible only when expiry type is `"views"`)
- `data-testid="expiry-time-select"` — dropdown for time duration (visible only when expiry type is `"time"`); option values: `"10s"`, `"1m"`, `"1h"`, `"1d"`, `"1w"`, `"never"`
- `data-testid="password-input"` — optional password field
- `data-testid="create-btn"` — submit button

### Paste view (`/p/:id`)

- `data-testid="code-block"` — the element wrapping the syntax-highlighted code
- `data-testid="language-label"` — displays the paste's language name
- `data-testid="line-number"` — each line number element (there will be multiple); the `data-line` attribute on each must equal the line's 1-based number as a string (e.g., `data-line="1"`)
- `data-testid="raw-link"` — anchor linking to the raw endpoint for this paste
- `data-testid="expired-message"` — shown when the paste has expired (either by views or time); must not be present when paste is active
- `data-testid="not-found-message"` — shown when no paste with this ID exists
- `data-testid="expiry-info"` — shows expiry details (e.g., "Expires in 23h" or "3 views remaining"); visible on active pastes

### Password gate (shown on `/p/:id` when paste is locked)

- `data-testid="password-gate"` — the wrapper element for the entire password-gate UI
- `data-testid="password-gate-input"` — password entry field
- `data-testid="password-gate-submit"` — submit button
- `data-testid="password-gate-error"` — error shown on wrong password; must not be present before a failed attempt

---

## Additional Requirements

- The creation form must reset (or navigate to `/`) after a successful paste is created — the user should land on the new paste's view page, not stay on the form.
- A paste's view page must include a visible link or button that copies the shareable URL to the clipboard, OR simply displays the full URL in a readable element (`data-testid="share-url"`).
- The raw link (`data-testid="raw-link"`) on the view page must point to `/raw/:id`.
- Syntax highlighting must visually differ between at least two different languages — the color tokens applied to Python keywords must differ from those applied to SQL keywords, for example.
- Line numbers must be rendered in the DOM as individual elements (not a single block of text) so they are individually clickable and selectable by the test harness.
