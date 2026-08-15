# Alumni Compass — AI & Systems (S3)

This repository contains the AI service, WebRTC video component, and signaling server for Alumni Compass.

## Structure

```
fastapi-service/     FastAPI AI service (recommendations + ATS + grammar)
webrtc-component/    Drop-in React VideoRoom component for S2
signaling-server/    Socket.io signaling server for WebRTC
docs/                API contract, integration guide, demo scenarios
```

## Quick start

### 1. FastAPI AI Service

```bash
cd fastapi-service
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 2. Signaling Server

```bash
cd signaling-server
npm install
npm start
```

### 3. WebRTC component

Install dependencies in the frontend repo:

```bash
npm install simple-peer socket.io-client prop-types
```

Copy `webrtc-component/VideoRoom.jsx` into the React app and set:

```env
REACT_APP_SIGNALING_URL=http://localhost:5000
```

## Team integration

| Student | Receives from S3 |
|---------|------------------|
| S1 Laravel | `POST /api/v1/recommend`, `POST /api/v1/cv/analyze` |
| S2 Frontend | `VideoRoom.jsx` |
| S5 UI/UX | ATS response shape from `/api/v1/cv/analyze` |

## Documentation

- [API Contract](docs/API_contract.md)
- [Laravel Integration Guide](docs/integration_guide.md)
- [Demo Scenarios](docs/DEMO_SCENARIOS.md)
- [VideoRoom README](docs/VideoRoom_README.md)

## Tests

```bash
cd fastapi-service
pytest tests/ -v
```

## Deployment

- **FastAPI:** Railway (`fastapi-service/Dockerfile`, health check `/health`)
- **Signaling:** deploy `signaling-server/` as a Node service on Railway or similar

Use the same PostgreSQL database as Laravel for live mentor recommendations.
