import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

import Navbar from './components/Navbar';
import CookieConsent from './components/CookieConsent';
import Dashboard from './pages/Dashboard';
import CharacterList from './pages/CharacterList';
import CharacterDetail from './pages/CharacterDetail';
import WorldStats from './pages/WorldStats';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Navbar />
          <Box 
            component="main" 
            sx={{ 
              flexGrow: 1, 
              p: 3,
              width: '80%',
              maxWidth: '1400px',
              margin: '0 auto'
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/characters" element={<CharacterList />} />
              <Route path="/characters/:id" element={<CharacterDetail />} />
              <Route path="/stats" element={<WorldStats />} />
            </Routes>
          </Box>
          <CookieConsent />
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App; 