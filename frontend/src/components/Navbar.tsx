import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

const Navbar: React.FC = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          TaleonTracker
        </Typography>
        <Box>
          <Button
            color="inherit"
            component={RouterLink}
            to="/characters"
            sx={{ mr: 2 }}
          >
            Personagens
          </Button>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<AddIcon />}
            component={RouterLink}
            to="/characters/new"
          >
            Novo Personagem
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 