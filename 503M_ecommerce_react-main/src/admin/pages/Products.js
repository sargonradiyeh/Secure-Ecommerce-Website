import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Modal,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField
} from '@mui/material';
import AddProduct from '../../components/AddProduct';
import UpdateProduct from '../../components/UpdateProduct';
import RemoveProduct from '../../components/RemoveProduct';
import axios from '../../axiosConfig';
import Papa from 'papaparse';

const Products = () => {
  //State for managing products and modals
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isUpdateOpen, setIsUpdateOpen] = useState(false);
  const [isRemoveOpen, setIsRemoveOpen] = useState(false);
  const [csvFile, setCsvFile] = useState(null);

  //Handle user logout
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

  // Function to fetch products from the backend
  const fetchData = useCallback(async () => {
    try {
      const response = await axios.get('/api/view_products');
      console.log('API Response:', response.data); //log the response for debugging

      // Check if the response is an array
      if (Array.isArray(response.data)) {
        setProducts(response.data);
      } else if (response.data && Array.isArray(response.data.products)) {
        //fallback if the response has a 'products' key
        setProducts(response.data.products);
      } else {
        console.error('Unexpected API response structure:', response.data);
        setProducts([]);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]);
    }
  }, []);

  //fetch products on component mount and set up interval for refreshing
  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, 10000);
    return () => clearInterval(intervalId); 
  }, [fetchData]);

  // Modal handlers
  const openAddModal = () => setIsAddOpen(true);
  const closeAddModal = () => setIsAddOpen(false);

  const openUpdateModal = (product) => {
    setSelectedProduct(product);
    setIsUpdateOpen(true);
  };
  const closeUpdateModal = () => setIsUpdateOpen(false);

  const openRemoveModal = (product) => {
    setSelectedProduct(product);
    setIsRemoveOpen(true);
  };
  const closeRemoveModal = () => setIsRemoveOpen(false);

  // Handle CSV file selection
  const handleCsvUpload = (event) => {
    setCsvFile(event.target.files[0]);
  };

  // Process and upload CSV file
  const processCsvFile = () => {
    if (!csvFile) {
      console.error('No file selected');
      return;
    }

    Papa.parse(csvFile, {
      header: true,
      skipEmptyLines: true,
      complete: async (result) => {
        const productsData = result.data;
        try {
          const response = await axios.post('/api/bulk-add-products', { products: productsData });
          if (response.status === 200) {
            fetchData();
            console.log('Bulk upload successful');
            setCsvFile(null); //reset file input
          } else {
            console.error('Bulk upload failed');
          }
        } catch (error) {
          console.error('Error uploading CSV data:', error);
        }
      },
      error: (error) => {
        console.error('Error parsing CSV file:', error);
      }
    });
  };

  return (
    <Box sx={{ padding: '20px', marginLeft: '250px', }}>
      <Typography variant="h4" gutterBottom>Product Management</Typography>

      {/* Logout Button */}
      <div>
        <Button 
          variant="contained" 
          color="secondary" 
          onClick={handleLogout}
          sx={{ mb: 2 }}
        >
          Logout
        </Button>
      </div>

      {/* Add Product Button */}
      <Button variant="contained" onClick={openAddModal} sx={{ mb: 3 }}>Add Product</Button>

      {/* Bulk Upload Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>Bulk Upload Products</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <TextField
            type="file"
            inputProps={{ accept: ".csv" }}
            onChange={handleCsvUpload}
          />
          <Button variant="contained" onClick={processCsvFile} disabled={!csvFile}>
            Upload CSV
          </Button>
        </Box>
      </Box>

      {/* Products Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Product ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Product Name</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Description</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Price</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Discount (%)</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Image</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Listed</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Category ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Subcategory ID</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {products.length > 0 ? (
              products.map((product) => (
                <TableRow key={product.Product_ID}>
                  <TableCell>{product.Product_ID}</TableCell>
                  <TableCell>{product.Name}</TableCell>
                  <TableCell>{product.Description}</TableCell>
                  <TableCell>${product.Price.toFixed(2)}</TableCell>
                  <TableCell>{product.Discount_Percentage || 0}%</TableCell>
                  <TableCell>
                    {product.ImageURL ? (
                      <img src={product.ImageURL} alt={product.Name} width="50" height="50" />
                    ) : (
                      'No Image'
                    )}
                  </TableCell>
                  <TableCell>{product.Listed ? 'Yes' : 'No'}</TableCell>
                  <TableCell>{product.Category_ID || 'N/A'}</TableCell>
                  <TableCell>{product.SubCategory_ID || 'N/A'}</TableCell>
                  <TableCell>
                    <Button 
                      onClick={() => openUpdateModal(product)} 
                      variant="outlined" 
                      sx={{ mr: 1 }}
                    >
                      Edit
                    </Button>
                    <Button 
                      onClick={() => openRemoveModal(product)} 
                      variant="outlined" 
                      color="error"
                    >
                      Remove
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={10} align="center">
                  No products available.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Product Modal */}
      <Modal open={isAddOpen} onClose={closeAddModal}>
        <Box sx={{ maxWidth: 500, mx: 'auto', p: 4, bgcolor: 'background.paper', mt: 8 }}>
          <AddProduct onClose={closeAddModal} onAdd={fetchData} />
        </Box>
      </Modal>

      {/* Update Product Modal */}
      <Modal open={isUpdateOpen} onClose={closeUpdateModal}>
        <Box sx={{ maxWidth: 500, mx: 'auto', p: 4, bgcolor: 'background.paper', mt: 8 }}>
          <UpdateProduct product={selectedProduct} onClose={closeUpdateModal} onUpdate={fetchData} />
        </Box>
      </Modal>

      {/* Remove Product Modal */}
      <Modal open={isRemoveOpen} onClose={closeRemoveModal}>
        <Box sx={{ maxWidth: 500, mx: 'auto', p: 4, bgcolor: 'background.paper', mt: 8 }}>
          <RemoveProduct product={selectedProduct} onClose={closeRemoveModal} onRemove={fetchData} />
        </Box>
      </Modal>
    </Box>
  );
};

export default Products;