# legal-strategist

Legal strategist powered by AI.

## Environment Settings

It is recommended to create a `.env` file inside `docker` folder with the following:

```
AUTH_TOKEN="titangroup123456"
COMPOSE_PROJECT_NAME="legal-strategist"
DEBUG_MODE = "true"
```

Where `AUTH_TOKEN` is the token used to login inside the frontend.

## Developer Setup

1. Clone repository
2. Navigate to repository folder `/docker` (for local deployment)
3. Add `.env` file with valid values for keys present in `.env.example` file
4. Run: `docker-compose build --build-arg ECR_REGISTRY=docker.io`
   - In new docker versions, run: `docker compose build --build-arg ECR_REGISTRY=docker.io`
5. Run: `docker-compose up -d`
   - In new docker versions, run: `docker compose up -d`
6. Check status by running: `docker logs legal-strategist-api` or `docker logs legal-strategist-web`
7. Open frontend webapp in: [http://localhost:3002/demand-text/generator](http://localhost:3002/demand-text/generator)
8. Open backend api docs in: [http://localhost:8100/docs](http://localhost:8100/docs)

## Development Policy

For each task, create a branch from `develop`, write the necessary code, then submit a pull request to `develop`.

Changes or pull requests to `main` branch should be restricted to repository owner, as it triggers changes in AWS prod environment.
