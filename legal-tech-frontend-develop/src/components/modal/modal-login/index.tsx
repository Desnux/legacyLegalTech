import { useState } from "react";
import Button from "@/components/button";
import { TextInput, PasswordInput } from "@/components/input";

interface ModalLoginProps {
  isVisible: boolean;
  onClose: () => void;
  onSubmit: (username: string, password: string) => void;
  loading?: boolean;
}

const ModalLogin = ({ isVisible, onClose, onSubmit, loading = false }: ModalLoginProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = () => {
    onSubmit(username, password);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-pure-white rounded-2xl shadow-xl border border-medium-gray p-8 max-w-md w-full mx-4">
        <h2 className="text-h2 font-semibold text-petroleum-blue mb-6 text-center">Iniciar Sesión</h2>
        
        <div className="space-y-4">
          <TextInput
            name="username"
            label="Usuario"
            placeholder="Ingrese su usuario"
            value={username}
            onChange={setUsername}
            className="w-full"
          />
          
          <PasswordInput
            name="password"
            label="Contraseña"
            placeholder="Ingrese su contraseña"
            value={password}
            onChange={setPassword}
            className="w-full"
          />
        </div>
        
        <div className="flex gap-3 mt-6">
          <Button
            variant="secondary"
            onClick={onClose}
            className="flex-1"
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            loading={loading}
            disabled={!username || !password}
            className="flex-1"
          >
            Ingresar
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModalLogin;
