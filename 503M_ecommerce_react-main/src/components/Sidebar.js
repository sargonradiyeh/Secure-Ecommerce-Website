import React from 'react';
import { Box, List, ListItem, ListItemText, ListItemIcon } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import InventoryIcon from '@mui/icons-material/Inventory';
import WarehouseIcon from '@mui/icons-material/Warehouse';
//import PeopleIcon from '@mui/icons-material/People';

const Sidebar = ({ onSelect }) => {
  const menuItems = [
    { text: "Dashboard", icon: <DashboardIcon />, key: "dashboard" },
    { text: "Warehouse", icon: <WarehouseIcon />, key: "warehouse" },
    { text: "Inventory", icon: <InventoryIcon />, key: "inventory" },
    { text: "Orders", icon: <InventoryIcon />, key: "orders" },
    { text: "Returns", icon: <InventoryIcon />, key: "returns" },
    { text: "Products", icon: <InventoryIcon />, key: "products" },
  ];

  return (
    <Box
      sx={{
        width: 240,
        backgroundColor: "#1976d2",
        height: "100vh", // full height
        color: "white",
        position: "fixed", //ensuring the sidebar stays fixed to the left
        top: 0,
        left: 0,
        zIndex: 1,
      }}
    >
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.key} onClick={() => onSelect(item.key)}>
            <ListItemIcon sx={{ color: "white" }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default Sidebar;
