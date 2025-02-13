import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
} from '@mui/material';
import UpdateInventory from './UpdateInventory';

const InventoryTable = ({ data, refreshInventory }) => {
  const [openUpdateModal, setOpenUpdateModal] = useState(false);
  const [selectedInventory, setSelectedInventory] = useState([]);

  const handleOpenUpdateModal = (inventory) => {
    setSelectedInventory([inventory]); //set the selected product in the modal
    setOpenUpdateModal(true);
  };

  const handleCloseUpdateModal = () => {
    setOpenUpdateModal(false);
    setSelectedInventory([]);
  };

  return (
    <Box sx={{ mt: 2, maxWidth: '1000px' }}>
      <TableContainer component={Paper} sx={{ borderRadius: 2, boxShadow: 3 }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 'bold' }}>Product Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Stock Level</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Warehouse</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((product) => (
              <TableRow key={product.Product_ID} hover>
                <TableCell>{product.Product_Name}</TableCell>
                <TableCell>{product.Stock_Level}</TableCell>
                <TableCell>{product.Warehouse_ID}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    onClick={() => handleOpenUpdateModal(product)}
                  >
                    Update Stock
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Update Inventory Modal */}
      <UpdateInventory
        open={openUpdateModal}
        handleClose={handleCloseUpdateModal}
        inventoryData={selectedInventory}
        refreshInventory={refreshInventory}
      />
    </Box>
  );
};

export default InventoryTable;
