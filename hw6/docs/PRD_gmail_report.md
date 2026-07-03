# PRD — Gmail Report

**Mechanism:** Automated Gmail Report Sender  
**Version:** 1.0  
**Date:** 2026-07-03  
**Status:** Draft

---

## 1. Purpose

After all 6 sub-games complete, the **Cop agent** automatically sends one email
to the lecturer containing a structured JSON report of the game results.
The email body is JSON-only — no free text. Authentication uses OAuth 2.0
with a Desktop client type (token stored locally, never hardcoded).

---

## 2. Responsibilities

| Responsibility | Description |
|----------------|-------------|
| Compose report | Build the JSON report dict from GameResult |
| Authenticate | Load OAuth token from `token.json`; refresh if expired |
| Send email | POST to Gmail API with JSON body (no free text) |
| Retry on failure | Up to `gmail.max_retries` times via ApiGatekeeper |
| Log send result | Timestamp, status, recipient logged to results/ |

---

## 3. JSON Report Schema

Sent as email body (Content-Type: text/plain, content is a JSON string):

```json
{
  "group_name": "...",
  "students": ["Student One", "Student Two"],
  "github_repo": "https://github.com/...",
  "cop_mcp_url": "http://localhost:8001",
  "thief_mcp_url": "http://localhost:8002",
  "timezone": "Asia/Jerusalem",
  "sub_games": [
    {
      "sub_game_number": 1,
      "winner": "cop",
      "moves_played": 14,
      "cop_score": 20,
      "thief_score": 5,
      "barriers_placed": 2,
      "cop_messages": ["I see you.", "Corner is mine."],
      "thief_messages": ["I'm going north.", "You'll never catch me."]
    }
  ],
  "totals": {
    "cop": 75,
    "thief": 45
  }
}
```

Rules (from assignment):
- Body contains **only** the JSON string — no greeting, no signature, no free text.
- Sub-games that crashed and were re-run are excluded from the report.
- The report is sent exactly **once** after the 6th valid sub-game.

---

## 4. OAuth 2.0 Setup

| Item | Detail |
|------|--------|
| Client type | Desktop (not Web) |
| Scopes | `gmail.modify`, `calendar` |
| Credentials file | `credentials.json` (git-ignored, obtained from Google Cloud Console) |
| Token file | `token.json` (git-ignored, created on first run) |
| First-run flow | Opens browser for consent; saves token.json |
| Token refresh | Automatic via `google-auth-oauthlib` when token expires |

Setup steps documented in `docs/course/google-api-guide.pdf`.

---

## 5. Send Flow

```
1. Build JSON report from GameResult (SDK call)
2. Validate JSON schema (all required fields present)
3. Load credentials: token.json → refresh if expired → save updated token
4. Compose email:
     To: config.gmail.recipient
     Subject: "Game Report — <group_name>"
     Body: json.dumps(report, indent=2)
5. ApiGatekeeper.call(gmail_api, send_request)
6. Log: {"sent_at": ..., "status": "ok"|"failed", "recipient": ...}
```

---

## 6. Config Parameters Used

```
gmail.recipient          # lecturer address — never hardcoded
gmail.credentials_file   # default: "credentials.json"
gmail.token_file         # default: "token.json"
gmail.max_retries        # default: 3
reporting.group_name
reporting.github_repo
reporting.timezone
```

---

## 7. .env Variables

```
# .env (git-ignored)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
```

```
# .env.example (committed)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
```

---

## 8. Test Plan

| Test | Type | Description |
|------|------|-------------|
| `test_report_schema_valid` | unit | All required JSON fields present |
| `test_report_no_free_text` | unit | Body is valid JSON, no extra text |
| `test_report_excludes_crashed` | unit | Crashed sub-games not in report |
| `test_token_refresh_called` | unit | Expired token triggers refresh |
| `test_send_called_once` | unit | Email sent exactly once after 6 sub-games |
| `test_send_retry_on_failure` | unit | API failure triggers retry up to max_retries |
| `test_send_integration` | integration | Full flow with mocked Gmail API (no real send) |

Real Gmail API is never called in tests — fully mocked via `unittest.mock`.

---

## 9. File Layout

```
src/cop_thief/gmail/
├── __init__.py
├── report_builder.py   # Builds JSON report dict from GameResult
├── auth.py             # OAuth2 token load/refresh logic
└── sender.py           # Gmail API send call via ApiGatekeeper
```

Each file stays under 150 code lines.
