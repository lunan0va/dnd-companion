import React, { useState } from 'react';
import { loginUser } from '../services/api';
import './LoginPage.css';

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const data = await loginUser({ username, password });
      localStorage.setItem('access_token', data.access_token);
      onLogin();
    } catch (err) {
      setError('Login fehlgeschlagen! Bitte überprüfe deine Zugangsdaten.');
    }
  };

  return (
    <div className="row justify-content-center">
      <div className="login-container col-md-6">
        <h2 className="login-title mb-4">Login</h2>
        {error && <div className="alert alert-danger">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="username" className="form-label">Benutzername</label>
            <input
              type="text"
              className="form-control"
              id="username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">Passwort</label>
            <input
              type="password"
              className="form-control"
              id="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary w-100">Login</button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;