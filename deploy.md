# Server Deployment Guide

## Environment

- DigitalOcean Droplet (Ubuntu)
- Data hosted on HuggingFace: `**your-hf-username**/**your-dataset**`
- App: `main_cloud.py`

## Setup Steps


### 1. Clone repo

```bash
git clone https://github.com/**your-username**/**your-repo**.git
cd bathy_mapping
```

### 2. Install Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

### 3. Create environment

```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda create -n bathy python=3.12 -y
conda activate bathy
pip install uv
uv pip install -r requirements.txt
```

### 4. Install TiTiler and nginx

```bash
pip install "titiler[full]"
apt install nginx -y
```

### 5. Configure nginx

Edit `/etc/nginx/sites-available/default`:

```nginx
server {
    listen 80;

    location /titiler/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

> `proxy_set_header Host $host` is required so TiTiler generates tile URLs with the public IP instead of `localhost:8000`.

### 6. Create Streamlit config

Create `.streamlit/config.toml` **before** starting Streamlit. Without this, the WebSocket connection will be rejected when running behind nginx:

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = false
```

### 7. Run services (in tmux)

**TiTiler** (tmux window 1):
```bash
conda activate bathy
TITILER_API_ROOT_PATH=/titiler uvicorn titiler.application.main:app --host 0.0.0.0 --port 8000
```

**Streamlit** (tmux window 2):
```bash
conda activate bathy
cd bathy_mapping
streamlit run main_cloud.py --server.port 8501
```

### 8. Configure custom domain + HTTPS

**Namecheap DNS**
Get domain. Add a new A Record pointing to `**your-server-ip**`.

**Let's Encrypt — HTTPS certificate**

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d **your-domain**
```

Certbot automatically adds SSL directives and an HTTP→HTTPS redirect. Then manually add `return 301 https://**your-domain**$request_uri;` to the HTTP server block so bare IP access also redirects to the domain.

Final `/etc/nginx/sites-available/default`:

```nginx
# HTTPS server (SSL directives managed by Certbot)
server {
    server_name **your-domain**;

    location /titiler/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/**your-domain**/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/**your-domain**/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

# HTTP server — redirect to HTTPS (if block managed by Certbot)
server {
    if ($host = **your-domain**) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name **your-domain**;
    return 301 https://**your-domain**$request_uri; # redirects bare IP access
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

**Code — update titiler endpoint**

In `main_cloud.py`, change:

```python
titiler_endpoint = "http://**your-server-ip**/titiler"
```

to:

```python
titiler_endpoint = "https://**your-domain**/titiler"
```

> HTTPS pages cannot load HTTP resources (mixed content). The endpoint must go through the domain's HTTPS reverse proxy.

### 9. Access

```
https://**your-domain**
```

## Architecture

```
Browser
  └── 443 (HTTPS) → nginx (Let's Encrypt TLS)
                      ├── /titiler/ → TiTiler (port 8000) → HuggingFace (COG data)
                      └── /        → Streamlit (port 8501)
```

## Update app

```bash
git pull
# restart Streamlit in tmux
```
