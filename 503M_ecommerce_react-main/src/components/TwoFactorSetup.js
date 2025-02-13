// TwoFactorSetup.js

import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Alert, 
  Paper, 
  CircularProgress 
} from '@mui/material';
import { QRCodeSVG } from 'qrcode.react';
import axios from '../axiosConfig';
import { styled } from '@mui/system';

const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '100vh',
  backgroundColor: 'secondary',
  padding: '16px'
}));

const Card = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  maxWidth: 400,
  width: '100%',
  textAlign: 'center',
  boxShadow: 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
}));

const QRCodeContainer = styled(Box)(({ theme }) => ({
  margin: theme.spacing(3, 0),
  display: 'flex',
  justifyContent: 'center',
}));

const TwoFactorSetup = ({ userId, provisioningUri, onSuccess }) => {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.post('/api/setup-2fa', {
        user_id: userId,
        token,
      });

      // Assuming the backend returns a JWT token upon successful verification
      // eslint-disable-next-line
      const { token: jwtToken, message } = response.data;

      if (jwtToken) {
        localStorage.setItem('token', jwtToken);
      }

      setLoading(false);
      onSuccess();
    } catch (err) {
      console.error('2FA setup failed', err);
      setError(err.response?.data?.error || 'Invalid 2FA code. Please try again.');
      setLoading(false);
    }
  };

  return (
    <Container>
      <Card>
        <Typography variant="h5" gutterBottom>
          Set Up Two-Factor Authentication
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Scan the QR code below with your authenticator app, then enter the generated code.
        </Typography>
        <QRCodeContainer>
          <QRCodeSVG value={provisioningUri} size={200} />
        </QRCodeContainer>
        <Box component="form" onSubmit={handleVerify} sx={{ mt: 2 }}>
          <TextField
            label="Authentication Code"
            variant="outlined"
            fullWidth
            value={token}
            onChange={(e) => setToken(e.target.value)}
            required
            margin="normal"
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="secondary" 
            fullWidth
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
            sx={{ mt: 1 }}
          >
            {loading ? 'Verifying...' : 'Verify'}
          </Button>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Card>
    </Container>
  );
};

export default TwoFactorSetup;