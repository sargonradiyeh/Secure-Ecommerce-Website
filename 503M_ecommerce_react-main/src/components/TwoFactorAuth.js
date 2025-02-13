// TwoFactorAuth.js

import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Alert, 
  Paper, 
  CircularProgress, 
  Snackbar 
} from '@mui/material';
import { styled } from '@mui/system';
import axios from '../axiosConfig';
import MuiAlert from '@mui/material/Alert';

// Styled Components
const Container = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '100vh',
  backgroundColor: 'secondary',
  padding: '16px',
}));

const Card = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(4),
  maxWidth: 400,
  width: '100%',
  textAlign: 'center',
  boxShadow: 'rgba(0, 0, 0, 0.1) 0px 4px 12px',
}));

// Alert Component for Snackbar
const AlertComponent = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const TwoFactorAuth = ({ userId, onSuccess }) => {
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.post('/api/verify-2fa', {
        user_id: userId,
        token,
      });
      // eslint-disable-next-line
      const { token: jwtToken, message } = response.data;

      if (jwtToken) {
        localStorage.setItem('token', jwtToken);
      }

      setLoading(false);
      setSuccess(true);
      onSuccess();
    } catch (err) {
      console.error('2FA verification failed', err);
      setError(err.response?.data?.error || 'Invalid 2FA code. Please try again.');
      setLoading(false);
    }
  };

  return (
    <Container>
      <Card>
        <Typography variant="h5" gutterBottom>
          Two-Factor Authentication
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Please enter the authentication code from your authenticator app.
        </Typography>
        <Box component="form" onSubmit={handleVerify} sx={{ mt: 3 }}>
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
            sx={{ mt: 2 }}
          >
            {loading ? 'Verifying...' : 'Verify'}
          </Button>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        <Snackbar
          open={success}
          autoHideDuration={6000}
          onClose={() => setSuccess(false)}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <AlertComponent onClose={() => setSuccess(false)} severity="success" sx={{ width: '100%' }}>
            Two-Factor Authentication verified successfully!
          </AlertComponent>
        </Snackbar>
      </Card>
    </Container>
  );
};

export default TwoFactorAuth;