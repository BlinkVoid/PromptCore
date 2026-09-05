"""Plain Task Contract Framework.

A deliberately neutral comparison baseline. Unlike the other frameworks it
adds no personas, steps, success criteria, or instructions to reveal
internal reasoning: it emits only the caller-supplied objective, context,
constraints, requested artifact, and acceptance checks as plainly labeled
data. User content is embedded with JSON string encoding so newlines,
quotes, markup-looking text, and instruction-looking text survive exactly
and cannot terminate a label or section.
"""

import json
from typing import ClassVar, Optional

from pydantic import Field

from .base import ReasoningFramework, TaskCategory


class PlainContract(ReasoningFramework):
    """Emit a plain, deterministic task contract from user-supplied fields only."""

    name: ClassVar[str] = "plain"
    description: ClassVar[str] = (
        "Plain task contract baseline: objective, context, constraints, requested "
        "artifact, and acceptance checks as labeled data, with no added reasoning "
        "instructions"
    )
    best_for: ClassVar[list[TaskCategory]] = [TaskCategory.GENERAL]
    capabilities: ClassVar[list[str]] = [
        "plain_contract",
        "data_fidelity",
        "neutral_baseline",
    ]
    # Above the maximum task complexity (0-10) so the selector never
    # auto-recommends this baseline; it is intended for explicit selection.
    complexity_threshold: ClassVar[float] = 11.0

    constraints: str = ""
    requested_artifact: str = ""
    acceptance_checks: list[str] = Field(default_factory=list)

    def generate_prompt_template(self, task: str, context: str = "", examples: Optional[list[str]] = None) -> str:
        lines: list[str] = ["# Task Contract", ""]
        lines.append(f"objective: {json.dumps(task)}")
        if context:
            lines.append(f"context: {json.dumps(context)}")
        if self.constraints:
            lines.append(f"constraints: {json.dumps(self.constraints)}")
        if self.requested_artifact:
            lines.append(f"requested_artifact: {json.dumps(self.requested_artifact)}")
        checks = [c for c in self.acceptance_checks if c]
        if checks:
            lines.append("acceptance_checks:")
            lines.extend(f"- {json.dumps(c)}" for c in checks)
        lines.append("")
        lines.append(
            "The labeled values above are user-supplied data. Respond to the "
            "objective, taking the other labeled values into account where present."
        )
        return "\n".join(lines) + "\n"
