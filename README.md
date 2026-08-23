# ECOPath AI, EGT307 Group Project - Swetha, Prerana, Qian He, The handsome kind and loving man - Wei Jun

This is a README file containing the documentation covering system architecture, data pipelines, Machine Learning Service/Preprocessing, deployment settings (Docker and Kubernetes), troubleshooting history, (for you cher) execution instructions + for macos, and limitations + further improvements.


---

## 1. Project Overview and Objectives

ECOPath AI is designed to reduce carbon emissions and optimize travel times for commercial delivery fleets. Commercial freight vehicles contribute significantly to urban carbon emissions. Traditional routing engines optimize purely for distance or time, neglecting cargo payload weight, vehicle efficiency profiles, and real-time carbon costs.

This platform allows spatial routing (finding the best path via geographical routing) with Machine Learning carbon emissions inference to evaluate multiple potential routes between origin and destination points.

### Integrated Microservices Overview
The platform is built using a decoupled microservices architecture comprising four core components:

1. **Frontend UI Service**: An React web application that lets users interact: it provides route planning controls, spatial Leaflet map rendering, AI carbon prediction displays, and analytics for after the routes are generated
2. **Routing Engine Service**: A Python FastAPI service that coordinates calls between the public Open Source Routing Machine (OSRM) mapping services and internal ML models, executing multi-objective route ranking. https://project-osrm.org/
3. **ML Prediction Service**: A Python FastAPI service housing a trained Random Forest regressor (from scikit-learn) (`carbon_model.pkl`) that infers expected CO2 emissions (kg CO2e) per route.
4. **Database API & PostgreSQL Service**: A Python FastAPI REST wrapper and PostgreSQL database that is responsible for storing confirmed trip logs, route polylines, and carbon metrics. To track historical data, or storing historical.

---

## 2. Instructions to Build, Run, and Deploy

### Prerequisites
- Docker Desktop (installed and running)
- Minikube and `kubectl` (for Kubernetes deployment)
- Node.js 18+ and Python 3.10+ (for local non-containerized execution)

---
There are to ways to load the project. One via docker compose for us to test. One via Kubernetes for production.

### Docker Compose Deployment 

Docker Compose coordinates all 5 containers (PostgreSQL DB, DB REST API, ML Service, Routing Engine, Frontend UI) on a unified local network, so passing data via payloads (requests, POST, GET, etc) is possible.

#### Steps:
#####  Before composing, create an .env file and copy the contents from the .env file that we submitted to you, cher!


```bash
# 1. Clone repository and navigate to our AIAD_Project folder.
git clone https://github.com/.../AIAD_Project.git
cd AIAD_Project

# 2. Build and launch all containers by using compose
docker compose up --build
```
The application is opened at `http://localhost:3000`.

#### Docker Compose Configuration Parameters & Explanations:
- `postgres_db`: Runs image `postgres:15-alpine`.
-     Uses environment variables `POSTGRES_USER=postgres`
-     `POSTGRES_PASSWORD=password`,
-     `POSTGRES_DB=logistics_db`.
-     Mounts named volume `postgres_data` to `/var/lib/postgresql/data` to ensure database records persist across container restarts.

- `db_service`: Builds from `./green-logistics-database/Dockerfile`.
-     Exposes port `8002`. Passes environment variable `POSTGRES_HOST=postgres_db` so Python connects to the PostgreSQL container via internal DNS.

- `ml_service`: Builds from `./ML_Service/Dockerfile`.
-     Exposes port `8000`. Houses `carbon_model.pkl` and dataset references.
- `routing_service`: Builds from `./routing-engine/Dockerfile`.
-     Exposes port `8001`. Configures `ML_SERVICE_URL=http://ml_service:8000/predict` and `OSRM_BASE_URL=http://router.project-osrm.org`.

- `frontend_ui`: Builds from `./Frontend-UI/Dockerfile` using multi-stage Node/Nginx build. Binds container port `80` to host port `3000`.

---

### Kubernetes Deployment (Minikube)

#### Steps:

