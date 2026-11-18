#!/usr/bin/env python3
"""Build ready-to-upload Claude Skill ZIP archives from skills/.

Also validates that every SKILL.md has valid YAML frontmatter, matching folder
name, and a description within Claude's 200-character limit.

Usage:
  python3 scripts/build_skills_zip.py
"""

import re
import sys
import zipfile
from pathlib import Path

DESC_LIMIT = 200
ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist" / "skills"


def validate_skill(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        raise ValueError(f"{skill_md}: missing YAML frontmatter")
    header = m.group(1)
    m_name = re.search(r'^name:\s*["\']?([^\n"\']+)["\']?\s*$', header, re.MULTILINE)
    m_desc = re.search(r'^description:\s*["\'](.*?)["\']\s*$', header, re.MULTILINE)
    if not m_name or not m_desc:
        raise ValueError(f"{skill_md}: missing name or description field")
    name = m_name.group(1).strip()
    desc = m_desc.group(1).strip()
    if name != skill_md.parent.name:
        raise ValueError(f"{skill_md}: name ({name}) does not match folder ({skill_md.parent.name})")
    if len(desc) > DESC_LIMIT:
        raise ValueError(f"{skill_md}: description too long ({len(desc)} > {DESC_LIMIT} chars)")
    return f"{name} ({len(desc)}/{DESC_LIMIT} chars)"


def main() -> int:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    folders = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    if not folders:
        print("No skills found in skills/.", file=sys.stderr)
        return 1

    for folder in folders:
        skill_md = folder / "SKILL.md"
        if not skill_md.exists():
            print(f"ERROR: {skill_md} not found", file=sys.stderr)
            return 1
        summary = validate_skill(skill_md)
        archive = DIST_DIR / f"{folder.name}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(SKILLS_DIR))
        print(f"OK: {archive.relative_to(ROOT)} — {summary}")

    print(f"\nGenerated {len(folders)} skill archives in {DIST_DIR.relative_to(ROOT)}/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
