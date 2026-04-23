"""
Sistema de Gerência de Skills.

Mantém um registro central das skills e valida se todos os arquivos
`skills/<skill-id>/SKILL.md` existem no repositório.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    category: str
    description: str

    @property
    def relative_file(self) -> str:
        return f"skills/{self.skill_id}/SKILL.md"


SKILL_REGISTRY: tuple[SkillDefinition, ...] = (
    SkillDefinition("docx", "core-toolkit", "Creating reports, memos, letters"),
    SkillDefinition("xlsx", "core-toolkit", "Spreadsheets, data tables, trackers"),
    SkillDefinition("pdf", "core-toolkit", "Creating, merging, splitting PDFs"),
    SkillDefinition("pdf-reading", "core-toolkit", "Extracting content from PDFs"),
    SkillDefinition("pptx", "core-toolkit", "Slide decks, presentations"),
    SkillDefinition("frontend-design", "core-toolkit", "Web UIs, components, dashboards"),
    SkillDefinition("file-reading", "core-toolkit", "Handling any uploaded file"),
    SkillDefinition("skill-creator", "power-user", "Building your own .md skill files"),
    SkillDefinition("mcp-builder", "power-user", "Building custom tool/API servers"),
    SkillDefinition("web-artifacts-builder", "power-user", "Interactive apps/workflows"),
)


class SkillManager:
    def __init__(self, repository_root: str | Path):
        self.repository_root = Path(repository_root).resolve()

    def list_skills(self, category: str | None = None) -> list[SkillDefinition]:
        if category is None:
            return list(SKILL_REGISTRY)
        return [skill for skill in SKILL_REGISTRY if skill.category == category]

    def get_skill(self, skill_id: str) -> SkillDefinition | None:
        return next((skill for skill in SKILL_REGISTRY if skill.skill_id == skill_id), None)

    def skill_file_path(self, skill_id: str) -> Path | None:
        skill = self.get_skill(skill_id)
        if skill is None:
            return None
        return self.repository_root / skill.relative_file

    def read_skill_markdown(self, skill_id: str) -> str | None:
        file_path = self.skill_file_path(skill_id)
        if file_path is None or not file_path.exists():
            return None
        return file_path.read_text(encoding="utf-8")

    def missing_skill_files(self) -> list[str]:
        missing: list[str] = []
        for skill in SKILL_REGISTRY:
            if not (self.repository_root / skill.relative_file).exists():
                missing.append(skill.relative_file)
        return missing

    def validate_registry(self) -> tuple[bool, list[str]]:
        missing = self.missing_skill_files()
        return (len(missing) == 0, missing)


def required_skill_ids() -> Iterable[str]:
    return (skill.skill_id for skill in SKILL_REGISTRY)

