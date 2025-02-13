// src/pages/DashboardOverview.js

import React, { useEffect, useState } from 'react';
import { Grid, Card, CardContent, Typography, CircularProgress, Alert } from '@mui/material';
import axios from '../axiosConfig';

const DashboardOverview = () => {
  const [stats, setStats] = useState({
    total_products: 0,
    orders_today: 0,
    total_customers: 0,
    pending_orders: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/dashboard');
        setStats(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError('Failed to load dashboard statistics.');
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  // Prepare stats for rendering
  const statsArray = [
    { title: "Total Products", value: stats.totalProducts },
    { title: "Orders Today", value: stats.ordersToday },
    { title: "Total Customers", value: stats.totalCustomers },
    { title: "Pending Orders", value: stats.pendingOrders }
  ];

  return (
    <Grid container spacing={3}>
      {statsArray.map((stat, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card sx={{ display: 'flex', justifyContent: 'center', padding: 2 }}>
            <CardContent>
              <Typography variant="h6" noWrap>{stat.title}</Typography>
              <Typography variant="h4" color="primary" noWrap>{stat.value}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default DashboardOverview;