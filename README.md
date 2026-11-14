# mco-simple-python-app

A small Hello World app. The page shows a message from a SQLite database. You can change the message and save it.

```
browser -> nginx :8080 -> /api/* -> FastAPI :8000 -> SQLite (/data/app.db on volume "data")
```

- `frontend/` - the web page (HTML, CSS, JS). nginx serves it and sends `/api/*` calls to the backend.
- `backend/main.py` - the API. `GET /api/greeting` reads the message, `PUT /api/greeting` saves it.
- `.github/workflows/ci.yml` - the CI pipeline.

## Requirements
- Docker with Compose v2
- `curl` (only for the check below)

You can use Podman instead of Docker:

1. Install it: `brew install podman podman-compose`
2. Start it: `podman machine init && podman machine start`
3. Use `podman compose` wherever this README says `docker compose`.

## Starting the Application

```sh
docker compose up --build -d
```

Open http://localhost:8080. You will see "Hello World". Type a new message and click Save.

**Data:** the database is saved in a Docker volume.
- `docker compose down` stops the app. Your data stays.
- `docker compose down -v` stops the app and deletes the data. Next time it starts with "Hello World" again.

**Settings:** to change them, copy `.env.example` to `.env` and edit it.
- `DB_PATH` - where the database file is. Default: `/data/app.db`. It must be inside `/data`, or the data is lost.
- `BACKEND_URL` - where nginx sends API calls. Default: `http://mco-simple-python-app-backend:8000`.

## Check that data is saved

With the app running:

```sh
curl -X PUT localhost:8080/api/greeting -H 'Content-Type: application/json' -d '{"message":"Hi there"}'
docker compose restart mco-simple-python-app-backend
curl localhost:8080/api/greeting      # still "Hi there"
```

The message is still there after the restart, so it was read from the volume, not from memory.

I also checked:
- The data is still there after `down` and `up`.
- The data is reset after `down -v`.

## Pipeline

The pipeline runs on every pull request and every push to `main`:

1. Build both images.
2. Scan both images with Trivy. The build fails if Trivy finds a HIGH or CRITICAL problem that has a fix.

Images are not pushed to a registry yet, because nothing uses them yet.

## Choices and tradeoffs

- **FastAPI**: small, and it checks input for you.
- **SQLite**: no extra database container. But only one backend can use it, so for production it should change to Postgres.
- **Plain JavaScript, no React**: the page is very small, so React would add more work than it saves.
- **nginx in front**: the browser talks to one address only. It works like a Kubernetes ingress.
- **Only read and update**: this is what the task asked for.
- **No migration tool**: there is only one table. Add Alembic when the table needs to change.
- **Security basics**:
  - Containers do not run as root.
  - OS packages are updated during the build.
  - pip is removed from the backend image, because it caused most of the Trivy findings.
  - GitHub Actions are pinned to exact versions.



## Migration to Kubernetes

**First step:** write simple manifests and run them on one cluster.

- **Frontend**: a Deployment with 2 replicas, a Service and an Ingress. It keeps no data, so rolling updates work normally.
- **Backend**: a Deployment with 1 replica, a Service called `mco-simple-python-app-backend`, and a PVC mounted at `/data`.
  - Use `strategy: Recreate`. This stops two pods from writing to the same SQLite file at the same time.
  - Add health probes on `/healthz`.
- **Settings**: put `DB_PATH` and `BACKEND_URL` in a ConfigMap. There are no passwords yet, so no Secret is needed.
- **Images**: CI pushes the images to a registry, tagged with the commit SHA.

### Scaling the backend with Postgres

SQLite is a single file, so only one backend pod can safely write to it. To run more backend pods, move the data to Postgres:

```
Ingress -> frontend (Deployment, 2+) -> backend (Deployment, 2+) -> Postgres (StatefulSet, 1)
```

- **For local dev**, add a `postgres` service with a volume to `compose.yaml`, so local matches the cluster.

**StatefulSet or managed database?** A StatefulSet keeps everything inside the cluster and is fine for dev and test. For production, a managed database such as Amazon RDS is usually better, because backups, upgrades and failover are handled for you. Running more than one Postgres replica with failover in-cluster needs an operator such as CloudNativePG. Only take that on if you must keep the database in the cluster.

### Deployment to k8s

- **Multiple  environments** (dev, test, prod): use Kustomize or Helm.
- **Multiple clusters**: use GitOps with Argo CD.
- **Scaling **: add autoscaling (HPA) and a PodDisruptionBudget.


