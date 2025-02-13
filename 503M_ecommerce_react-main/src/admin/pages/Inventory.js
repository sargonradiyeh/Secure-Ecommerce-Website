// src/pages/Inventory.js

import React, { useEffect, useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import InventoryTable from '../../components/InventoryTable';
import InventoryReports from '../../components/InventoryReports';
import LowStockAlert from '../../components/LowStockAlert';
import config from '../../config';
import axios from '../../axiosConfig';

const Inventory = () => {
  const { server } = config;
  const [inventoryData, setInventoryData] = useState([]);
  const [lowStockProducts, setLowStockProducts] = useState([]);
  const [turnoverData, setTurnoverData] = useState({ labels: [], values: [] });
  const [popularProductsData, setPopularProductsData] = useState({ labels: [], values: [] });
  const [demandPredictionData, setDemandPredictionData] = useState({ labels: [], values: [] });

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

  useEffect(() => {
    const fetchData = async () => {
      try {
       
        const response = await axios.get(`/api/view_inventory`);
        const data = response.data;
        console.log('Inventory Response:', data);

        //Validate that data.inventory is an array
        if (Array.isArray(data.inventory)) {
          setInventoryData(data.inventory);
          const lowStock = data.inventory.filter(item => item.Stock_Level < 10);
          setLowStockProducts(lowStock);
          console.log('Low Stock Products:', lowStock);
        } else {
          console.error('Expected an array but got:', data.inventory);
        }

        // Fetch inventory reports
        const reportResponse = await axios.get(`/api/inventory/turnover`);
        console.log(reportResponse.data)
        setTurnoverData(reportResponse.data);
        console.log(reportResponse.turnoverData)
        setPopularProductsData(reportResponse.popularProductsData);
        setDemandPredictionData(reportResponse.demandPredictionData);
        console.log(reportResponse.turnoverData)
      } catch (error) {
        console.error('Error fetching inventory data:', error);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 10000); //10 seconds

    //Cleanup interval on component unmount
    return () => clearInterval(intervalId);
  }, [server]);

  return (
    <Box sx={{ padding: '20px', marginRight: '450px', marginTop: '70px' }}>
      <Typography variant="h4" gutterBottom>Inventory Management</Typography>
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
          onClick={() => navigate('/warehouse')}
          sx={{ mb: 2 }} 
        >
          Go to Warehouses
        </Button>
      </div>

      {/* Low Stock Alert */}
      <LowStockAlert lowStockProducts={lowStockProducts} />

      {/* Inventory Table and Reports */}
      <InventoryTable data={inventoryData} />
      <InventoryReports
        turnoverData={turnoverData}
        popularProductsData={popularProductsData}
        demandPredictionData={demandPredictionData}
      />
    </Box>
  );
};

export default Inventory;