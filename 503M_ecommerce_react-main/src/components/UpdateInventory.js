// src/components/UpdateInventory.js
import React, { useState } from 'react';
import {
  Modal,
  Box,
  Typography,
  TextField,
  Button,
  MenuItem,
} from '@mui/material';
import axios from '../axiosConfig';

const UpdateInventory = ({ open, handleClose, inventoryData, refreshInventory }) => {
  const [selectedProductId, setSelectedProductId] = useState('');
  const [adjustmentAmount, setAdjustmentAmount] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const adjustment = parseInt(adjustmentAmount, 10);
      if (isNaN(adjustment)) {
        alert('Please enter a valid number for adjustment amount.');
        return;
      }

    
      await axios.put(`/api/edit_inventory_by_id`, {
        Product_ID: selectedProductId,
        to_be_added: adjustmentAmount
      });
      
      handleClose();
      refreshInventory();

      
      setSelectedProductId('');
      setAdjustmentAmount('');
    } catch (error) {
      console.error('Error updating inventory:', error);
    }
  };

  const style = {
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

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="update-inventory-modal-title"
      aria-describedby="update-inventory-modal-description"
    >
      <Box sx={style} component="form" onSubmit={handleSubmit}>
        <Typography id="update-inventory-modal-title" variant="h6" component="h2" gutterBottom>
          Update Inventory
        </Typography>

        {/* Product Selection */}
        <TextField
          select
          required
          label="Product"
          value={selectedProductId}
          onChange={(e) => setSelectedProductId(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        >
          {inventoryData.map((item) => (
            <MenuItem key={item.Product_ID} value={item.Product_ID}>
              {item.Product_Name}
            </MenuItem>
          ))}
        </TextField>

        {/* Adjustment Amount */}
        <TextField
          required
          label="Adjustment Amount"
          type="number"
          value={adjustmentAmount}
          onChange={(e) => setAdjustmentAmount(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        />

        {/* Submit Button */}
        <Button variant="contained" color="primary" type="submit" fullWidth>
          Update Inventory
        </Button>
      </Box>
    </Modal>
  );
};

export default UpdateInventory;