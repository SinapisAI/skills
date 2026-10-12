#!/usr/bin/env python3
"""Validate the distributable skill, relative references, and code examples offline."""

import ast
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/sinapisai-integration"


def validate():
    text = (SKILL / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    assert frontmatter, "Missing frontmatter"
    assert re.search(r"^name: sinapisai-integration$", frontmatter[1], re.M), "Wrong skill name"
    assert re.search(r"^description: .+", frontmatter[1], re.M), "Missing description"
    assert len(text.splitlines()) < 200, "Keep the entry point focused"

    for file in SKILL.rglob("*.md"):
        content = file.read_text()
        assert "sinapis.top" not in content, "Old development URL must not be shipped"
        assert not re.search(r"sk-[A-Za-z0-9_-]{16,}", content), "Possible secret"
        for link in re.findall(r"\]\(([^)]+)\)", content):
            if "://" not in link and not link.startswith("#"):
                target = (file.parent / link.split("#")[0]).resolve()
                assert target.is_relative_to(SKILL), f"Reference leaves skill: {link}"
                assert target.is_file(), f"Missing reference: {link}"

    examples = (SKILL / "references/examples.md").read_text()
    python_examples = re.findall(r"```python\n(.*?)\n```", examples, re.S)
    javascript_examples = re.findall(r"```javascript\n(.*?)\n```", examples, re.S)
    assert python_examples and javascript_examples, "Missing examples"
    for example in python_examples:
        ast.parse(example)
    for example in javascript_examples:
        subprocess.run(["node", "--input-type=module", "--check"], input=example, text=True, check=True)
    for file in SKILL.rglob("*.py"):
        ast.parse(file.read_text())

    metadata = (SKILL / "agents/openai.yaml").read_text()
    assert "$sinapisai-integration" in metadata, "Missing explicit invocation example"
    print("Skill metadata, relative resources, Python and JavaScript examples validated offline.")


if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, SyntaxError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
