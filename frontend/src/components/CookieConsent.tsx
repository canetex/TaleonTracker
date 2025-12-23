import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Link,
} from '@mui/material';

const COOKIE_CONSENT_KEY = 'taleontracker_cookie_consent';

export const CookieConsent: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [consent, setConsent] = useState<string | null>(null);

  useEffect(() => {
    // Verifica se já existe consentimento
    const storedConsent = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (!storedConsent) {
      setOpen(true);
    } else {
      setConsent(storedConsent);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'accepted');
    setConsent('accepted');
    setOpen(false);
  };

  const handleReject = () => {
    localStorage.setItem(COOKIE_CONSENT_KEY, 'rejected');
    setConsent('rejected');
    setOpen(false);
  };

  const handleRevoke = () => {
    localStorage.removeItem(COOKIE_CONSENT_KEY);
    setConsent(null);
    setOpen(true);
  };

  if (consent === 'rejected') {
    return (
      <Box
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 1000,
        }}
      >
        <Button
          variant="outlined"
          size="small"
          onClick={handleRevoke}
          sx={{ backgroundColor: 'background.paper' }}
        >
          Gerenciar Cookies
        </Button>
      </Box>
    );
  }

  return (
    <Dialog
      open={open}
      onClose={() => {}}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>Uso de Cookies</DialogTitle>
      <DialogContent>
        <Typography variant="body2" paragraph>
          Este site utiliza cookies para melhorar sua experiência de navegação e 
          para fins de análise. Ao continuar navegando, você concorda com o uso de cookies.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Para mais informações, consulte nossa{' '}
          <Link href="#" onClick={(e) => e.preventDefault()}>
            política de privacidade
          </Link>
          .
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleReject} color="secondary">
          Rejeitar
        </Button>
        <Button onClick={handleAccept} variant="contained" color="primary">
          Aceitar
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CookieConsent;

