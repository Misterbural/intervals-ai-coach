# Self-Hosting the `intervals-icu-mcp` Server on a VPS with Cloudflare Zero Trust

This guide walks through deploying the community [`intervals-icu-mcp`](https://github.com/hhopke/intervals-icu-mcp) server on an Ubuntu/Debian VPS, exposing it securely via a **Cloudflare Tunnel** (zero open HTTP ports), locking it down with **Cloudflare Access Managed OAuth**, and connecting it to Claude (desktop, mobile, and scheduled tasks).

> **Conventions used below** — replace with your own values:
> - `coachadmin` → your non-root admin Linux username
> - `YOUR_VPS_IP` → your VPS IPv4 address
> - `coach.yourdomain.com` → your public subdomain
> - `YOUR_API_KEY` → your intervals.icu API key
> - `i123456` → your intervals.icu Athlete ID
>
> Run `ssh` / `ssh-keygen` on your local machine and `sudo` commands on the VPS. Whenever editing SSH or firewall rules, **always keep your current SSH session open** and verify login in a second terminal before closing the first.

---

## 1. Prepare intervals.icu

1. **API key**: go to [intervals.icu/settings](https://intervals.icu/settings) → **Developer** → **Create API Key**. Store it in your password manager (it grants full read/write access to your account).
2. **Athlete ID**: visible in your profile URL (format `i123456`).
3. **Connect data sources directly (do NOT rely on Strava)**:
   Since November 2024, Strava API terms prevent intervals.icu from forwarding Strava-synced activities over its API—the MCP server only sees empty shells (`"Untitled"`, no metrics). Connect your watch, bike computer, and indoor apps **directly** to intervals.icu (Garmin Connect, Wahoo, Coros, Suunto, Zwift, etc.). Strava can remain connected for social features, just not as the primary data source.
4. **Wellness & RPE**: enable daily HRV, resting HR, and sleep sync from your wearable, and log post-workout RPE/feel in intervals.icu so the coach sees both objective and subjective signals.
5. **Single planner**: disable competing adaptive plans (e.g. Zwift Coach, Garmin Daily Suggested Workouts) so two plans do not conflict.

---

## 2. Provision a VPS & Create an SSH Key

Provision a small Linux VPS (1 vCPU / 1–2 GB RAM is plenty; tested on Ubuntu 24.04/26.04 LTS and Debian 12).

On your local machine (macOS, Linux, WSL, or PowerShell):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_vps_coach -C "vps-coach"
```

Set a strong passphrase, then print your **public** key (never copy the private key):

```bash
cat ~/.ssh/id_ed25519_vps_coach.pub
```

Add an SSH shortcut to `~/.ssh/config` (`chmod 600 ~/.ssh/config`):

```text
Host coach-vps
    HostName YOUR_VPS_IP
    User coachadmin
    IdentityFile ~/.ssh/id_ed25519_vps_coach
    IdentitiesOnly yes
```

Before creating `coachadmin`, connect with the default provider user (`ubuntu` or `debian`):

```bash
ssh ubuntu@coach-vps
```

Update the system and set your timezone:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo timedatectl set-timezone UTC   # e.g. Europe/Paris, America/New_York
sudo reboot
```

---

## 3. Create an Admin User & Harden SSH

Reconnect after reboot, then create your dedicated admin user:

```bash
sudo adduser coachadmin
sudo usermod -aG sudo coachadmin
sudo mkdir -p /home/coachadmin/.ssh
sudo nano /home/coachadmin/.ssh/authorized_keys
# Paste your public key, save and exit
sudo chown -R coachadmin:coachadmin /home/coachadmin/.ssh
sudo chmod 700 /home/coachadmin/.ssh
sudo chmod 600 /home/coachadmin/.ssh/authorized_keys
```

Test in a **second terminal** before touching anything else:

```bash
ssh coach-vps
sudo -v
```

Once verified, harden SSH using a `00-` priority drop-in (so cloud-init configs like `50-cloud-init.conf` cannot re-enable passwords):

```bash
sudo nano /etc/ssh/sshd_config.d/00-hardening.conf
```

```text
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers coachadmin
```

Validate, reload, and verify effective settings:

```bash
sudo sshd -t
sudo systemctl restart ssh
sudo sshd -T | grep -Ei '^(permitrootlogin|passwordauthentication|allowusers)'
```

Open a new terminal to confirm `ssh coach-vps` works, then lock `root` and remove the default cloud user (`ubuntu` or `debian`):

```bash
sudo passwd -l root
sudo deluser --remove-home ubuntu
```

---

## 4. Firewall & Automatic Security Updates

```bash
sudo apt install -y ufw unattended-upgrades
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
sudo dpkg-reconfigure -plow unattended-upgrades
```

Only port 22 (SSH) remains open inbound; Cloudflare Tunnel only makes outbound connections.

---

## 5. Install `intervals-icu-mcp` as a Hardened `systemd` Service

Create a dedicated non-login system user and install `uv`:

```bash
sudo useradd --system --create-home --home-dir /opt/coach-mcp --shell /usr/sbin/nologin mcp
sudo -u mcp -H bash -c 'curl -LsSf https://astral.sh/uv/install.sh | sh'
sudo -u mcp /opt/coach-mcp/.local/bin/uvx --version
```

Create a root-only environment file for secrets:

```bash
sudo install -m 600 -o root -g root /dev/null /etc/intervals-mcp.env
sudo nano /etc/intervals-mcp.env
```

```text
INTERVALS_ICU_API_KEY=YOUR_API_KEY
INTERVALS_ICU_ATHLETE_ID=i123456
INTERVALS_ICU_DELETE_MODE=safe
```

Create the `systemd` unit (pin a specific package version and review its changelog before upgrading):

```bash
sudo nano /etc/systemd/system/intervals-mcp.service
```

```ini
[Unit]
Description=intervals.icu MCP Server
After=network-online.target
Wants=network-online.target

[Service]
User=mcp
Group=mcp
WorkingDirectory=/opt/coach-mcp
EnvironmentFile=/etc/intervals-mcp.env
ExecStart=/opt/coach-mcp/.local/bin/uvx intervals-icu-mcp@5.7.1 --transport http --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=full

[Install]
WantedBy=multi-user.target
```

Start the service and watch the initial launch:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now intervals-mcp
sudo journalctl -u intervals-mcp -f
```

Test locally on the VPS (confirming the MCP endpoint path, usually `/mcp`):

```bash
curl -s -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}'
```

Expected: a JSON response containing `serverInfo`.

---

## 6. Configure Cloudflare Access (Before Exposing the Tunnel)

Creating the Access lock *first* ensures your MCP endpoint is never publicly reachable without authentication.

1. **Domain & Zero Trust**: add your domain to Cloudflare (Free plan; if migrating DNS from another registrar, disable DNSSEC first during transfer and enable auto-renew). Open **Zero Trust** (Free plan, up to 50 users).
2. **Identity provider**: under **Integrations → Identity providers**, add **One-time PIN** (email OTP) alongside Cloudflare account login if desired.
3. **Create the Self-Hosted Application**:
   - **Access controls → Applications → Add an application → Self-hosted**.
   - Public hostname: subdomain `coach`, domain `yourdomain.com`, path blank.
   - **Policy**: name `Me Only`, Action `Allow`, Include `Emails` → your email address only.
   - **Additional settings → Managed OAuth**:
     - Enable Managed OAuth.
     - **Disable** `Allow localhost clients` and `Allow loopback clients`.
     - Allowed redirect URIs:
       - `https://claude.ai/api/mcp/auth_callback`
       - `https://claude.com/api/mcp/auth_callback`
     - Grant session duration: set according to your security preference (e.g. `2 weeks` or longer if you later enable scheduled tasks so they do not fail silently on expiry).
     - Access token lifetime: Default (15 minutes).
   - Save.

---

## 7. Create the Cloudflare Tunnel

1. **Zero Trust → Networks → Tunnels → Create a tunnel** (Cloudflared), name `coach-vps`.
2. Select **Debian 64-bit** and run the displayed `cloudflared` install + `sudo cloudflared service install <TOKEN>` commands on your VPS.
3. Confirm the tunnel shows **Healthy** (`systemctl status cloudflared`).
4. Add a **Public Hostname** route:
   - Subdomain: `coach`, Domain: `yourdomain.com`, Path: blank
   - Service URL: `http://localhost:8000`

---

## 8. Verify the Auth Lock

From your local computer:

```bash
curl -i https://coach.yourdomain.com/mcp
curl -s https://coach.yourdomain.com/.well-known/oauth-authorization-server
```

- The first command **must** return `401 Unauthorized` with a `WWW-Authenticate` header—never your training data.
- The second command must return the Cloudflare Access OAuth discovery JSON.
- If the first command does not return `401`, stop the service immediately (`sudo systemctl stop intervals-mcp`) and review your Access application before continuing.

---

## 9. Connect to Claude

1. **Claude → Settings → Connectors → Add custom connector**.
2. Name: `intervals.icu coach`. URL: `https://coach.yourdomain.com/mcp`.
3. Click **Connect**, sign in through Cloudflare Access, and authorize.
4. **Tool permissions (important)**: set **Always allow** on read-only tools, and **Manual approval** on every tool that creates, updates, or deletes workouts, events, or settings.
5. Run read/write smoke tests in a fresh chat:
   - *"Show my activities from the last 7 days"*
   - *"What are my current CTL, ATL, and TSB?"*
   - *"Create a test workout tomorrow: 10 min at 50%"* → verify in intervals.icu, then delete it.

---

## 10. Routine Maintenance

- **Status & logs**: `systemctl status intervals-mcp cloudflared` and `sudo journalctl -u intervals-mcp -n 100`.
- **Upgrading `intervals-icu-mcp`**: read the changelog, bump `@5.7.1` in `/etc/systemd/system/intervals-mcp.service`, then `sudo systemctl daemon-reload && sudo systemctl restart intervals-mcp`.
- **Updating `cloudflared`**: run `sudo apt update && sudo apt upgrade` periodically.
- **Rotating a compromised API key**: regenerate in intervals.icu, update `/etc/intervals-mcp.env`, then `sudo systemctl restart intervals-mcp`.
- **Emergency kill switch**: `sudo systemctl stop intervals-mcp`, disable the Access app, or remove the connector in Claude.

### Fallback if Managed OAuth Fails
If your client or Cloudflare plan has issues with Managed OAuth, deploy a small Cloudflare Worker using [`workers-oauth-provider`](https://github.com/cloudflare/workers-oauth-provider) forwarding to your tunnel protected by a Cloudflare Access Service Token.

### References
- [`intervals-icu-mcp` remote deployment docs](https://github.com/hhopke/intervals-icu-mcp/blob/main/docs/remote-deployment.md)
- [Cloudflare Access Managed OAuth](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/managed-oauth/)
- [Claude Help Center: Custom Connectors](https://support.claude.com/en/articles/11175166)
