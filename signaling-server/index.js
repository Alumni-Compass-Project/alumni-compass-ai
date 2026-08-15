const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

app.get('/health', (_req, res) => {
  res.json({ status: 'healthy', service: 'Alumni Compass Signaling' });
});

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// rooms: { roomId: [{ socketId, userName }] }
const rooms = {};

io.on('connection', (socket) => {
  console.log('New socket connected:', socket.id);

  socket.on('join-room', ({ roomId, userId, userName }) => {
    socket.join(roomId);

    if (!rooms[roomId]) rooms[roomId] = [];
    // add user to room list
    rooms[roomId].push({ socketId: socket.id, userName });

    // send existing users to the newcomer
    const otherUsers = rooms[roomId].filter(u => u.socketId !== socket.id).map(u => ({ socketId: u.socketId, userName: u.userName }));
    socket.emit('all-users', otherUsers);

    // notify others (optional) - handled when peers signal
  });

  socket.on('sending-signal', ({ userToSignal, callerId, signal, userName }) => {
    // forward the signal to the target user
    io.to(userToSignal).emit('user-joined', { signal, callerId, userName });
  });

  socket.on('returning-signal', ({ signal, callerId }) => {
    io.to(callerId).emit('receiving-returned-signal', { signal, id: socket.id });
  });

  socket.on('send-message', (message) => {
    const { roomId } = message;
    if (roomId) {
      io.to(roomId).emit('receive-message', message);
    }
  });

  socket.on('disconnecting', () => {
    // remove from rooms
    const socketRooms = Object.keys(socket.rooms).filter(r => r !== socket.id);
    socketRooms.forEach((roomId) => {
      if (rooms[roomId]) {
        rooms[roomId] = rooms[roomId].filter(u => u.socketId !== socket.id);
        // notify remaining users
        io.to(roomId).emit('user-left', socket.id);
      }
    });
  });

  socket.on('disconnect', () => {
    console.log('Socket disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Signaling server listening on port ${PORT}`);
});
