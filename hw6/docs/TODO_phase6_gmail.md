# TODO — Phase 6: Gmail Report

**Dependency:** Phase 3 complete.  
**PRD:** [PRD_gmail_report.md](PRD_gmail_report.md)  
**Status:** [ ] Not started

---

## 1. Google Cloud Setup (one-time, manual)

- [x] Go to https://console.cloud.google.com
- [x] Create a new project (e.g. `cop-thief-ex06`)
- [x] Enable **Gmail API**: APIs & Services → Enable APIs → search "Gmail API"
- [x] Enable **Google Calendar API** (required by scopes)
- [x] Go to **APIs & Services → OAuth consent screen**:
  - User Type: External
  - App name: `Cop Thief EX06`
  - Add scopes: `gmail.modify`, `calendar`
  - Add test user: your Gmail address
- [x] Go to **APIs & Services → Credentials**:
  - Create Credentials → OAuth client ID
  - Application type: **Desktop app**
  - Download JSON → rename to `credentials.json`
  - Place in `hw6/` root (git-ignored)
- [x] Verify `credentials.json` exists and is git-ignored

---

## 2. Report Builder (TDD)

- [ ] Write `tests/unit/test_report_builder.py` FIRST (red):
  - `test_report_has_all_required_fields`
  - `test_report_body_is_valid_json`
  - `test_report_excludes_crashed_sub_games`
  - `test_report_totals_match_sub_game_scores`
  - `test_report_contains_student_names`
  - `test_report_contains_github_repo`
- [ ] Implement `src/cop_thief/gmail/report_builder.py` (green):
  - `ReportBuilder.build(game_result, config) -> dict`
  - Validates all required fields present
  - Filters out crashed sub-games
- [ ] Refactor — keep file ≤ 150 code lines
- [ ] `uv run ruff check` → 0 violations

---

## 3. Auth Module (TDD)

- [x] Write `tests/unit/test_auth.py` FIRST (red):
  - `test_loads_credentials_from_file`
  - `test_refreshes_expired_token`
  - `test_saves_refreshed_token`
  - `test_missing_credentials_raises_error`
  - (added) `test_first_run_launches_browser_flow`
- [x] Implement `src/cop_thief/gmail/auth.py` (green):
  - `GmailAuth.get_credentials() -> Credentials`
  - First run: browser OAuth flow → saves `token.json`
  - Subsequent runs: load `token.json`, refresh if expired
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations

---

## 4. Sender (TDD)

- [x] Write `tests/unit/test_sender.py` FIRST (red):
  - `test_email_sent_to_correct_recipient`
  - `test_email_body_is_json_only`
  - `test_email_sent_exactly_once`
  - `test_retry_on_api_failure`
  - `test_send_result_logged`
  - (added) `test_send_logs_failure_and_reraises`
- [x] Implement `src/cop_thief/gmail/sender.py` (green):
  - `GmailSender.send(report_dict, config) -> None`
  - Uses ApiGatekeeper for the API call
  - Email body: `json.dumps(report_dict, indent=2)` — no free text
  - Logs send timestamp and status to `results/gmail_log.json`
- [x] All Gmail API calls mocked in tests — no real sends
- [x] Refactor — keep file ≤ 150 code lines
- [x] `uv run ruff check` → 0 violations
- [x] Generalized `ApiGatekeeper` (Phase 3) with `call_sync(provider, func)` so
  Gmail's blocking google-api-client call goes through the same central
  gate as the LLM's async httpx call — added a `gmail` rate-limit section
  to `config/rate_limits.json`.

---

## 5. First-Run OAuth Flow (manual)

- [x] Run the OAuth flow → Browser opens → sign in → consent → `token.json` created
  (hit `Error 403: access_denied` first — account wasn't correctly saved as
  a Test user; fixed, then consent screen worked)
- [x] Verify `token.json` exists and is git-ignored

---

## 6. End-to-End Test (manual)

- [ ] Run a full game: `uv run python src/main.py --headless`
  → After 6 sub-games, email sent automatically
- [ ] Check inbox of `rmisegal+uoh26b@gmail.com` (ask lecturer to confirm)
- [ ] Verify email body is valid JSON with no free text

---

## 7. Phase 6 Sign-off

- [ ] `uv run pytest tests/ --cov` → all green, coverage ≥ 85%
- [ ] `uv run ruff check .` → 0 violations
- [ ] Email received and verified by team
- [ ] All files have docstrings
- [ ] Commit: `git commit -m "ex06: phase 6 — Gmail OAuth report sender"`
- [ ] Push to `yamandahle-hw6`
- [ ] Update [TODO.md](TODO.md) phase status to `[x] Done`
