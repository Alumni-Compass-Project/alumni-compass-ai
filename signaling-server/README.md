Signaling Server for Alumni Compass WebRTC

## Quick start

```bash
cd signaling-server
npm install
npm start
```

Default port: `5000`

Health check: `GET /health`

## Environment

Copy `.env.example` to `.env` if you need a custom port:

```env
PORT=5000
```

## Frontend integration

In the React app:

```env
REACT_APP_SIGNALING_URL=http://localhost:5000
```

`VideoRoom.jsx` connects to this URL automatically.

## Supported Socket.io events

- `join-room`
- `all-users`
- `sending-signal`
- `user-joined`
- `returning-signal`
- `receiving-returned-signal`
- `user-left`
- `send-message`
- `receive-message`

## Deploy

Deploy as a Node service on Railway. Expose the public URL to S2 via `REACT_APP_SIGNALING_URL`.
