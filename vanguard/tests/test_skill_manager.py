import os
import sys


sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "services",
        "skill-manager",
    ),
)

from skill_manager import SkillManager, required_skill_ids


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_registry_contains_required_10_skills():
    assert len(list(required_skill_ids())) == 10


def test_registry_validation_finds_no_missing_files():
    manager = SkillManager(_repo_root())
    valid, missing = manager.validate_registry()
    assert valid is True
    assert missing == []


def test_list_core_toolkit_skills_count():
    manager = SkillManager(_repo_root())
    core = manager.list_skills(category="core-toolkit")
    assert len(core) == 7


def test_list_power_user_skills_count():
    manager = SkillManager(_repo_root())
    power = manager.list_skills(category="power-user")
    assert len(power) == 3


def test_read_skill_markdown_returns_content():
    manager = SkillManager(_repo_root())
    content = manager.read_skill_markdown("docx")
    assert content is not None
    assert "# docx" in content


def test_unknown_skill_returns_none():
    manager = SkillManager(_repo_root())
    assert manager.get_skill("unknown-skill") is None
    assert manager.read_skill_markdown("unknown-skill") is None
