#!/usr/bin/env python3
import os, json, yaml, re, sys
from pathlib import Path

skills_dir = Path(os.path.expanduser("~/.opencode/skills"))
output_file = Path(os.path.expanduser("~/.opencode/interactive-skills/skills.json"))

skills_data = []
errors = []

for skill_dir in sorted(skills_dir.iterdir()):
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue

    content = skill_md.read_text(encoding="utf-8", errors="replace")

    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        errors.append(f"No frontmatter: {skill_dir.name}")
        skills_data.append(
            {
                "name": skill_dir.name,
                "description": "",
                "domain": "",
                "role": "",
                "triggers": [],
            }
        )
        continue

    fm_text = fm_match.group(1)
    try:
        fm = yaml.safe_load(fm_text)
        if not fm:
            fm = {}
    except yaml.YAMLError as e:
        errors.append(f"YAML error: {skill_dir.name}: {e}")
        fm = {}

    name = fm.get("name", skill_dir.name)
    desc = fm.get("description", "")
    meta = fm.get("metadata", {}) or {}
    domain = meta.get("domain", "")
    role = meta.get("role", "")
    triggers_raw = meta.get("triggers", "")
    triggers = (
        [t.strip() for t in triggers_raw.split(",") if t.strip()]
        if isinstance(triggers_raw, str)
        else (triggers_raw or [])
    )
    related = meta.get("related-skills", "")
    related_list = (
        [r.strip() for r in related.split(",") if r.strip()]
        if isinstance(related, str)
        else (related or [])
    )

    # truncate very long descriptions
    if len(desc) > 300:
        desc = desc[:297] + "..."

    skills_data.append(
        {
            "name": name,
            "description": desc,
            "domain": domain,
            "role": role,
            "triggers": triggers,
            "related": related_list,
        }
    )

output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(
        {"skills": skills_data, "total": len(skills_data), "errors": len(errors)},
        f,
        indent=2,
        ensure_ascii=False,
    )

print(f"Total: {len(skills_data)} skills, {len(errors)} errors")
print(f"Output: {output_file}")
if errors:
    for e in errors[:5]:
        print(f"  ERR: {e}")
