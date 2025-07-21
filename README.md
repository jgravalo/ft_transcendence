# 🏓 ft_transcendence

**ft_transcendence** is a real-time web platform that reimagines the classic Pong game as a modern, secure, and scalable multiplayer experience. Built as a capstone project for the Common Core, it integrates a wide range of technologies and advanced modules.

---

## 🚀 Core Technologies

- **Backend**: Node.js + Fastify (framework backend module)
- **Frontend**: TypeScript + Tailwind CSS (framework frontend module)
- **Database**: SQLite (database module)
- **Authentication**: JWT + 2FA + Google OAuth (2FA/JWT & remote auth modules)
- **User Management**: Profiles, avatars, match history, online friends (user management module)
- **Game**: Pong with live multiplayer (local & remote) and tournament system
- **Live Chat**: Direct messages, invitations, block feature (live chat module)
- **Security**: WAF with ModSecurity + HashiCorp Vault (waf/mod module)
- **Monitoring**: Prometheus + Grafana (monitoring module)
- **Accessibility**: Multi-device support, cross-browser, multilingual (🇪🇸 🇬🇧 🇫🇷)

---

## 🎮 Main Features

### 🕹 Gameplay
- Live Pong matches between remote players.
- Tournament system with matchmaking.
- Identical paddle speed for all players.
- Optional: AI opponent.

### 👥 User Management
- Secure user registration and login.
- Remote login via Google OAuth.
- Two-Factor Authentication (2FA) with OTP.
- User profiles with avatar, stats, and friends.

### 💬 Live Chat
- Private messaging between users.
- Game invitations via chat.
- Block feature and real-time notifications.

### 🌐 Accessibility & Compatibility
- Fully responsive design for desktop, tablet, and mobile.
- Compatible with modern browsers (Firefox, Chrome, Safari).
- Language switcher for English, Spanish, and French.

---

## 🛡 Security

- Password hashing and secure JWT handling.
- Client-side and server-side form validation.
- Mandatory HTTPS + WSS for WebSocket communication.
- Hardened WAF via ModSecurity.
- Secrets stored securely with HashiCorp Vault.

---

## 📈 Monitoring

- Integrated **Prometheus** and **Grafana** dashboards.
- Real-time system and user metrics.

---

## 🐳 Docker Deployment

Run the full stack using Docker:

```bash
docker compose up --build
```

## 🌍 Supported Languages
- Spanish 🇪🇸
- English 🇬🇧
- French 🇫🇷

## 🧪 Testing
- Browsers: Latest Mozilla Firefox, Chrome, Safari
- Devices: Mobile, tablet, desktop
- Security: SQL Injection / XSS protected
- Auth flow: Fully tested JWT + 2FA
