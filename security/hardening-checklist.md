# Security & trust hardening checklist

For Security e-drift (`blog.lugton.co.uk`). Pair with marketing content in `/site`.

## Do now (high)

- [ ] **Rotate MCP Bearer token** if it was shared in chat/config with a placeholder replaced by a real value. Treat as admin-equivalent.
- [ ] **Scope MCP**: disable write scopes you do not need; turn MCP off when not actively editing.
- [ ] **Cloudflare Access / WAF**: restrict `/wp-json/easy-mcp-ai/` to known IPs or authenticated users where possible. Note: endpoint currently advertises `Access-Control-Allow-Origin: *`.
- [ ] **Consent banner**: install/configure a UK GDPR-capable banner wired to WP Consent API + Site Kit Consent Mode (defaults already deny — ensure UI exists and ads wait for consent).
- [ ] **Publish updated Privacy Policy** from `site/content/privacy-policy.html` (page ID 251).
- [ ] **Harden subscribe** using `security/subscribe-endpoint.php` (honeypot + rate limit + double opt-in).
- [ ] **Enable HSTS** in Cloudflare (Full Strict SSL + “Always Use HTTPS” + HSTS).
- [ ] **Remove/fix Yoast Twitter** `@drift` placeholder.

## Do next (medium)

- [ ] Add footer legal links (`site/content/footer.html`).
- [ ] Trim primary nav (`site/content/nav-ia.md`).
- [ ] Reduce plugin/version leakage in HTML where easy (generator tags).
- [ ] Confirm Application Passwords / unused API keys are revoked.
- [ ] MFA on all WordPress admin users.
- [ ] Keep WordPress, Kadence, and security plugins updated.
- [ ] Ensure “what to do if scammed” pages are not crowded by AdSense units.

## MCP operational rules

1. Store token only in env (`WP_API_TOKEN`), never in git.
2. Prefer project `.cursor/mcp.json` with `${env:WP_API_TOKEN}`.
3. Log who has the token; rotate on staff/contractor changes.
4. Do not expose MCP URL in public documentation with live credentials.
5. After editing via MCP, review changes in wp-admin before promoting socially.

## Verify after deploy

```bash
# Privacy page date visible
curl -sL https://blog.lugton.co.uk/privacy-policy/ | rg -i "Last updated"

# MCP still requires auth
curl -sI https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp | rg -i "401|www-authenticate"

# HSTS present
curl -sI https://blog.lugton.co.uk/ | rg -i "strict-transport"

# Footer links present
curl -sL https://blog.lugton.co.uk/ | rg -i "privacy-policy|affiliate-disclosure"
```
