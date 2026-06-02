# Stage 1 — How to Run the Manual Debate

You are the Father (judge) in this stage.
Your job is to copy-paste arguments between the two AIs and observe what happens.
No automation. No code. Just you in the middle.

---

## Setup

- Browser tab 1: ChatGPT — this is the PRO side
- Browser tab 2: Gemini — this is the CON side

---

## Step 1 — Start PRO (ChatGPT)

1. Open ChatGPT in a new conversation
2. Paste the entire contents of `stage1/pro_prompt.md`
3. Then type exactly:

   > Start the debate. Make your opening argument.

4. Copy the full PRO response.

---

## Step 2 — First CON reply (Gemini)

1. Open Gemini in a new conversation
2. Paste the entire contents of `stage1/con_prompt.md`
3. Then type exactly:

   > The PRO side just said:
   > [paste the PRO response here]
   > Now make your counter argument.

4. Copy the full CON response.

---

## Step 3 — PRO replies to CON (ChatGPT)

1. Go back to the ChatGPT tab (same conversation — do NOT start a new one)
2. Type exactly:

   > The CON side just said:
   > [paste the CON response here]
   > Now respond.

3. Copy the full PRO response.

---

## Step 4 — Repeat

Go back to Gemini (same conversation) and repeat Step 2 with the new PRO response.
Then go back to ChatGPT and repeat Step 3 with the new CON response.

Run 5 full rounds total (5 PRO arguments + 5 CON arguments).

---

## Step 5 — Judge the debate yourself

After 5 rounds, read through the full exchange and ask yourself:

- Who made the stronger arguments overall?
- Who used better evidence and real statistics?
- Who was more persuasive — and why?
- Did either side try to soften their position or partially agree?
- Did either side repeat the same point more than once?
- Which single argument was the most effective?
- What would you change in the prompts to make the debate sharper?

Write your answers in `stage1/observations.md`.

---

## After the debate

- Take a screenshot of the full ChatGPT conversation
- Take a screenshot of the full Gemini conversation
- Save both screenshots to `assets/stage1/`
- Name them: `chatgpt_pro_session.png` and `gemini_con_session.png`
- Then fill in `stage1/observations.md`

---

## Git commit when done

```
git add hw2/stage1/ hw2/assets/stage1/
git commit -m "feat: Stage 1 manual debate - prompts and screenshots"
git push origin yamandahle-hw2
```
