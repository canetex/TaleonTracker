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
          to="/characters"
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
            color="inherit"
            component={RouterLink}
            to="/stats"
            sx={{ mr: 2 }}
          >
            Estatísticas
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/characters/compare"
            sx={{ mr: 2 }}
          >
            Comparar
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 