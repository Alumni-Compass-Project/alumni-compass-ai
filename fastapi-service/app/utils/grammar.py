"""
Grammar checker using language_tool_python (LanguageTool – free, local).
Falls back gracefully if the JVM/package is unavailable.
"""
from __future__ import annotations

import asyncio
from typing import List

from ..schemas.cv import GrammarIssue

_tool = None


def _get_tool():
    global _tool
    if _tool is None:
        try:
            import language_tool_python
            _tool = language_tool_python.LanguageTool("en-US")
        except Exception as e:
            print(f"[GrammarChecker] LanguageTool unavailable: {e}")
            _tool = False
    return _tool if _tool else None


class GrammarChecker:
    @staticmethod
    async def check_grammar(text: str) -> List[GrammarIssue]:
        return await asyncio.get_event_loop().run_in_executor(None, GrammarChecker._check_sync, text)

    @staticmethod
    def _check_sync(text: str) -> List[GrammarIssue]:
        tool = _get_tool()
        if not tool:
            return []
        try:
            matches = tool.check(text[:5000])  # limit to avoid timeout
            issues: List[GrammarIssue] = []
            for m in matches[:20]:  # cap at 20 issues
                issues.append(GrammarIssue(
                    message     = m.message,
                    context     = m.context,
                    suggestions = list(m.replacements[:3]),
                    offset      = m.offset,
                    length      = m.errorLength,
                    rule_id     = m.ruleId,
                ))
            return issues
        except Exception as e:
            print(f"[GrammarChecker] check failed: {e}")
            return []
