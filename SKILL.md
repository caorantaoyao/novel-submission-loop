---
name: novel-submission-loop
description: "Use when the user wants to run the fixed Qimao editor novel submission loop: use the fixed editor preference library, take the next editor from the queue, decide the submission type from that editor's preferences, search male-channel candidate books only on Qidian Chinese Network and female-channel candidate books only on Fanqie Novel, select an excellent but non-mega-hit target book, read its first five chapters, generate detailed chapter outlines, write first five chapters, create title/introduction/character names/chapter names, generate a Word document, prepare an email preview, send only through the QQ Mail plugin after explicit confirmation, record the submission, and move to the next editor."
---

# Novel Submission Loop

Follow the user's locked workflow exactly. Do not add, remove, or reorder top-level steps.

## Locked Workflow

1. Read the fixed editor preference library.
2. Take the next editor from the queue.
3. Decide the submission type from that editor's preferences.
4. Automatically find candidate books for that type.
5. Select an excellent but non-mega-hit target book.
6. Read the target book's first five chapters.
7. Generate a detailed outline for each chapter.
8. Write first five chapters.
9. Generate or rewrite the book title, synopsis, character names, and chapter names.
10. Generate a Word document.
11. Prepare an email preview.
12. Send only after the user explicitly confirms.
13. Record the submission.
14. Move automatically to the next editor.

## Fixed Files

Use these repo-relative files:

- `data/editors/qimao_editors.json`: fixed editor preference library.
- `data/editors/editor_cursor.json`: queue cursor.
- `outputs/submission_log.jsonl`: append-only submission log.
- `outputs/<project_slug>/`: per-submission artifacts.

Use this helper when possible:

```bash
python3 .agents/skills/novel-submission-loop/scripts/editor_queue.py next
python3 .agents/skills/novel-submission-loop/scripts/editor_queue.py advance --project "<project_slug>" --title "<book_title>" --docx "outputs/<project_slug>/<book_title>.docx" --status sent
```

## Per-Submission Artifacts

Create these files for each run:

```text
outputs/<project_slug>/
  00_editor.md
  01_type_decision.md
  02_candidates.md
  03_target_book.md
  04_chapter_outlines.md
  05_draft.md
  06_title_intro_names.md
  07_mail_preview.md
  <book_title>.docx
```

## Execution Rules

- Start by reading the next editor via `editor_queue.py next`.
- Use the editor's stated preferences as fixed data. Do not refresh, mutate, or reinterpret the editor library unless the user explicitly asks.
- Choose one submission type from the editor's preferences and explain the choice in `01_type_decision.md`.
- For candidate search, target books that are strong enough to prove market fit but not obvious mega-hits.
- Record candidate evidence in `02_candidates.md`: source, title, author if visible, popularity signal, update status if visible, why it qualifies, and why it is not a mega-hit.
- Use only one selected target book for the chapter reading and outline.
- Keep the generated manuscript aligned with the chosen editor preference and submission type.
- Generate the Word document after the draft, title, synopsis, character names, and chapter names are finalized.
- Use the document workflow available in the current Codex session for `.docx` creation and render/QA when available.
- Prepare the email preview before any send attempt. Include recipient, subject, body, and attachment path.
- Send email only through the QQ Mail plugin / `qq_mail` tool.
- Never send the email until the user explicitly confirms the exact preview.
- Only after successful send, append the submission log and advance the cursor.
- If the QQ Mail plugin / `qq_mail` tool is unavailable or cannot attach the Word file, leave status as `prepared` and do not advance the cursor unless the user instructs otherwise.

## Submission Word Rules

Apply these rules to the final `.docx` intended for the editor:

- Name the final Word file with the novel title only: `outputs/<project_slug>/<book_title>.docx`.
- Do not use numeric prefixes, queue numbers, project slugs, editor names, platform names, dates, or labels such as `08_submission` in the final Word filename.
- If the novel title contains filesystem-invalid characters, remove only those invalid characters. Do not add replacement numbering.
- If a same-title `.docx` already exists, ask the user before overwriting or renaming. Do not silently add `1`, `v2`, timestamps, or queue numbers.
- The submitted Word document must be a clean manuscript, not an operations report.
- By default, the Word document should contain only the novel title and the five completed chapters with final chapter names.
- Keep synopsis, character names, title options, editor information, candidate evidence, target-book notes, and submission metadata in the Markdown artifacts or email preview, not inside the submitted Word document.
- Do not include sections titled or equivalent to: `投稿信息`, `编辑信息`, `目标书`, `参考书`, `候选书`, `主要人物`, `人物设定`, `创作说明`, `AI说明`, `生成说明`, `细纲`, `节奏表`, `大纲`, or `备注`.
- Do not mention `AI`, `Codex`, `ChatGPT`, prompts, model usage, automated generation, source-book analysis, or workflow steps anywhere in the submitted Word document.
- Before preparing the email preview, inspect the generated `.docx` text or rendered output and verify that forbidden metadata sections are absent.

