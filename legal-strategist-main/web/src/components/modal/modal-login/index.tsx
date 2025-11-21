import { useState } from "react";
import classNames from "classnames";
import { ButtonPrimary, ButtonSecondary } from "@/components/button";
import { PasswordInput } from "@/components/input";
import { Modal } from "@/components/modal";

interface ModalLoginProps {
  isVisible: boolean;
  onClose: () => void;
  onSubmit: (token: string) => void;
  className?: string;
}

const ModalLogin = ({ isVisible, onClose, onSubmit, className }: ModalLoginProps) => {
  const [authToken, setAuthToken] = useState("");

  const handleSubmit = () => {
    if (authToken.trim()) {
      onSubmit(authToken);
    }
    setAuthToken("");
  };

  if (!isVisible) {
    return null;
  }

  return (
    <Modal
      className={classNames("text-gray-900", className)}
      isVisible={isVisible}
      onClose={onClose}
      title="Autorizar"
      footer={(
        <div className="flex justify-end space-x-2">
          <ButtonSecondary label="Cancelar" onClick={onClose}/>
          <ButtonPrimary label="Ingresar" onClick={handleSubmit}/>
        </div>
      )}
    >
      <PasswordInput
        name="auth-token"
        value={authToken}
        onChange={(value) => setAuthToken(value)}
        placeholder="Ingrese su token de autenticación"
      />
    </Modal>
  );
};

export default ModalLogin;
