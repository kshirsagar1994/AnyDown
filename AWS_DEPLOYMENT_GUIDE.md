# AnyDown AWS Deployment Guide

This guide explains how to upload and deploy the complete AnyDown stack (Next.js Frontend, FastAPI Backend, and Nginx Reverse Proxy) to your Amazon Web Services (AWS) account.

---

## Architecture Overview

```
                      +---------------------------------------+
                      |               AWS EC2                 |
                      |  (Ubuntu 24.04 LTS / t3.small/micro)  |
                      |                                       |
User Browser -------->| Port 80 / 443 (Nginx Reverse Proxy)  |
                      |   ├── /         ──> Frontend (3000)   |
                      |   └── /api/     ──> Backend (8000)    |
                      +---------------------------------------+
```

- **Port 80/443 (Nginx)**: Acts as the single entrypoint. Routes user web requests to the Next.js frontend and `/api/...` requests to the FastAPI backend.
- **Backend**: Containerized FastAPI service with `yt-dlp`, `ffmpeg`, and Node.js.
- **Frontend**: Containerized Next.js 15 app in optimized standalone mode.
- **No CORS issues**: Frontend and backend share the same domain and IP under reverse proxy.

---

## Quick Start (Automated Deployment)

### Step 1: Install AWS CLI (if not already installed)

Open **PowerShell as Administrator** and run:

```powershell
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /qn
```

*Close and reopen your terminal after installation finishes.*

### Step 2: Configure Your AWS Credentials

Run:

```powershell
aws configure
```

Enter your details when prompted:
- **AWS Access Key ID**: `[Your Access Key]`
- **AWS Secret Access Key**: `[Your Secret Key]`
- **Default region name**: `us-east-1` (or your preferred region, e.g. `ap-south-1`, `eu-west-1`)
- **Default output format**: `json`

> **Security Note:** Never share or commit your AWS Access Keys or secrets.

---

### Step 3: Run the 1-Click Deployment Script

In the project root (`c:\Users\ajaya\OneDrive\Desktop\AnyDown`), run:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy-to-aws-ec2.ps1
```

#### What this script does automatically:
1. Authenticates with your AWS account using `aws sts get-caller-identity`.
2. Creates an EC2 Key Pair (`anydown-ec2-key.pem`) and secures file permissions.
3. Creates an EC2 Security Group (`anydown-ec2-sg`) with ports `22` (SSH), `80` (HTTP), and `443` (HTTPS) open.
4. Finds the latest official Ubuntu 24.04 LTS AMI in your selected region.
5. Launches an EC2 instance with 20 GB gp3 storage.
6. Waits for instance launch and SSH availability.
7. Packages the project bundle (excluding `node_modules` and temporary files).
8. Uploads the bundle to the instance via `scp`.
9. Runs `setup-ec2.sh` on the instance, which:
   - Configures 2GB swap space (ensures zero out-of-memory errors on micro/small instances).
   - Installs Docker & Docker Compose plugin.
   - Builds and launches all containers (`backend`, `frontend`, `nginx`).
   - Verifies API and frontend health.
10. Prints your live website URL: `http://<YOUR-EC2-PUBLIC-IP>`.

---

## Deploying to an Existing EC2 Instance

If you already launched an EC2 instance in your AWS Console, you can deploy to it with one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy-to-aws-ec2.ps1 -ExistingIp <YOUR_EC2_PUBLIC_IP> -KeyPath <PATH_TO_PEM_KEY>
```

---

## Manual Deployment (AWS Web Console Alternative)

If you prefer to launch the instance through the [AWS Management Console](https://console.aws.amazon.com/ec2):

1. **Launch an EC2 Instance**:
   - **Name**: `AnyDown-Server`
   - **AMI**: `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type`
   - **Instance Type**: `t3.small` (recommended) or `t3.micro` (free tier eligible)
   - **Key pair**: Create or select an existing `.pem` key pair
   - **Network settings**: Check **Allow SSH traffic**, **Allow HTTP traffic from the internet**, and **Allow HTTPS traffic from the internet**
   - **Storage**: `20 GiB gp3`

2. **Connect to your EC2 Instance via SSH**:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@<EC2-PUBLIC-IP>
   ```

3. **Clone or Transfer the Repository**:
   ```bash
   git clone https://github.com/kshirsagar1994/AnyDown.git
   cd AnyDown
   ```

4. **Run the Setup Script**:
   ```bash
   chmod +x setup-ec2.sh
   ./setup-ec2.sh
   ```

5. Once completed, navigate to `http://<EC2-PUBLIC-IP>` in your browser.

---

## Useful Operational Commands

### Check running containers on EC2:
```bash
sudo docker compose ps
```

### View live logs:
```bash
# All logs:
sudo docker compose logs -f

# Backend only:
sudo docker compose logs -f backend

# Frontend only:
sudo docker compose logs -f frontend

# Nginx reverse proxy:
sudo docker compose logs -f nginx
```

### Restart all services:
```bash
sudo docker compose restart
```

### Update application after code changes:
```bash
git pull
sudo docker compose up -d --build
```

---

## Setting up a Custom Domain & Free SSL (HTTPS)

Once your domain is pointing to the EC2 Public IP:

1. Install Certbot on EC2:
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   ```
2. Stop the docker Nginx container temporarily:
   ```bash
   sudo docker compose stop nginx
   ```
3. Generate the SSL certificate:
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   ```
4. Update `nginx/nginx.conf` with your certificate paths and restart Nginx:
   ```bash
   sudo docker compose start nginx
   ```

