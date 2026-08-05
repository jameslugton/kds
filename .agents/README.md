# Agent skills

Project skills installed for Cursor (see `skills-lock.json` at repo root).

## Sources

| Source | Skills |
|--------|--------|
| [mattpocock/skills](https://github.com/mattpocock/skills) | Engineering / productivity pack (`grill-me`, `tdd`, `handoff`, …) |
| [anthropics/skills](https://github.com/anthropics/skills) | `frontend-design`, `skill-creator`, `doc-coauthoring`, `mcp-builder`, `webapp-testing`, document skills (`pdf`/`docx`/`xlsx`/`pptx`) |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | `find-skills` |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `writing-guidelines`, `web-design-guidelines` |

## Restore / update

```bash
npx skills@latest experimental_install
# or refresh a source:
npx skills@latest add mattpocock/skills --skill '*' --agent cursor -y --copy
npx skills@latest add anthropics/skills --skill frontend-design --skill skill-creator --skill doc-coauthoring --skill pdf --skill docx --skill xlsx --skill pptx --skill mcp-builder --skill webapp-testing --agent cursor -y --copy
npx skills@latest add vercel-labs/skills --skill find-skills --agent cursor -y --copy
npx skills@latest add vercel-labs/agent-skills --skill writing-guidelines --skill web-design-guidelines --agent cursor -y --copy
```

Invoke examples: `/grill-me`, `/find-skills`, `/frontend-design`.
