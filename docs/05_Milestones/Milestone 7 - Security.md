
# ✅ Milestone 7 – Security

## 🧠 Goal

Add core security features to make the NetAutoGen API safe for broader use.

This includes:
- Basic authentication or token auth
- Input sanitation (file size, YAML safety)
- Protection against misuse or accidental overload
- Optional CLI secrets masking

---

## 📦 Output

- Token-based authentication for API access
- Input validation logic (sanity limits, allowed keys)
- Configurable `config/security.yaml` (secrets, token)
- Updated API server to reject unauthorized requests
- Optional CLI prompt masking for passwords

---

## 📋 Tasks

- [ ] Add simple API token check (`Authorization: Bearer`)
- [ ] Load token from env var or `config/security.yaml`
- [ ] Reject invalid or missing token with `401`
- [ ] Sanitize uploaded YAML: no giant payloads or system calls
- [ ] Enforce max file size (e.g., 1MB)
- [ ] Optional: CLI password prompts use `getpass` (no echo)
- [ ] Add section in `README.md` about secure usage

---

## 🧪 Testing

| Scenario | Expected |
|----------|----------|
| No token → call `/api/generate` | 🔒 401 Unauthorized |
| Valid token → process as normal | ✅ 200 OK |
| Input > 1MB | ❌ Rejected with 413 |
| Malformed YAML | ❌ Graceful error |
| Password in CLI prompt | ✅ Hidden input |

---

## 🔐 Future Enhancements

- Role-based access (admin, viewer)
- Session expiration / token rotation
- JWT auth instead of static token
- HTTPS + TLS cert support
- Secrets manager integration (e.g., Vault)

---

## 🔗 Related Notes

- `[[API_Server]]`
- `[[Config_Merger]]`
- `[[Input_Spec_Validation]]`
- `[[Deployment_Guide]]`

---

## 🧭 Status

🛠 In Progress → Ready when:
- API blocks unauthorized access
- YAML input is validated safely
- CLI secrets are not exposed in logs or shell history
