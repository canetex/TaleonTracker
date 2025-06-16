import React, { useState } from 'react';
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface AddCharacterFormProps {
  onAdd: (name: string) => void;
}

const AddCharacterForm: React.FC<AddCharacterFormProps> = ({ onAdd }) => {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState('');

  const handleSubmit = () => {
    if (name.trim()) {
      onAdd(name.trim());
      setName('');
      setOpen(false);
    }
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
      >
        Novo Personagem
      </Button>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Adicionar Novo Personagem</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nome do Personagem"
            type="text"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancelar</Button>
          <Button onClick={handleSubmit} color="primary">
            Adicionar
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AddCharacterForm; 