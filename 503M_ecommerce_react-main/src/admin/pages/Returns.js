// src/pages/admin/Returns.js

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Snackbar,
  Alert,
  Select,
  MenuItem,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../../axiosConfig';
import config from '../../config';

const Returns = () => {
  const { server } = config;
  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout');
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      window.location.replace('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const fetchReturns = async () => {
    try {
      const response = await axios.get('/api/view_return');
      setReturns(response.data);
    } catch (error) {
      console.error('Failed to load returned orders:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReturns();
    const intervalId = setInterval(fetchReturns, 10000); //refresh every 10 seconds

    return () => clearInterval(intervalId);
  }, [server]);

  const handleStatusChange = async (Return_ID, newStatus) => {
    try {
      //update the status locally for immediate UI feedback
      const updatedReturns = returns.map((returnOrder) =>
        returnOrder.Return_ID === Return_ID
          ? { ...returnOrder, Status: newStatus }
          : returnOrder
      );
      setReturns(updatedReturns);

      
      await axios.put(`/api/update_return/${Return_ID}`, {
        Status: newStatus,
      });

      
      setSnackbarMessage(`Return ${Return_ID} status updated to ${newStatus}`);
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      
      console.error(`Failed to update status for return ${Return_ID}:`, error);
      setSnackbarMessage(`Failed to update status for return ${Return_ID}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', marginTop: '50px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ padding: '20px' }}>
      {/* Snackbar for success/error messages */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      {/* Header Section */}
      <Typography variant="h4" gutterBottom>
        Returns Management
      </Typography>
      <div>
        <Button
          variant="contained"
          color="secondary"
          onClick={handleLogout}
          sx={{ mb: 2 }}
        >
          Logout
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/orders')}
          sx={{ mb: 2, ml: 2 }}
        >
          Go to Orders
        </Button>
      </div>

      {/* Returns Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Return ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Return Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Refund Amount</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {returns.length > 0 ? (
              returns.map((returnOrder) => (
                <TableRow key={returnOrder.Return_ID}>
                  <TableCell>{returnOrder.Return_ID}</TableCell>
                  <TableCell>{returnOrder.Return_Date}</TableCell>
                  <TableCell>{returnOrder.Status}</TableCell>
                  <TableCell>
                    ${parseFloat(returnOrder.Refund_Amount).toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Select
                      value={returnOrder.Status}
                      onChange={(e) =>
                        handleStatusChange(
                          returnOrder.Return_ID,
                          e.target.value
                        )
                      }
                      variant="outlined"
                      size="small"
                      sx={{ minWidth: 150 }}
                    >
                      <MenuItem value="Pending">Pending</MenuItem>
                      <MenuItem value="Refund Issued">Refund Issued</MenuItem>
                      <MenuItem value="Replacement Sent">
                        Replacement Sent
                      </MenuItem>
                      <MenuItem value="Return Denied">Return Denied</MenuItem>
                    </Select>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No returns available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Returns;