import React, { useEffect, useRef, useState, useCallback } from 'react';
import Peer from 'simple-peer';
import io from 'socket.io-client';
import PropTypes from 'prop-types';
const ICE_SERVERS = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:global.stun.twilio.com:3478' },
    ],
};

const SIGNALING_URL =
    (typeof process !== 'undefined' && process.env && process.env.REACT_APP_SIGNALING_URL) ||
    'http://localhost:5000';

/**
 * مكون VideoRoom.jsx
 * يوفر تجربة مؤتمرات فيديو كاملة باستخدام WebRTC و Socket.io
 * يدعم اللغة العربية (RTL)
 */
const VideoRoom = ({ roomId, userId, userName, userRole, onLeave, onError }) => {
    const [stream, setStream] = useState(null);
    const [peers, setPeers] = useState([]);
    const [isMuted, setIsMuted] = useState(false);
    const [isVideoOff, setIsVideoOff] = useState(false);
    const [isScreenSharing, setIsScreenSharing] = useState(false);
    const [audioOnly, setAudioOnly] = useState(false);
    const [mediaError, setMediaError] = useState(null);
    const [messages, setMessages] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');

    const socketRef = useRef();
    const userVideo = useRef();
    const peersRef = useRef([]);
    const screenTrackRef = useRef();

    useEffect(() => {
            socketRef.current = io.connect(SIGNALING_URL);

        const requestMedia = async () => {
            try {
                return await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            } catch (err) {
                if (err.name === 'NotFoundError' || err.name === 'OverconstrainedError') {
                    return await navigator.mediaDevices.getUserMedia({ audio: true });
                }
                throw err;
            }
        };

        requestMedia()
            .then((currentStream) => {
                const hasVideo = currentStream.getVideoTracks().length > 0;
                if (!hasVideo) setAudioOnly(true);
                setStream(currentStream);
                if (userVideo.current) {
                    userVideo.current.srcObject = currentStream;
                }

                socketRef.current.emit('join-room', { roomId, userId, userName });

                socketRef.current.on('all-users', (users) => {
                    const peers = [];
                    users.forEach((user) => {
                        const peer = createPeer(user.socketId, socketRef.current.id, currentStream);
                        peersRef.current.push({
                            peerId: user.socketId,
                            peer,
                            userName: user.userName
                        });
                        peers.push({
                            peerId: user.socketId,
                            peer,
                            userName: user.userName
                        });
                    });
                    setPeers(peers);
                });

                socketRef.current.on('user-joined', (payload) => {
                    const peer = addPeer(payload.signal, payload.callerId, currentStream);
                    peersRef.current.push({
                        peerId: payload.callerId,
                        peer,
                        userName: payload.userName
                    });
                    setPeers((prevPeers) => [...prevPeers, {
                        peerId: payload.callerId,
                        peer,
                        userName: payload.userName
                    }]);
                });

                socketRef.current.on('receiving-returned-signal', (payload) => {
                    const item = peersRef.current.find((p) => p.peerId === payload.id);
                    if (item) {
                        item.peer.signal(payload.signal);
                    }
                });

                socketRef.current.on('user-left', (id) => {
                    const peerObj = peersRef.current.find((p) => p.peerId === id);
                    if (peerObj) peerObj.peer.destroy();
                    const remainingPeers = peersRef.current.filter((p) => p.peerId !== id);
                    peersRef.current = remainingPeers;
                    setPeers(remainingPeers);
                });

                socketRef.current.on('receive-message', (message) => {
                    setMessages((prev) => [...prev, message]);
                });
            })
            .catch((err) => {
                console.error("خطأ في الوصول إلى الوسائط:", err);
                setMediaError(err.message || 'Media access failed');
                if (onError) onError(err);
            });

        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, [roomId, userId, userName, onError]);

    const createPeer = (userToSignal, callerId, stream) => {
        const peer = new Peer({
            initiator: true,
            trickle: false,
            stream,
            config: ICE_SERVERS,
        });

        peer.on('signal', (signal) => {
            socketRef.current.emit('sending-signal', { userToSignal, callerId, signal, userName });
        });

        return peer;
    };

    const addPeer = (incomingSignal, callerId, stream) => {
        const peer = new Peer({
            initiator: false,
            trickle: false,
            stream,
            config: ICE_SERVERS,
        });

        peer.on('signal', (signal) => {
            socketRef.current.emit('returning-signal', { signal, callerId });
        });

        peer.signal(incomingSignal);
        return peer;
    };

    const toggleMute = () => {
        if (stream) {
            stream.getAudioTracks()[0].enabled = !stream.getAudioTracks()[0].enabled;
            setIsMuted(!isMuted);
        }
    };

    const toggleVideo = () => {
        if (stream) {
            const videoTrack = stream.getVideoTracks()[0];
            if (videoTrack) {
                videoTrack.enabled = !videoTrack.enabled;
                setIsVideoOff(!videoTrack.enabled);
                setAudioOnly(!videoTrack.enabled);
            }
        }
    };

    const toggleAudioOnlyMode = () => {
        if (!stream) return;
        const nextAudioOnly = !audioOnly;
        stream.getVideoTracks().forEach((track) => {
            track.enabled = !nextAudioOnly;
        });
        setAudioOnly(nextAudioOnly);
        setIsVideoOff(nextAudioOnly);
    };

    const toggleScreenShare = async () => {
        try {
            if (!isScreenSharing) {
                const screenStream = await navigator.mediaDevices.getDisplayMedia({ cursor: true });
                const screenTrack = screenStream.getTracks()[0];
                
                peersRef.current.forEach(({ peer }) => {
                    peer.replaceTrack(
                        stream.getVideoTracks()[0],
                        screenTrack,
                        stream
                    );
                });

                screenTrack.onended = () => {
                    stopScreenShare();
                };

                screenTrackRef.current = screenTrack;
                setIsScreenSharing(true);
                if (userVideo.current) userVideo.current.srcObject = screenStream;
            } else {
                stopScreenShare();
            }
        } catch (err) {
            console.error("خطأ في مشاركة الشاشة:", err);
        }
    };

    const stopScreenShare = () => {
        if (screenTrackRef.current) {
            screenTrackRef.current.stop();
            peersRef.current.forEach(({ peer }) => {
                peer.replaceTrack(
                    screenTrackRef.current,
                    stream.getVideoTracks()[0],
                    stream
                );
            });
            setIsScreenSharing(false);
            if (userVideo.current) userVideo.current.srcObject = stream;
        }
    };

    const sendMessage = (e) => {
        e.preventDefault();
        if (currentMessage.trim()) {
            const messageData = {
                sender: userName,
                text: currentMessage,
                time: new Date().toLocaleTimeString('ar-SA')
            };
            socketRef.current.emit('send-message', { roomId, ...messageData });
            setMessages((prev) => [...prev, messageData]);
            setCurrentMessage('');
        }
    };

    const handleLeave = () => {
        if (onLeave) onLeave();
    };

    return (
        <div style={{ direction: 'rtl', fontFamily: 'Arial, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#1a1a1a', color: 'white' }}>
            {/* Header */}
            <div style={{ padding: '15px', backgroundColor: '#2d2d2d', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>غرفة الاجتماع: {roomId}</h3>
                <div>مرحباً، {userName} ({userRole === 'mentor' ? 'مرشد' : 'خريج'})</div>
            </div>
            {(audioOnly || mediaError) && (
                <div style={{ padding: '10px 20px', backgroundColor: '#b22222', color: 'white', textAlign: 'center' }}>
                    {mediaError ? `تعذر الوصول إلى الكاميرا: ${mediaError}` : 'تم تشغيل الوضع الصوتي فقط لأن الكاميرا غير متاحة.'}
                </div>
            )}

            {/* Main Content */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Video Grid */}
                <div style={{ flex: 3, padding: '20px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '15px', overflowY: 'auto' }}>
                    <div style={{ position: 'relative', borderRadius: '10px', overflow: 'hidden', backgroundColor: '#000' }}>
                        <video ref={userVideo} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        <div style={{ position: 'absolute', bottom: '10px', right: '10px', background: 'rgba(0,0,0,0.5)', padding: '5px 10px', borderRadius: '5px' }}>
                            أنت {isVideoOff && ' (الكاميرا مغلقة)'}
                        </div>
                    </div>
                    {peers.map((peerObj) => (
                        <Video key={peerObj.peerId} peer={peerObj.peer} name={peerObj.userName} />
                    ))}
                </div>

                {/* Chat Sidebar */}
                <div style={{ flex: 1, backgroundColor: '#2d2d2d', display: 'flex', flexDirection: 'column', borderRight: '1px solid #444' }}>
                    <div style={{ padding: '15px', borderBottom: '1px solid #444' }}>المحادثة</div>
                    <div style={{ flex: 1, padding: '10px', overflowY: 'auto' }}>
                        {messages.map((msg, idx) => (
                            <div key={idx} style={{ marginBottom: '10px', background: msg.sender === userName ? '#005c4b' : '#3d3d3d', padding: '8px', borderRadius: '8px' }}>
                                <div style={{ fontSize: '0.8rem', color: '#bbb' }}>{msg.sender} - {msg.time}</div>
                                <div>{msg.text}</div>
                            </div>
                        ))}
                    </div>
                    <form onSubmit={sendMessage} style={{ padding: '10px', display: 'flex', gap: '5px' }}>
                        <input 
                            type="text" 
                            value={currentMessage} 
                            onChange={(e) => setCurrentMessage(e.target.value)}
                            placeholder="اكتب رسالة..."
                            style={{ flex: 1, padding: '8px', borderRadius: '5px', border: 'none' }}
                        />
                        <button type="submit" style={{ padding: '8px 15px', borderRadius: '5px', border: 'none', backgroundColor: '#00a884', color: 'white', cursor: 'pointer' }}>إرسال</button>
                    </form>
                </div>
            </div>

            {/* Controls */}
            <div style={{ padding: '20px', backgroundColor: '#2d2d2d', display: 'flex', justifyContent: 'center', gap: '20px' }}>
                <button onClick={toggleMute} style={controlButtonStyle(isMuted ? '#ea4335' : '#444')}>
                    {isMuted ? 'إلغاء الكتم' : 'كتم الصوت'}
                </button>
                <button onClick={toggleVideo} style={controlButtonStyle(isVideoOff ? '#ea4335' : '#444')}>
                    {isVideoOff ? 'تشغيل الكاميرا' : 'إيقاف الكاميرا'}
                </button>
                <button onClick={toggleAudioOnlyMode} style={controlButtonStyle(audioOnly ? '#00a884' : '#444')}>
                    {audioOnly ? 'تشغيل الفيديو' : 'صوت فقط'}
                </button>
                <button onClick={toggleScreenShare} style={controlButtonStyle(isScreenSharing ? '#00a884' : '#444')}>
                    {isScreenSharing ? 'إيقاف المشاركة' : 'مشاركة الشاشة'}
                </button>
                <button onClick={handleLeave} style={controlButtonStyle('#ea4335')}>
                    مغادرة
                </button>
            </div>
        </div>
    );
};

const Video = ({ peer, name }) => {
    const ref = useRef();
    useEffect(() => {
        peer.on("stream", stream => {
            ref.current.srcObject = stream;
        });
    }, [peer]);

    return (
        <div style={{ position: 'relative', borderRadius: '10px', overflow: 'hidden', backgroundColor: '#000' }}>
            <video ref={ref} autoPlay playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', bottom: '10px', right: '10px', background: 'rgba(0,0,0,0.5)', padding: '5px 10px', borderRadius: '5px' }}>
                {name}
            </div>
        </div>
    );
};

const controlButtonStyle = (bgColor) => ({
    padding: '10px 20px',
    borderRadius: '25px',
    border: 'none',
    backgroundColor: bgColor,
    color: 'white',
    cursor: 'pointer',
    fontSize: '1rem',
    transition: 'background 0.3s'
});

VideoRoom.propTypes = {
    roomId: PropTypes.string.isRequired,
    userId: PropTypes.string.isRequired,
    userName: PropTypes.string.isRequired,
    userRole: PropTypes.oneOf(['mentor', 'graduate']).isRequired,
    onLeave: PropTypes.func,
    onError: PropTypes.func
};

export default VideoRoom;
