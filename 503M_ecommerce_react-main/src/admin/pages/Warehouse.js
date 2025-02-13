// src/admin/pages/Warehouse.js

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Paper,
  Modal,
  TextField,
  Snackbar,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import axios from '../../axiosConfig';
import config from '../../config';

const Warehouse = () => {
  const { server } = config;
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openCreateModal, setOpenCreateModal] = useState(false);
  const [openUpdateModal, setOpenUpdateModal] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState(null);
  const [managerId, setManagerId] = useState('');
  const [location, setLocation] = useState('');
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
      showSnackbar('Logout failed. Please try again.', 'error');
    }
  };

  // Fetch warehouses from backend
  const fetchWarehouses = async () => {
    try {
      const response = await axios.get('/api/warehouses');
      setWarehouses(response.data);
    } catch (error) {
      console.error('Error fetching warehouses:', error);
      showSnackbar('Failed to load warehouses.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWarehouses();
    const intervalId = setInterval(fetchWarehouses, 10000); //refresh every 10 seconds

    //cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, [server]);

  //handlers for Modals
  const handleOpenCreateModal = () => {
    setManagerId('');
    setLocation('');
    setOpenCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    setOpenCreateModal(false);
  };

  const handleOpenUpdateModal = (warehouse) => {
    setSelectedWarehouse(warehouse);
    setManagerId(warehouse.Manager_ID);
    setLocation(warehouse.Location);
    setOpenUpdateModal(true);
  };

  const handleCloseUpdateModal = () => {
    setOpenUpdateModal(false);
  };

  //snackbar Utility Function
  const showSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  //create Warehouse
  const handleCreateWarehouse = async () => {
    try {
      await axios.post('/api/create_warehouse', {
        Manager_ID: managerId,
        Location: location,
      });
      fetchWarehouses();
      handleCloseCreateModal();
      showSnackbar('Warehouse created successfully.', 'success');
    } catch (error) {
      console.error('Error creating warehouse:', error);
      showSnackbar('Failed to create warehouse.', 'error');
    }
  };

  //update Warehouse
  const handleUpdateWarehouse = async () => {
    try {
      await axios.put(`/api/update_warehouse/${selectedWarehouse.Warehouse_ID}`, {
        Manager_ID: managerId,
        Location: location,
      });
      fetchWarehouses();
      handleCloseUpdateModal();
      showSnackbar('Warehouse updated successfully.', 'success');
    } catch (error) {
      console.error('Error updating warehouse:', error);
      showSnackbar('Failed to update warehouse.', 'error');
    }
  };

  const modalStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    borderRadius: '8px',
    boxShadow: 24,
    p: 4,
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
        Warehouse Management
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
          onClick={() => navigate('/inventory')}
          sx={{ mb: 2, ml: 2 }}
        >
          Go to Inventory
        </Button>
      </div>

      {/* Create Warehouse Button */}
      <Button
        variant="contained"
        color="primary"
        onClick={handleOpenCreateModal}
        sx={{ mb: 2 }}
      >
        Create Warehouse
      </Button>

      {/* Warehouses Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Warehouse ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Manager ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {warehouses.length > 0 ? (
              warehouses.map((warehouse) => (
                <TableRow key={warehouse.Warehouse_ID}>
                  <TableCell>{warehouse.Warehouse_ID}</TableCell>
                  <TableCell>{warehouse.Manager_ID}</TableCell>
                  <TableCell>{warehouse.Location}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => handleOpenUpdateModal(warehouse)}
                      sx={{ mr: 1 }}
                    >
                      Update
                    </Button>
                    {/* You can add more action buttons here if needed */}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  No warehouses available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Warehouse Modal */}
      <Modal
        open={openCreateModal}
        onClose={handleCloseCreateModal}
        aria-labelledby="create-warehouse-modal-title"
      >
        <Box sx={modalStyle}>
          <Typography id="create-warehouse-modal-title" variant="h6" gutterBottom>
            Create Warehouse
          </Typography>
          <TextField
            label="Manager ID"
            value={managerId}
            onChange={(e) => setManagerId(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" onClick={handleCreateWarehouse}>
            Create
          </Button>
        </Box>
      </Modal>

      {/* Update Warehouse Modal */}
      <Modal
        open={openUpdateModal}
        onClose={handleCloseUpdateModal}
        aria-labelledby="update-warehouse-modal-title"
      >
        <Box sx={modalStyle}>
          <Typography id="update-warehouse-modal-title" variant="h6" gutterBottom>
            Update Warehouse
          </Typography>
          <TextField
            label="Manager ID"
            value={managerId}
            onChange={(e) => setManagerId(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <TextField
            label="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" onClick={handleUpdateWarehouse}>
            Update
          </Button>
        </Box>
      </Modal>
    </Box>
  );
};

export default Warehouse;