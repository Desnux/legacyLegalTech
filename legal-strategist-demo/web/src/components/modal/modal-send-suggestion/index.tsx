import React, { useState } from 'react';
import classNames from "classnames";
import { ButtonPrimary, ButtonSecondary } from '@/components/button';
import { sendSuggestion } from "@/services/case";
import { Modal } from '@/components/modal';

// Propiedades necesarias
interface ModalSendSuggestionProps {
  caseId: string;
  eventId: string;
  alternativeId: string;
  file: Blob;
  onClose: () => void;
  onSuccess: () => void; // Para refrescar el timeline de eventos
}

const ModalSendSuggestion: React.FC<ModalSendSuggestionProps> = ({
  caseId,
  eventId,
  alternativeId,
  file,
  onClose,
  onSuccess,
}) => {
  const [password, setPassword] = useState('');
  const [rut, setRut] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSend = async () => {
    try {
      setLoading(true);
      await sendSuggestion(caseId, eventId, alternativeId, file, password, rut);
      setLoading(false);
      onSuccess(); // Refrescar timeline de eventos
      onClose(); // Cerrar modal
    } catch (error) {
      console.error('Error al enviar alternativa:', error);
      setLoading(false);
    }
  };

  return (
    <Modal
      className={classNames("max-h-[90vh] overflow-hidden text-gray-900")}
      isVisible
      onClose={onClose}
      title="Enviar Alternativa"
      footer={
        <div className="flex justify-end space-x-2">
          <ButtonSecondary label="Cancelar" onClick={onClose} />
          <ButtonPrimary
            label="Confirmar y Enviar"
            onClick={handleSend}
            disabled={loading}
            // loading={loading}
          />
        </div>
      }
    >
      {showConfirmation ? (
        <p>¿Estás seguro de que deseas enviar esta alternativa?</p>
      ) : (
        <div className="space-y-4">
          <p>Por favor, ingresa los siguientes datos para enviar la alternativa:</p>
          <input
            type="text"
            placeholder="RUT"
            value={rut}
            onChange={(e) => setRut(e.target.value)}
            className="w-full px-4 py-2 border rounded"
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded"
          />
        </div>
      )}
    </Modal>
  );
};

export default ModalSendSuggestion;
