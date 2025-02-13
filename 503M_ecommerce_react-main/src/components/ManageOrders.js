// src/components/ManageOrders.js
import React from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Select, MenuItem } from '@mui/material';
import jsPDF from 'jspdf';
import 'jspdf-autotable';


const ManageOrders = ({ orders, onStatusChange }) => {
  const generateInvoice = (order) => {
    const doc = new jsPDF();
    const issueDate = new Date().toLocaleDateString();

    // Invoice Header
    doc.setFontSize(18);
    doc.text('Invoice', 105, 20, null, null, 'center');
    doc.setFontSize(12);
    doc.text(`Invoice number: ${order.order_id}`, 105, 30, null, null, 'center');
    doc.text(`Date of issue: ${issueDate}`, 105, 40, null, null, 'center');

    doc.setFontSize(10);
    doc.text('Gaming Console Store', 14, 70);
    doc.text('Bliss Street', 14, 75);
    doc.text('Hamra, Beirut', 14, 85);
    doc.text('Lebanon', 14, 90);
    doc.text('support@GSC.com', 14, 95);

    doc.text('Bill to', 150, 70);
    doc.text(order.customer_name, 150, 75);
    doc.text(order.address || 'Address not provided', 150, 80); 
    doc.text(`${order.city || ''}, ${order.postal_code || ''}`, 150, 85);
    doc.text(order.country || 'Country not provided', 150, 90);
    doc.text(order.email || 'Email not provided', 150, 95);

    doc.autoTable({
      startY: 105,
      head: [['Description', 'Qty', 'Unit price', 'Amount']],
      body: [
        [order.product_name, order.quantity, `$${order.total_price.toFixed(2)}`, `$${(order.quantity * order.total_price).toFixed(2)}`],
        ['Tax', '1', '$0.00', '$0.00'],
      ],
    });

    const finalY = doc.lastAutoTable.finalY + 10;
    doc.text(`Subtotal: $${order.total_price.toFixed(2)}`, 14, finalY);
    doc.text(`Total: $${order.total_price.toFixed(2)}`, 14, finalY + 5);
    doc.text(`Amount due: $${order.total_price.toFixed(2)} USD`, 14, finalY + 10);

    //Save the PDF
    doc.save(`Invoice-${order.order_id}.pdf`);
  };

  return (
    <Box sx={{ padding: '20px', marginLeft: '250px' }}> {/* Fixed position for consistent alignment */}
    <Typography variant="h4" gutterBottom>Order Management</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Customer Name</TableCell>
              <TableCell>Product</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Total Price</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow key={order.order_id}>
                <TableCell>{order.order_id}</TableCell>
                <TableCell>{order.customer_name}</TableCell>
                <TableCell>{order.product_name}</TableCell>
                <TableCell>{order.quantity}</TableCell>
                <TableCell>${order.total_price.toFixed(2)}</TableCell>
                <TableCell>
                  <Select
                    value={order.status}
                    onChange={(e) => onStatusChange(order.order_id, e.target.value)}
                    variant="outlined"
                    size="small"
                  >
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="processing">Processing</MenuItem>
                    <MenuItem value="shipped">Shipped</MenuItem>
                    <MenuItem value="delivered">Delivered</MenuItem>
                  </Select>
                </TableCell>
                <TableCell>
                  <Button variant="contained" color="primary" size="small" onClick={() => generateInvoice(order)}>
                    Generate Invoice
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ManageOrders;
