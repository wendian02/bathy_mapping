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
nginx -t && systemctl restart nginx
```

> `proxy_set_header Host $host` is required so TiTiler generates tile URLs with the public IP instead of `localhost:8000`.

### 6. Run services (in tmux)

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

### 7. Access

```
http://**your-server-ip**
```

## Architecture

```
Browser
  └── port 80 → nginx
                  ├── /titiler/ → TiTiler (port 8000) → HuggingFace (COG data)
                  └── /        → Streamlit (port 8501)
```

## Update app

```bash
git pull
# restart Streamlit in tmux
```
