# mail-service

FastAPI mail microservice for SplitSmarter (OTP, password reset, provider failover).

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
# Optional local secrets file (not used in containers if env is set):
# mail_service_secrets.txt with KEY=VALUE lines
uvicorn src.main:app --reload --port 8083
```

Health: `GET /` or `GET /health`

## Container

```bash
docker build -t mail-service .
docker run --rm -p 8083:8083 --env-file .env mail-service
```

## CI/CD

Deployment is centralized in [`SplitSmarter/ci-cd-workflows`](https://github.com/SplitSmarter/ci-cd-workflows):

- Thin caller: [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)
- Docs: `ci-cd-workflows/deploy/README.md`

Before the first deploy:

1. Bootstrap the Droplet (`deploy/droplet/bootstrap.sh`)
2. Set org Variables `DEVELOPMENT_INSTANCE_1` + `DEVELOPMENT_APPSECRET_MAILSERVICE`
3. Set org Secrets `GHCR_USERNAME` + `GHCR_TOKEN`
4. Run **Sync Host Secrets** on `ci-cd-workflows`
5. Push this repo (or `workflow_dispatch` deploy)
