import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Checkbox, FormControlLabel } from '@mui/material';
//import config from '../config';
import axios from '../axiosConfig';

const AddProduct = ({ onClose, onAdd }) => {
  //const { server } = config;

  
  const [name, setName] = useState('');
  const [price, setPrice] = useState('');
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [listed, setListed] = useState(true);
  const [discountPercentage, setDiscountPercentage] = useState(0, 0);
  const [categoryId, setCategoryId] = useState('');
  const [subCategoryId, setSubCategoryId] = useState('');
  const [error, setError] = useState('');

  const handleAddProduct = async () => {
    // Validate input
    if (!name || !price || !categoryId || !subCategoryId) {
      setError('Name, Price, Category ID, and Subcategory ID are required.');
      return;
    }
    if (discountPercentage < 0 || discountPercentage > 100) {
      setError('Discount Percentage must be between 0 and 100.');
      return;
    }

    const newProduct = {
      Name: name,
      Price: parseFloat(price),
      Description: description,
      ImageURL: imageUrl,
      Listed: listed,
      Discount_Percentage: parseInt(discountPercentage),
      Category_ID: parseInt(categoryId),
      SubCategory_ID: parseInt(subCategoryId),
    };

    try {
      //axios interceptor will automatically include the CSRF token
      const response = await axios.post('/api/add_product', newProduct);

      if (response.status === 201) {
        onAdd(response.data.product);
        onClose(); //close the modal
      } else {
        setError(response.data.error || 'Failed to add product');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('An error occurred while adding the product.');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Add New Product
      </Typography>
      {error && <Typography color="error">{error}</Typography>}
      <TextField
        label="Product Name"
        fullWidth
        margin="normal"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <TextField
        label="Price"
        type="number"
        fullWidth
        margin="normal"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
      />
      <TextField
        label="Description"
        fullWidth
        multiline
        rows={3}
        margin="normal"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <TextField
        label="Image URL"
        fullWidth
        margin="normal"
        value={imageUrl}
        onChange={(e) => setImageUrl(e.target.value)}
      />
      <FormControlLabel
        control={
          <Checkbox
            checked={listed}
            onChange={(e) => setListed(e.target.checked)}
          />
        }
        label="Listed"
      />
      <TextField
        label="Discount Percentage"
        type="number"
        fullWidth
        margin="normal"
        value={discountPercentage}
        onChange={(e) => setDiscountPercentage(e.target.value)}
      />
      <TextField
        label="Category ID"
        type="number"
        fullWidth
        margin="normal"
        value={categoryId}
        onChange={(e) => setCategoryId(e.target.value)}
      />
      <TextField
        label="Subcategory ID"
        type="number"
        fullWidth
        margin="normal"
        value={subCategoryId}
        onChange={(e) => setSubCategoryId(e.target.value)}
      />
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button onClick={onClose} sx={{ mr: 2 }}>
          Cancel
        </Button>
        <Button variant="contained" color="primary" onClick={handleAddProduct}>
          Add Product
        </Button>
      </Box>
    </Box>
  );
};

export default AddProduct;
