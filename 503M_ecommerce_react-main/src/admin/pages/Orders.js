// src/pages/admin/order.js
import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Select,
  MenuItem,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import config from '../../config';
import { useNavigate } from 'react-router-dom';
import axios from '../../axiosConfig';
import AddOrderItem from '../../components/AddOrderItem';

const Orders = () => {
  const { server } = config;
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const [selectedOrder, setSelectedOrder] = useState(null); 

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

  const fetchData = async () => {
    try {
      const response = await axios.get(`/api/view_all_orders`);
      setOrders(response.data);
      setLoading(false);
      console.log(response.data)
    } catch (error) {
      console.error('Error fetching orders:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 10000); //10 seconds

    return () => clearInterval(intervalId);
  }, [server]);

  const handleStatusChange = async (Order_ID, newStatus) => {
    try {
      const updatedOrders = orders.map((order) =>
        order.Order_ID === Order_ID ? { ...order, Status: newStatus } : order
      );
      setOrders(updatedOrders);

      await axios.put(`/api/update_order_status/${Order_ID}`, { Status: newStatus });

      setSnackbarMessage(`Order ${Order_ID} status updated to ${newStatus}`);
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      console.error(`Failed to update status for order ${Order_ID}:`, error);
      setSnackbarMessage(`Failed to update status for order ${Order_ID}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

const generateInvoice = (order) => {
  const doc = new jsPDF();
  const issueDate = new Date().toLocaleDateString();

  doc.setFontSize(18);
  doc.text('Invoice', 105, 20, null, null, 'center');
  doc.setFontSize(12);
  doc.text(`Invoice Number: ${order.Order_ID}`, 105, 30, null, null, 'center');
  doc.text(`Date of Issue: ${issueDate}`, 105, 40, null, null, 'center');

  doc.setFontSize(10);
  doc.text('Gaming Console Store', 14, 70);
  doc.text('Bliss Street', 14, 75);
  doc.text('Hamra, Beirut', 14, 80);
  doc.text('Lebanon', 14, 85);
  doc.text('support@GSC.com', 14, 90);

  doc.text('Bill Info', 150, 70);
  doc.text(`Order ID: ${order.Order_ID}`, 150, 75);
  doc.text(`Order Date: ${order.Order_Date || 'Date not provided'}`, 150, 80);

  doc.autoTable({
    startY: 105,
    head: [['Description', 'Qty', 'Unit Price', 'Amount']],
    body: [
      [
        `Order ID: ${order.Order_ID}`,
        order.Total_Amount.toString(),
        `$${order.Total_Price.toFixed(2)}`,
        `$${(order.Total_Amount * order.Total_Price).toFixed(2)}`,
      ],
      // Add more items if needed
    ],
  });

  const finalY = doc.lastAutoTable.finalY + 10;
  doc.text(`Subtotal: $${order.Total_Price.toFixed(2)}`, 14, finalY);
  doc.text(`Total: $${order.Total_Price.toFixed(2)}`, 14, finalY + 5);
  doc.text(`Amount Due: $${order.Total_Price.toFixed(2)} USD`, 14, finalY + 10);

  doc.save(`Invoice-${order.Order_ID}.pdf`);
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

      <Typography variant="h4" gutterBottom>
        Order Management
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
          onClick={() => navigate('/returns')}
          sx={{ mb: 2 }}
        >
          Go to Returns
        </Button>
      </div>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Order ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Total Amount</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Order Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Total Price</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.length > 0 ? (
              orders.map((order) => (
                <TableRow key={order.Order_ID}>
                  <TableCell>{order.Order_ID}</TableCell>
                  <TableCell>{order.Total_Amount}</TableCell>
                  <TableCell>{order.Order_Date}</TableCell>
                  <TableCell>{order.Status}</TableCell>
                  <TableCell>${order.Total_Price.toFixed(2)}</TableCell>
                  <TableCell>
                    <Select
                      value={order.Status}
                      onChange={(e) =>
                        handleStatusChange(order.Order_ID, e.target.value)
                      }
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
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      onClick={() => generateInvoice(order)}
                    >
                      Generate Invoice
                    </Button>
                    {/* Highlighted: Button to open AddOrderItem modal */}
                    <Button
                      variant="contained"
                      color="secondary"
                      size="small"
                      onClick={() => setSelectedOrder(order)}
                      sx={{ ml: 1 }}
                    >
                      Add Item
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No orders available
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {/* Highlighted: AddOrderItem modal */}
      <AddOrderItem
        open={!!selectedOrder}
        handleClose={() => setSelectedOrder(null)}
        orderId={selectedOrder?.Order_ID}
        refreshOrders={fetchData}
      />
    </Box>
  );
};

export default Orders;
