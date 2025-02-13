import axios from 'axios';

const API_BASE_URL = 'http://localhost:4000';

export const fetchInventory = () => axios.get(`${API_BASE_URL}/inventory`);
export const fetchOrders = () => axios.get(`${API_BASE_URL}/orders`);
export const fetchProducts = () => axios.get(`${API_BASE_URL}/products`);

// Additional CRUD functions can be added here.
