#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import glob
import importlib.util
import json
import os
from pathlib import Path
from typing import Any


def find_workspace_root() -> Path:
    script_path = Path(__file__).resolve()
    parents = list(script_path.parents)
    for index, parent in enumerate(parents):
        if parent.name == "novel-submission-loop" and index + 3 < len(parents):
            if parents[index + 1].name == "skills" and parents[index + 2].name == ".agents":
                return parents[index + 3]
    candidates = [Path.cwd(), *parents]
    for candidate in candidates:
        if (candidate / "qq-mail-mcp" / ".env").exists():
            return candidate
    return Path.cwd()


ROOT = find_workspace_root()
DEFAULT_ENV_FILE = ROOT / "qq-mail-mcp" / ".env"
PLUGIN_GLOB = (
    Path.home()
    / ".codex"
    / "plugins"
    / "cache"
    / "personal"
    / "qq-mail"
    / "*"
    / "mcp"
    / "qq-mail-mcp"
    / "server.py"
)


def normalize_path(raw: str) -> Path:
    value = raw.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path


def resolve_attachment(raw: str, preview_path: Path) -> Path:
    value = raw.strip()
    if value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    path = Path(value)
    if path.is_absolute():
        return path

    candidates = [ROOT / path, *[parent / path for parent in preview_path.resolve().parents]]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def parse_preview(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    current_key: str | None = None
    body_lines: list[str] = []
    in_body = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("收件人"):
            fields["to"] = line.split("：", 1)[1].strip() if "：" in line else ""
            current_key = "to"
            in_body = False
            continue
        if line.startswith("主题"):
            fields["subject"] = line.split("：", 1)[1].strip() if "：" in line else ""
            current_key = "subject"
            in_body = False
            continue
        if line.startswith("附件"):
            fields["attachment"] = line.split("：", 1)[1].strip() if "：" in line else ""
            current_key = "attachment"
            in_body = False
            continue
        if line.startswith("正文"):
            current_key = None
            in_body = True
            continue
        if line.startswith("发送前确认口令"):
            in_body = False
            current_key = None
            continue
        if line == "确认发送":
            continue
        if current_key and line and not fields.get(current_key):
            fields[current_key] = line
            current_key = None
            continue
        if in_body:
            body_lines.append(raw_line.rstrip())

    body = "\n".join(body_lines).strip()
    missing = [key for key in ("to", "subject", "attachment") if not fields.get(key)]
    if missing:
        raise SystemExit(f"Mail preview missing required fields: {', '.join(missing)}")
    if not body:
        raise SystemExit("Mail preview body is empty.")

    attachment = resolve_attachment(fields["attachment"], path)
    if not attachment.exists():
        raise SystemExit(f"Attachment not found: {attachment}")

    return {
        "to": fields["to"],
        "subject": fields["subject"],
        "attachment": attachment,
        "body": body,
    }


def find_plugin_server() -> Path:
    matches = sorted(glob.glob(str(PLUGIN_GLOB)))
    if not matches:
        raise SystemExit("QQ Mail plugin server not found in personal plugin cache.")
    return Path(matches[-1])


def load_qq_mail_server(server_path: Path):
    spec = importlib.util.spec_from_file_location("qq_mail_server", server_path)
    if not spec or not spec.loader:
        raise SystemExit(f"Cannot load QQ Mail plugin server: {server_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def send(parsed: dict[str, Any]) -> dict[str, Any]:
    os.environ.setdefault("QQ_MAIL_ENV_FILE", str(DEFAULT_ENV_FILE))
    os.environ.setdefault("QQ_MAIL_IMAP_HOST", "imap.qq.com")
    os.environ.setdefault("QQ_MAIL_IMAP_PORT", "993")
    os.environ.setdefault("QQ_MAIL_SMTP_HOST", "smtp.qq.com")
    os.environ.setdefault("QQ_MAIL_SMTP_PORT", "465")

    module = load_qq_mail_server(find_plugin_server())
    module.load_env_file()
    attachment_path: Path = parsed["attachment"]
    content_base64 = base64.b64encode(attachment_path.read_bytes()).decode("ascii")
    return module.tool_send_email(
        {
            "to": parsed["to"],
            "subject": parsed["subject"],
            "body": parsed["body"],
            "attachments": [
                {
                    "filename": attachment_path.name,
                    "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "content_base64": content_base64,
                }
            ],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a prepared Qimao submission through the QQ Mail plugin.")
    parser.add_argument("--preview", required=True, help="Path to 07_mail_preview.md")
    parser.add_argument("--confirm", default="", help="Must be exactly 确认发送 to send.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without sending.")
    args = parser.parse_args()

    parsed = parse_preview(normalize_path(args.preview))
    summary = {
        "to": parsed["to"],
        "subject": parsed["subject"],
        "attachment": str(parsed["attachment"]),
        "body_chars": len(parsed["body"]),
        "plugin_server": str(find_plugin_server()),
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **summary}, ensure_ascii=False, indent=2))
        return
    if args.confirm != "确认发送":
        raise SystemExit("Refusing to send: --confirm must be exactly 确认发送.")
    result = send(parsed)
    print(json.dumps({"summary": summary, "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
