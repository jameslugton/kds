# kds

Ops and content package for **Security e-drift** ([blog.lugton.co.uk](https://blog.lugton.co.uk/)).

## Cursor ↔ WordPress MCP

Project MCP config: `.cursor/mcp.json`

```bash
export WP_API_TOKEN='your-easy-mcp-ai-bearer-token'
```

Token stays in the environment — never commit it.

## Marketing & trust fixes (Jul 2026)

See **`site/APPLY.md`** for the full deploy checklist.

Quick start:

1. `python3 scripts/apply-via-mcp.py` (requires `WP_API_TOKEN`) or paste HTML from `site/content/`
2. Append `site/theme/edrift-patches.css` to the child theme
3. Rebuild nav (`site/content/nav-ia.md`) and footer (`site/content/footer.html`)
4. Work through `security/hardening-checklist.md`
