import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [status, setStatus] = useState('Checking...');
    const [faces, setFaces] = useState([]);

    useEffect(() => {
        // Check backend health
        axios.get('https://KishorKumar4120-deepguard-ai.hf.space/health')
            .then(response => {
                setStatus('✅ Connected to DeepGuard AI Backend');
                setFaces(response.data.face_engine?.known_faces || []);
            })
            .catch(error => {
                setStatus('❌ Backend not running. Start with: python run.py');
            });
    }, []);

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            padding: '20px'
        }}>
            <div style={{
                maxWidth: '1200px',
                margin: '0 auto',
                background: 'white',
                borderRadius: '20px',
                padding: '40px',
                boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}>
                <h1 style={{ color: '#667eea', marginBottom: '10px' }}>🛡️ DeepGuard AI</h1>
                <p style={{ color: '#666', marginBottom: '30px' }}>Enterprise Security Dashboard</p>
                
                <div style={{
                    background: '#f0fdf4',
                    border: '1px solid #86efac',
                    borderRadius: '10px',
                    padding: '15px',
                    marginBottom: '30px'
                }}>
                    <strong>System Status:</strong> {status}
                </div>

                <h2>Features Ready:</h2>
                <ul style={{ marginTop: '20px', lineHeight: '2' }}>
                    <li>✅ Backend Connected</li>
                    <li>✅ Face Recognition Ready</li>
                    <li>✅ Camera Management Ready</li>
                    <li>✅ Alert System Ready</li>
                </ul>

                {faces.length > 0 && (
                    <div style={{ marginTop: '30px' }}>
                        <h3>Registered Faces:</h3>
                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '10px' }}>
                            {faces.map((face, i) => (
                                <span key={i} style={{
                                    padding: '5px 15px',
                                    background: '#e0e7ff',
                                    borderRadius: '20px',
                                    color: '#4338ca'
                                }}>{face}</span>
                            ))}
                        </div>
                    </div>
                )}

                <div style={{ marginTop: '40px', padding: '20px', background: '#f3f4f6', borderRadius: '10px' }}>
                    <h3>Quick Links:</h3>
                    <p><a href="https://KishorKumar4120-deepguard-ai.hf.space/docs" target="_blank" rel="noopener noreferrer">📚 API Documentation</a></p>
                    <p><a href="https://KishorKumar4120-deepguard-ai.hf.space/health" target="_blank" rel="noopener noreferrer">💚 Health Check</a></p>
                </div>
            </div>
        </div>
    );
}

export default App;
