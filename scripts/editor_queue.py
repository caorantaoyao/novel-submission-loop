#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
EDITORS_PATH = ROOT / "data" / "editors" / "qimao_editors.json"
CURSOR_PATH = ROOT / "data" / "editors" / "editor_cursor.json"
LOG_PATH = ROOT / "outputs" / "submission_log.jsonl"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_state():
    editors = load_json(EDITORS_PATH)
    cursor = load_json(CURSOR_PATH)
    items = editors["editors"]
    if not items:
        raise SystemExit("No editors in editor library.")
    index = int(cursor.get("current_index", 0)) % len(items)
    return editors, cursor, items, index


def cmd_next(_args):
    editors, cursor, items, index = load_state()
    editor = items[index]
    result = {
        "platform": editors.get("platform"),
        "source": editors.get("source"),
        "queue_index": index,
        "queue_size": len(items),
        "cursor": cursor,
        "editor": editor,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_advance(args):
    editors, cursor, items, index = load_state()
    editor = items[index]
    now = datetime.now(timezone.utc).astimezone().isoformat()
    record = {
        "timestamp": now,
        "platform": editors.get("platform"),
        "editor": editor["name"],
        "email": editor["email"],
        "submission_type": args.submission_type or "",
        "target_book": args.target_book or "",
        "title": args.title,
        "project": args.project,
        "docx": args.docx,
        "status": args.status,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    cursor["current_index"] = (index + 1) % len(items)
    cursor["updated_at"] = now
    cursor["last_editor"] = editor["name"]
    cursor["last_status"] = args.status
    write_json(CURSOR_PATH, cursor)
    print(json.dumps({"logged": record, "next_index": cursor["current_index"]}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Manage the fixed Qimao editor submission queue.")
    sub = parser.add_subparsers(dest="command", required=True)

    next_parser = sub.add_parser("next", help="Print the current editor without advancing the queue.")
    next_parser.set_defaults(func=cmd_next)

    advance_parser = sub.add_parser("advance", help="Append a submission log entry and advance the queue.")
    advance_parser.add_argument("--project", required=True)
    advance_parser.add_argument("--title", required=True)
    advance_parser.add_argument("--docx", required=True)
    advance_parser.add_argument("--status", default="sent", choices=["sent", "prepared", "failed"])
    advance_parser.add_argument("--submission-type", default="")
    advance_parser.add_argument("--target-book", default="")
    advance_parser.set_defaults(func=cmd_advance)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
