# 🛡️ FIDO2 + WebAuthn Passkeys with Server-Triggered Custom Extension Server (POC)

![CI for Backend Services](https://github.com/nithyanatarajan/webauthn-custom-extension/actions/workflows/backend.yml/badge.svg)
![CI for Frontend Services](https://github.com/nithyanatarajan/webauthn-custom-extension/actions/workflows/frontend.yml/badge.svg)

This proof-of-concept demonstrates a **standards-compliant** passkey-based authentication flow using **FIDO2/WebAuthn**,
integrated with a **server-triggered custom extension server** to collect additional client-side data as part of the
registration and authentication ceremonies.

The **custom extension step** is initiated by the **Relying Party (RP) server** during `/register/begin` or
`/authenticate/begin` and includes:

* The **URL** of the custom extension server
* The **required data fields** to collect

The browser calls this extension server **before** invoking `navigator.credentials.create()` or
`navigator.credentials.get()`.
If the extension step fails, the WebAuthn flow is aborted.
On `/complete`, the RP verifies with the extension server before finalizing the ceremony.

---

## ✅ Key Features

* Standards-compliant WebAuthn flows for registration and authentication
* **Server-driven custom extension** for analytics or business validation
* Stateless challenge handling with signed payloads
* Clear separation between authentication logic (RP) and business logic (Extension Server)
* Works with real or virtual authenticators in modern browsers

---

## 🧩 Architectural Principles

* **Server-Driven**: RP embeds extension details (URL + required fields) in `/begin` responses
* **Stateless**: No backend sessions — validation is based on signed challenges or tokens
* **Isolated Concerns**: RP verifies WebAuthn responses; extension server validates custom data
* **FIDO2/WebAuthn Compliance**: No misuse of `extensions` API — data exchange is handled outside WebAuthn

---

## 🧱 Components

### 1. `passkey_web` (Web Client)

* Calls `/register/begin` or `/authenticate/begin` on RP
* Reads extension metadata (`url`, `data`) from RP’s response
* Calls the extension server before invoking WebAuthn API
* Aborts ceremony if extension call fails
* Sends attestation/assertion to RP on success

### 2. `passkey_server` (Relying Party)

* Generates WebAuthn `publicKeyCredentialOptions` for registration/authentication
* Embeds extension instructions in these options
* Verifies attestation/assertion responses
* Confirms with extension server during `/complete`

### 3. `extension_server` (Custom Extension Server)

* Receives client-submitted data before WebAuthn ceremony
* Validates fields against business rules
* Optionally issues signed challenges for further verification
* Responds to RP verification callbacks

---

## 🧾 Flow Summary

### Registration

1. Client → RP: `/register/begin` with username
2. RP → Client: WebAuthn options + extension instructions (`url`, `data`)
3. Client → Extension Server: POST required data to `/extensions/register`
4. Extension Server → Client: success/fail
5. If success → Client calls `navigator.credentials.create()`
6. Client → RP: `/register/complete` with attestation
7. RP → Extension Server: `/extensions/register/verify` to confirm data
8. RP verifies attestation and extension verification before success

### Authentication

1. Client → RP: `/authenticate/begin` with username
2. RP → Client: WebAuthn options + extension instructions (`url`, `data`)
3. Client → Extension Server: POST required data to `/extensions/authenticate`
4. Extension Server → Client: success/fail
5. If success → Client calls `navigator.credentials.get()`
6. Client → RP: `/authenticate/complete` with assertion
7. RP → Extension Server: `/extensions/authenticate/verify` to confirm data
8. RP verifies assertion and extension verification before success

---

## 📜 Detailed User Flow

### Registration

1. **Client → RP**: `POST /register/begin`
   **Body:** `{ "username": "<email>" }`

2. **RP → Client**: WebAuthn options **+** `customExtensions`

   ```json
   {
     "publicKey": {
       "...": "...",
       "customExtensions": {
         "url": "https://localhost:9001/extensions/register",
         "data": {
           "ip": "optional",
           "location": "optional"
         }
       }
     }
   }
   ```

3. **Client → Extension Server**: `POST /extensions/register`
   **Body (example):**

   ```json
   {
     "username": "<email>",
     "data": {
       "ip": "<client-ip-or-derived>",
       "location": "<geo-or-browser-hint>"
     }
   }
   ```

4. **Extension Server → Client**: success/fail
   **Response (example):** `{ "status": "ok" }` or `{ "status": "error", "reason": "..." }`

5. **If success** → **Client** calls `navigator.credentials.create({ publicKey })`

6. **Client → RP**: `POST /register/complete`
   **Body:** `{ "username": "<email>", "credential": { ...attestation payload... } }`

7. **RP → Extension Server**: `POST /extensions/register/verify`
   **Body (example):**

   ```json
   { "username": "<email>" }
   ```

   **Extension Server → RP:** `{ "status": "ok" }`
   **RP:** verify attestation **and** extension check → success.

---

### Authentication

1. **Client → RP**: `POST /authenticate/begin`
   **Body:** `{ "username": "<email>" }`

2. **RP → Client**: WebAuthn options **+** `customExtensions`

   ```json
   {
     "publicKey": {
       "...": "...",
       "customExtensions": {
         "url": "https://localhost:9001/extensions/authenticate",
         "data": {
           "ip": "required",
           "location": "required",
           "device": "optional"
         }
       }
     }
   }
   ```

3. **Client → Extension Server**: `POST /extensions/authenticate`
   **Body (example):**

   ```json
   {
     "username": "<email>",
     "data": {
       "ip": "<client-ip-or-derived>",
       "location": "<geo-or-browser-hint>",
       "device": "<ua-or-hardware-hint>"
     }
   }
   ```

4. **Extension Server → Client**: success/fail
   **Response:** `{ "status": "ok" }` or error

5. **If success** → **Client** calls `navigator.credentials.get({ publicKey })`

6. **Client → RP**: `POST /authenticate/complete`
   **Body:** `{ "username": "<email>", "credential": { ...assertion payload... } }`

7. **RP → Extension Server**: `POST /extensions/authenticate/verify`
   **Body:** `{ "username": "<email>" }`
   **Extension Server → RP:** `{ "status": "ok" }`
   **RP:** verify assertion **and** extension check → success.

---

## 📦 Project Structure

```bash
webauthn-custom-extension/
├── backend/                     # Backend services (RP server, extension server)
│   ├── pyproject.toml                 # Root-level lint/test config for Python (optional)
│   ├── uv.lock                        # uv lockfile for Python dependencies
│   ├── apps/
│   │   ├── extension_server/          # Custom extension server (FastAPI, pyproject.toml)
│   │   │   └─── src/
│   │   │       ├── .env.example
│   │   │       ├── config.py
│   │   │       ├── main.py
│   │   │       ├── handlers/
│   │   │       └── services/
│   │   └── passkey_server/            # RP server (FastAPI, pyproject.toml)
│   │       └─── src/
│   │           ├── .env.example
│   │           ├── config.py
│   │           ├── main.py
│   │           ├── handlers/
│   │           └── services/
│   └── tests/
│       ├── extension_server/
│       └── passkey_server/
│
├── frontend/                     # Frontend
│   └── passkey_web/               # Web frontend (Vite + Vanilla JS)
│       ├── public/
│       ├── src/
│       ├── .env.example
│       ├── .prettierrc.json
│       ├── eslint.config.js
│       ├── index.html
│       ├── package.json
│       ├── package-lock.json
│       ├── setupTests.js
│       ├── style.css
│       └── vitest.config.js
│
├── diagrams/                      # sequence.puml, architecture.puml, etc.
│
├── docs/                          # Overview.md, API.md, etc.
│
├── scripts/                       # Local dev scripts (start-all.sh, lint-all.sh, etc.)
│
├── .github/                       # GitHub Actions workflows
│   └── workflows/
│       ├── backend.yml            # Backend CI workflow
│       └── frontend.yml           # Frontend CI workflow
│
├── taskfile.yml                   # Taskfile for managing tasks (install, dev, lint, etc.)
│
├── .gitignore                     # Git ignore rules
│
└── README.md                      # Project overview and setup instructions
```

---

## 🚀 Getting Started

**Requirements:** Python 3.12+, Node.js, [`uv`](https://github.com/astral-sh/uv)

1️⃣ Install dependencies:

```bash
task install
```

2️⃣ Start all services:

```bash
task dev
```

* RP Server: [http://localhost:8000](http://localhost:8000)
* Extension Server: [http://localhost:9000](http://localhost:9000)
* Web Client: [http://localhost:5173](http://localhost:5173)

3️⃣ Test using Chrome DevTools → WebAuthn Panel

---

## ⚠️ Limitations

* Extension step is mandatory; failure aborts the ceremony
* No persistent storage — in-memory only (POC)
* Works only in browsers with native WebAuthn support

---

## 📚 References

* [WebAuthn Spec (W3C)](https://www.w3.org/TR/webauthn-3/)
* [MDN: WebAuthn Extensions](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions)
* [FIDO2: Server Guidance](https://developers.google.com/identity/passkeys/developer-guides/server-introduction)