## Search Source Rules

Apply these rules to the candidate-book and target-book steps:

- Route search source by the current editor's `channel` field in `data/editors/qimao_editors.json`.
- If the editor channel is `男频`, search and select candidate books only on Qidian Chinese Network.
- If the editor channel is `女频`, search and select candidate books only on Fanqie Novel.
- Do not mix Qidian and Fanqie candidates in the same run.
- Allowed male-channel candidate evidence sources are official Qidian pages under `qidian.com`.
- Allowed female-channel candidate evidence sources are official Fanqie Novel pages under `fanqienovel.com`.
- Do not use Qimao, Jinjiang, Zongheng, Webnovel, WeChat Reading, Baidu result snippets, media articles, social posts, forum posts, or third-party novel mirrors as candidate evidence.
- Do not select a target book unless its candidate evidence comes from the routed allowed source.
- If an external search engine is used only to locate a page, open and verify the routed official Qidian or Fanqie page before recording the candidate. The search result itself is not evidence.
- Record the routed source site for every candidate in `02_candidates.md` as either `Qidian` for male-channel runs or `Fanqie` for female-channel runs.
- If the editor channel is missing or unclear, stop and ask the user before searching.

## Browser Safety Rules

Apply these rules whenever using Qidian or Fanqie:

- Use a normal browser surface first: the in-app browser or the user's Chrome session when available.
- Do not use `curl`, `wget`, raw HTTP scripts, custom scrapers, batch DOM extraction loops, or concurrent page fetches for book pages or chapter pages.
- Do not open pages in parallel. Navigate one page at a time and wait for the visible page to load before reading or moving on.
- Limit candidate discovery to normal browsing: inspect at most 5 candidate book detail pages for one run.
- Use list/search/ranking pages only to identify candidates. Do not open many chapter pages during candidate discovery.
- Once the target book is selected, stop candidate browsing and read only that one book's first five chapters.
- Read chapters sequentially from chapter 1 to chapter 5. Do not revisit chapters repeatedly unless a page failed to load.
- Extract only enough information to write chapter outlines. Do not save, quote, or export full chapter text.
- If a captcha, login wall, unusual verification page, anti-bot warning, blank protected page, or access throttle appears, stop site interaction immediately. Record the block in the current artifact and ask the user to resolve it manually or choose another source.
- If the site is unstable or slow, reduce scope instead of retrying aggressively: keep the selected target if already known, or stop after the available candidate evidence.

## Email Rules

Apply these rules to the email preview and final send:

- Use only the QQ Mail plugin / `qq_mail` tool for the final send.
- Do not use Gmail, Lark Mail, system mail clients, browser-based manual sending, SMTP scripts outside the QQ Mail plugin, or any other email connector.
- The email attachment must be the final clean Word manuscript: `outputs/<project_slug>/<book_title>.docx`.
- The email body must contain only the novel title and the novel synopsis.
- Do not include greetings, editor names, self-introduction, submission notes, attachment explanations, contact details, thanks, signatures, workflow notes, source-book notes, or AI/model/tool references in the email body.
- The email preview may show recipient, subject, and attachment path as preview metadata, but those fields must not be repeated inside the email body.

## Email Preview Format

Write `07_mail_preview.md` like this:

```markdown
# Mail Preview

收件人：
主题：
附件：

正文：

小说名：

小说简介：

发送前确认口令：
确认发送
```

## Submission Log

When the user confirms and the email is sent, append one JSON object per line to `outputs/submission_log.jsonl` with:

- `timestamp`
- `platform`
- `editor`
- `email`
- `submission_type`
- `target_book`
- `title`
- `project`
- `docx`
- `status`

Then advance `data/editors/editor_cursor.json` to the next editor.
