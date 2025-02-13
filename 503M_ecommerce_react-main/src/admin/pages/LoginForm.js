import React, { useState } from 'react';
import axios from '../../axiosConfig';
import TwoFactorAuth from '../../components/TwoFactorAuth';
import TwoFactorSetup from '../../components/TwoFactorSetup';
import { Link } from 'react-router-dom';
import './LoginForm.css';

const LoginForm = ({ onLoginSuccess }) => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [requires2FASetup, setRequires2FASetup] = useState(false);
  const [userId, setUserId] = useState(null);
  const [provisioningUri, setProvisioningUri] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/login', {
        username: usernameOrEmail,
        password,
      });
      if (response.data.requires_2fa_setup) {
        setRequires2FASetup(true);
        setUserId(response.data.user_id);
        setProvisioningUri(response.data.provisioning_uri);
      } else if (response.data.requires_2fa) {
        setRequires2FA(true);
        setUserId(response.data.user_id);
      } else {
        const { token } = response.data;
        localStorage.setItem('token', token);
        onLoginSuccess();
      }
    } catch (error) {
      setError(error.response?.data?.error)
    }
  };

  const handle2FASetupSuccess = () => {
    onLoginSuccess();
  };

  const handle2FASuccess = () => {
    onLoginSuccess();
  };

  if (requires2FASetup) {
    return (
      <TwoFactorSetup
        userId={userId}
        provisioningUri={provisioningUri}
        onSuccess={handle2FASetupSuccess}
      />
    );
  }

  if (requires2FA) {
    return <TwoFactorAuth userId={userId} onSuccess={handle2FASuccess} />;
  }

  return (
<div className="login-container">
      <div className="login-card">
        <h1>Login</h1><br></br>
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label htmlFor="usernameOrEmail">Username or Email</label>
            <input
              type="text"
              id="usernameOrEmail"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button">
            Login
          </button>
        </form>
        <div className="reset-password-link"><br></br>
          <Link to="/password-reset">Forgot Password?</Link>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;