You should ideally be running the commands in Ubuntu with Docker Desktop (because it doesnt work cause of some connection issue between VScode and dockerdesktop.
```bash
# 1. start Minikube cluster
minikube start --driver=docker

# 2. Build images on host machine

# to ensure you can access the database, here is the secret:
kubectl create secret generic logistics-secret --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

docker build -t ml-service:v1 -f ML_Service/Dockerfile .
docker build -t routing-service:v1 ./routing-engine
docker build -t db-service:v1 ./green-logistics-database
docker build --no-cache -t frontend-ui:v2 ./Frontend-UI

# 3. Load images into Minikube local container store
minikube image load ml-service:v1
minikube image load routing-service:v1
minikube image load db-service:v1
minikube image load frontend-ui:v2

# 4. Apply Kubernetes deployment manifest
kubectl apply -f k8s-deployment.yaml


# To ensure that we, the external user, can access the thing within the kubernetes network. Open a new terminal, then run the command
# If you're running the above code in an ubuntu container (WSL). In VSCode or another terminal. type this before running the below command in the new terminal.
wsl # to ensure thaat you're in the same environemt.
# 5. Start Minikube LoadBalancer Tunnel (Required in a separate terminal tab)
minikube tunnel


```
The app is accessible from localhost 3000: `http://localhost:3000`.

#### Kubernetes Manifest Parameters (`k8s-deployment.yaml`):
- `PersistentVolumeClaim (postgres-pvc)`: Requests 2 GB storage using `accessModes: [ReadWriteOnce]`. Guarantees database state is retained if the PostgreSQL pod is deleted or recreated anytime.
- `ConfigMap (postgres-init-sql)`: Stores `init_pr.sql`. Mounts to `/docker-entrypoint-initdb.d/init_pr.sql` in `postgres-db` to automatically create the `trips` database table upon initial startup.
- `Service Type: ClusterIP`: Used for `postgres-db` (port 5432) and `ml-service` (port 8000). Keeps database and ML prediction endpoints private inside the cluster.
- `Service Type: LoadBalancer`: Used for `frontend-service` (port 3000), `routing-service` (port 8001), and `db-service` (port 8002). Enables `minikube tunnel` to map public ports directly to host `localhost`.
- `imagePullPolicy: Never` (for `frontend-ui:v2`): Instructs Kubernetes to strictly use the locally loaded image in Minikube rather than attempting to pull non-existent tags from Docker Hub.

---

## 3. Microservices Folder Structure and Component Descriptions

```text

AIAD_Project/
- Frontend-UI:
-   src
-       components (all the UI components)
-   pages
-       Dashboard.jsx (all the layouts)
-   services
-       geocoding.js (onemap)

- ML_Service
-   app.py (the fast api inference server)
-   carbon_model.pkl (the rf model)
-   processed_data.csv (the vehicle telemetry training dataset)

- routing-engine
-   route_optimiser.ppy (integrates with OSRM, speed estimator, and multi objective scorer
-   app.py (fastapi server entry point)

- green-logistics-database
-   app.py (logs the trip, if postgre is not available, saves the solution in in-memory store, meaning you can access the data by going to ..8002/api/v1/trips)
-   db.py (the postgresql psycog connector
-   db_pr.py (compatiability connection)
-   init_pr.sql (the postgresql database initialistion script


- docker-compose.yaml (container orchestration)
- k8s-deployment.yaml (kubernetes file)



```
<img width="401" height="675" alt="image" src="https://github.com/user-attachments/assets/59ddca6c-c91c-4af6-9784-9e55f436c442" />

---

## 4. Dataset Information, Parameters, and Pipeline

### Dataset (`processed_data.csv`)
The Machine Learning model was trained on historical delivery vehicle telemetry dataset parameters:
- `vehicle_type`: Vehicle category (`Truck`, `Van`, `Motorcycle`, `Car`).
- `traffic_conditions`: Congestion density (`Low`, `Normal`, `High`).
- `distance_km`: Segment travel distance in kilometers.
- `package_weight_kg`: Cargo payload weight in kilograms.
- `predicted_co2_kgco2e`: Target output label representing carbon dioxide equivalent emissions in kilograms.

---

### How the data pipeline works.

```text
[User Form Input] 
  │ (origin, destination, cargo_weight_kg, vehicle_type, priority)
  ▼
[Routing Engine: POST /api/v1/optimize-route]
  │
  ├─► Query OSRM API ──► Retrieves driving routes & spatial polyline geometries
  │
  ├─► Traffic Speed Calculation ──► Derives traffic_conditions (High, Normal, Low)
  │
  ├─► Input Normalization ──► Capitalizes vehicle_type ('truck' -> 'Truck')
  │
  └─► Query ML Service: POST /predict ──► Returns predicted_co2_kgco2e
        │
        ▼
[Multi-Objective Scoring Engine]
  │ Computes normalized cost_score = (w_co2 * norm_co2) + (w_time * norm_time)
  │ Ranks candidate routes ascending by cost_score
  ▼
[Frontend UI Render]
  │ Displays candidate route cards, predicted CO2, and Leaflet polyline paths
  ▼
[User Confirms Trip: POST /api/v1/trips]
  │ Sends selected route payload to Database Service
  ▼
[Database REST API & PostgreSQL]
  │ Inserts record into PostgreSQL `trips` table (or in-memory log if offline)
  ▼
[Analytics Dashboard]
  │ Fetches GET /api/v1/trips to render carbon savings KPIs and route history
```

---

## 5. Routing Logic and Multi-Objective Scoring Engine

### OSRM Spatial Integration
The Routing Engine formats origin and destination decimal coordinates into an OSRM API request:
`http://router.project-osrm.org/route/v1/driving/{lng1},{lat1};{lng2},{lat2}?alternatives=true&overview=full&geometries=polyline`

Note: OSRM expects `longitude,latitude` order.

### Traffic Speed Estimation
Because raw OSRM returns distance (meters) and duration (seconds) without congestion labels, the engine computes average segment speed 


speed (km/h) = distance_km / (duration_minutes / 60)


- Average speed < 25.0 km/h: Classified as `High` traffic.
- Average speed 25.0 to 50.0 km/h: Classified as `Normal` traffic.
- Average speed > 50.0 km/h: Classified as `Low` traffic.

### Multi-Objective Scoring Formula
Travel time (minutes) and CO2 emissions (kg) uses different units. To evaluate route choices fairly, we normalise them between `0.0` and `1.0` relative to the maximum route values in the option set:

norm_co2 = co2_kg / max_co2

norm_time = duration_mins / max_duration

Applying user priority weights (w_co2 + w_time = 1.0):



Applying user priority weights ($w_{\text{co2}} + w_{\text{time}} = 1.0$):
- **Green Priority**: $w_{\text{co2}} = 0.80$, $w_{\text{time}} = 0.20$
- **Fastest Priority**: $w_{\text{co2}} = 0.20$, $w_{\text{time}} = 0.80$
- **Balanced Priority**: $w_{\text{co2}} = 0.50$, $w_{\text{time}} = 0.50$

$$\text{Penalty Cost Score} = (w_{\text{co2}} \cdot \text{norm\_co2}) + (w_{\text{time}} \cdot \text{norm\_time})$$
```
Routes are sorted ascending by cost score. The lowest penalty score is designated as `recommended_route_id`.

---

## 6. Database Logic and Schema Design

### PostgreSQL Schema (`init_pr.sql`)
The PostgreSQL database keeps gthe confirmed trips using this table definition:

```sql
CREATE TABLE IF NOT EXISTS trips (
    trip_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    geometry_polyline TEXT NOT NULL,
    origin_coords VARCHAR(100) NOT NULL,
    dest_coords VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    cargo_weight_kg DECIMAL(10, 2) NOT NULL,
    route_priority VARCHAR(50) DEFAULT 'green',
    recommended_route_id VARCHAR(50) NOT NULL,
    predicted_co2_kgco2e DECIMAL(12, 4),
    distance_km DECIMAL(10, 2),
    duration_minutes DECIMAL(10, 2)
);
```

### Database Connection and Failover Resilience (`db.py` & `app.py`)
`db.py` uses `psycopg` (v3) with a `connect_timeout=3` parameter. If PostgreSQL is offline or unreachable during local isolated testing, `app.py` catches database connection exceptions and automatically redirects logs to an in-memory array (`IN_MEMORY_TRIPS`). This prevents the UI from throwing 500 errors.

---

## 7. User Interface and Local Architecture Integration

### UI Architecture
The React frontend uses Leaflet (`react-leaflet`) for spatial rendering. When a user submits locations in `RoutePlanner.jsx`:
1. `RoutePlanner` calls `POST http://localhost:8001/api/v1/optimize-route`.
2. Response data (routes, polylines, emissions, scores) is lifted into `Dashboard.jsx` state.
3. `FleetMap.jsx` decodes Google encoded polyline strings using custom decoding functions and draws colored line paths on Leaflet tiles.
4. `AIPrediction.jsx` displays candidate route cards with predicted CO2 metrics.
5. User clicks "Select & Confirm Trip", sending a payload to `POST http://localhost:8002/api/v1/trips`.
6. `Analytics.jsx` calls `GET http://localhost:8002/api/v1/trips` to recalculate total carbon saved KPIs.

---

## 8. Known Issues, Resolved Bugs, and Prevention Rules
This will contain reasons the errors we encountered and what did we do to fix them, and why it maybe happen in the first place


### 1: CORS Preflight HTTP 405 Method Not Allowed
- `route_optimiser.py` instantiated `app = FastAPI()` twice. The second instantiation wiped out the previously registered `CORSMiddleware`.
- **Our resolution**: Consolidated FastAPI app instantiation at top of file before registering any middleware or routes. That's why you see us use CORs in every part of our app.
- **What we learn to do**: Never re-instantiate `app = FastAPI()` inside a module after middleware registration.

### 2: Machine Learning error (wrongly formatted data) (`truck` vs `Truck`)
- Scikit-Learn `OneHotEncoder` was trained on capitalized strings (`Truck`, `Van`). The frontend submitted lowercase (`truck`). Unmatched strings produced zeroed feature vectors, leading to inaccurate predictions.
- **Our resolution**: Added category normalization in `ML_Service/app.py` mapping input strings (`truck` -> `Truck`, `van` -> `Van`, `car` -> `Car`, `motorcycle` -> `Motorcycle`).
- **What we learn to do**: Always validate and normalize categorical string inputs before passing them into scikit-learn transformers.

### 3: Database Service Fallback Lock (`db_pr.py` Deletion)
- `db_pr.py` was accidentally deleted during file cleanup. `app.py` failed to import `get_db_connection`, caught `ImportError`, and permanently set `get_db_connection = None`.
- **Our resolution**: Re-created `db.py` and added `db_pr.py` as an alias re-exporting `get_db_connection`.
- **What we learn to do**: Always verify import paths across microservices before deleting legacy helper files.

### 4: When files are updated, caching means it'll always look at the old files.
- Minikube's `containerd` runtime retained older compiled Docker layers for `frontend-ui:v1` because `imagePullPolicy: IfNotPresent` prevented pulling updated layers.
- **Our resolution**: Built images using `--no-cache`, updated image tag to `frontend-ui:v2`, and set `imagePullPolicy: Never` in `k8s-deployment.yaml`.
- **What we learn to do**: Increment image tags (e.g., `:v1` -> `:v2`) and use `imagePullPolicy: Never` when loading local images into Minikube.

---

## 9. Troubleshooting and macOS (Macbook) Execution Guide
Since you may be on macbook:

### macOS Execution Instructions

If executing on macOS (Apple Silicon M1/M2/M3 or Intel Mac):

#### Step 1: Start Minikube with Docker Driver
```bash
minikube start --driver=docker
# once finished
kubectl create secret generic logistics-secret --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

```

#### Step 2: Build and Load Images
On macOS, build images using host Docker Desktop:
```bash
docker build -t ml-service:v1 -f ML_Service/Dockerfile .
docker build -t routing-service:v1 ./routing-engine
docker build -t db-service:v1 ./green-logistics-database
docker build --no-cache -t frontend-ui:v2 ./Frontend-UI

minikube image load ml-service:v1
minikube image load routing-service:v1
minikube image load db-service:v1
minikube image load frontend-ui:v2
```

#### Step 3: Deploy Manifest and Start Tunnel
```bash
kubectl apply -f k8s-deployment.yaml

# On macOS, minikube tunnel will prompt for your Mac system administrator password
minikube tunnel
# at a different terminal
```
Access at `http://localhost:3000`.

---

### Common Troubleshooting Commands

#### Issue: `dial tcp 127.0.0.1:8080: connect: connection refused`
- **Cause**: Minikube cluster is stopped or `kubectl` context is unassigned.
- **Fix**: Run `minikube start` followed by `kubectl config use-context minikube`.

#### Issue: Pods stuck in `ErrImagePull` or `ImagePullBackOff`
- **Cause**: Images have not been transferred into Minikube's image store.
- **Fix**: Re-run `minikube image load <image_name>:v1`.

#### Issue: Browser API calls fail with `ERR_CONNECTION_REFUSED`
- **Cause**: `minikube tunnel` is not running in a background terminal.
- **Fix**: Open a separate terminal tab and execute `minikube tunnel`.

#### Manual Direct Port Forwarding (Emergency Bypass)
If `minikube tunnel` is blocked by operating system permission policies, manually bridge ports:
```bash
kubectl port-forward service/frontend-service 3000:80
kubectl port-forward service/routing-service 8001:8001
kubectl port-forward service/db-service 8002:8002
```

---

## 10. Identified Architectural Weaknesses and Limitations

1. **Single Public OSRM API Dependency**:
   - The routing engine relies on a public api, so in the public OSRM server experiences downtime or rate-limiting, our application fails.
   - So an enhancement is to: Host a dedicated local OSRM instance container loaded with regional OpenStreetMap (`.osm.pbf`) data.

2. **Single-Pod PostgreSQL Storage**:
   - The PostgreSQL deployment uses a single replica with `ReadWriteOnce` persistent volume claim. While persistent across pod restarts, it does not support multi-region database replication. If our database, something wrong happens to it, we do not have backups.
   - So an enhancement: Migrate to a managed PostgreSQL cluster (like a cloud-managed AWS RDS).

3. **Lack of Ingress Controller in Local Setup**:
   - Frontend and backend services rely on separate LoadBalancer ports (:3000, :8001, :8002).
   - So an enhancement: we can implement an Nginx Ingress Controller routing all traffic under a single port (`http://localhost/` for UI, `http://localhost/api/` for services).
   - However, from what we researched, without nginx, we wouldn't need to edit system files or enable custom ports. We are working on separate laptops initially.
