import React, { useState } from "react";
import { toast } from "react-toastify";
import { IconCheck, IconX, IconChevronDown, IconChevronUp } from "@tabler/icons-react";
import Modal from "@/components/modal/modal";
import { TextInput } from "@/components/input";
import { CreateTaskRequest } from "@/types/recepthor";
import { Case } from "@/types/case";
import { ReceptorsResponse } from "@/services/receptor";

interface NotificationModalProps {
  isVisible: boolean;
  onClose: () => void;
  caseId: string;
  receptors: ReceptorsResponse[];
  caseData: Case;
  onSuccess?: () => void;
}

interface DefendantFormData {
  address: string;
  deadline: string;
  notes: string;
}

const NotificationModal: React.FC<NotificationModalProps> = ({
  isVisible,
  onClose,
  caseId,
  receptors,
  caseData,
  onSuccess
}) => {
  const [loading, setLoading] = useState(false);
  const [expandedDefendant, setExpandedDefendant] = useState<string | null>(null);
  const [notifiedDefendants, setNotifiedDefendants] = useState<Set<string>>(new Set());
  
  // Obtener todos los demandados
  const defendants = caseData.litigants.filter(litigant => litigant.role === "defendant");
  
  // Inicializar formularios para cada demandado
  const [defendantForms, setDefendantForms] = useState<Record<string, DefendantFormData>>(() => {
    const initialForms: Record<string, DefendantFormData> = {};
    defendants.forEach(defendant => {
      initialForms[defendant.id] = {
        address: defendant.address || "",
        deadline: "",
        notes: "",
      };
    });
    return initialForms;
  });

  const toggleDefendantExpansion = (defendantId: string) => {
    // No permitir expandir si ya fue notificado
    if (notifiedDefendants.has(defendantId)) {
      return;
    }
    
    setExpandedDefendant(prev => {
      // Si el formulario ya está expandido, lo cerramos
      if (prev === defendantId) {
        return null;
      }
      // Si no, expandimos este formulario (cerrando cualquier otro)
      return defendantId;
    });
  };

  const handleDefendantInputChange = (defendantId: string, field: string, value: string) => {
    setDefendantForms(prev => ({
      ...prev,
      [defendantId]: {
        ...prev[defendantId],
        [field]: value
      }
    }));
  };

  const handleSubmit = async (defendantId: string) => {
    const formData = defendantForms[defendantId];
    
    // Validar campos requeridos
    if (!formData.address.trim() || !formData.deadline.trim()) {
      toast.error("Por favor complete todos los campos obligatorios");
      return;
    }

    if (receptors.length === 0) {
      toast.error("Debe seleccionar al menos un receptor");
      return;
    }

    try {
      setLoading(true);
      
      const taskData: CreateTaskRequest = {
        address: formData.address,
        caseId: caseId,
        deadline: new Date(formData.deadline).toISOString(),
        notes: formData.notes,
        receptorIds: receptors.map(r => r.id),
      };
      // await createTask(taskData);
      
      toast.success("Notificación creada exitosamente");
      
      // Marcar como notificado
      setNotifiedDefendants(prev => new Set(prev).add(defendantId));
      
      // Reset form para este demandado específico
      setDefendantForms(prev => ({
        ...prev,
        [defendantId]: {
          address: "",
          deadline: "",
          notes: "",
        }
      }));
      
      // Cerrar el formulario expandido
      setExpandedDefendant(null);
      
      // onSuccess?.();
    } catch (error: any) {
      toast.error(error.message || "Error al crear la notificación");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Modal
      isVisible={isVisible}
      onClose={handleClose}
      title="Crear Avisos"
      customWidthClassName="max-w-6xl w-full max-h-[90vh] overflow-hidden"
    >
      <div className="space-y-4 max-h-[calc(90vh-120px)] overflow-y-auto pr-2">
        {/* Información del caso */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            Se avisará a {receptors.length} receptores del tribunal: {caseData.details?.tribunal.name}
          </p>
          <p className="text-xs text-blue-600 mt-1">
            {defendants.length} demandado{defendants.length !== 1 ? 's' : ''} encontrado{defendants.length !== 1 ? 's' : ''} - {notifiedDefendants.size} notificado{notifiedDefendants.size !== 1 ? 's' : ''} - Solo se puede expandir un formulario a la vez
          </p>
        </div>

        {/* Lista de demandados */}
        <div className="space-y-3">
          {defendants.map((defendant) => {
            const isExpanded = expandedDefendant === defendant.id;
            const isNotified = notifiedDefendants.has(defendant.id);
            const formData = defendantForms[defendant.id];
            
            return (
              <div key={defendant.id} className="border border-gray-200 rounded-lg overflow-hidden">
                {/* Header del demandado */}
                <div 
                  className={`p-4 transition-colors duration-200 flex items-center justify-between ${
                    isNotified
                      ? 'bg-sky-50 border-sky-200 border-l-4 cursor-default'
                      : isExpanded 
                        ? 'bg-teal-50 border-teal-200 border-l-4 cursor-pointer' 
                        : 'bg-gray-50 hover:bg-gray-100 cursor-pointer'
                  }`}
                  onClick={() => !isNotified && toggleDefendantExpansion(defendant.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className={`font-medium truncate ${
                        isNotified 
                          ? 'text-sky-900' 
                          : isExpanded 
                            ? 'text-teal-900' 
                            : 'text-gray-900'
                      }`}>
                        {defendant.name}
                      </h3>
                      {isNotified && (
                        <IconCheck size={16} className="text-sky-600 flex-shrink-0" />
                      )}
                    </div>
                    <p className={`text-sm truncate ${
                      isNotified 
                        ? 'text-sky-700' 
                        : isExpanded 
                          ? 'text-teal-700' 
                          : 'text-gray-600'
                    }`}>
                      RUT: {defendant.rut}
                    </p>
                    {defendant.address && (
                      <p className={`text-xs mt-1 truncate ${
                        isNotified 
                          ? 'text-sky-600' 
                          : isExpanded 
                            ? 'text-teal-600' 
                            : 'text-gray-500'
                      }`}>
                        Dirección: {defendant.address}
                      </p>
                    )}
                    {isNotified && (
                      <p className="text-xs mt-1 text-sky-600 font-medium">
                        ✓ Notificado
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                    {!isNotified && (
                      <>
                        <span className={`text-xs hidden sm:inline ${
                          isExpanded ? 'text-teal-600' : 'text-gray-500'
                        }`}>
                          {isExpanded ? 'Contraer' : 'Expandir'}
                        </span>
                        {isExpanded ? (
                          <IconChevronUp size={20} className="text-teal-600" />
                        ) : (
                          <IconChevronDown size={20} className="text-gray-500" />
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Formulario expandido */}
                {isExpanded && (
                  <div className="p-4 bg-white border-t border-gray-200">
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {/* Dirección */}
                        <div className="lg:col-span-2">
                          <TextInput
                            name={`address-${defendant.id}`}
                            label="Dirección *"
                            value={formData.address}
                            onChange={(value) => handleDefendantInputChange(defendant.id, "address", value)}
                            placeholder="Ingrese la dirección completa"
                            required={true}
                          />
                        </div>

                        {/* Fecha límite */}
                        <div className="lg:col-span-2">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Fecha límite *
                            </label>
                            <input
                              type="date"
                              value={formData.deadline}
                              onChange={(e) => handleDefendantInputChange(defendant.id, "deadline", e.target.value)}
                              className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-200 transition-colors duration-200 bg-white"
                              min={new Date().toISOString().split('T')[0]}
                              required
                            />
                          </div>
                        </div>

                        {/* Notas */}
                        <div className="lg:col-span-2">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Notas
                            </label>
                            <textarea
                              value={formData.notes}
                              onChange={(e) => handleDefendantInputChange(defendant.id, "notes", e.target.value)}
                              placeholder="Notas adicionales (opcional)"
                              className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-200 transition-colors duration-200 bg-white resize-y min-h-20"
                              rows={3}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Botones de acción para este demandado */}
                      <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
                        <button
                          onClick={() => toggleDefendantExpansion(defendant.id)}
                          disabled={loading}
                          className="w-full sm:w-auto px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                          <IconX size={16} />
                          Cancelar
                        </button>
                        <button
                          onClick={() => handleSubmit(defendant.id)}
                          disabled={loading}
                          className={`w-full sm:w-auto px-4 py-2 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2 ${
                            loading
                              ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                              : 'bg-teal-500 hover:bg-teal-600 text-white'
                          }`}
                        >
                          {loading ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                              Creando...
                            </>
                          ) : (
                            <>
                              <IconCheck size={16} />
                              Crear Notificación
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Botón para cerrar modal */}
        <div className="flex justify-end pt-4 border-t border-gray-200 sticky bottom-0 bg-white">
          <button
            onClick={handleClose}
            disabled={loading}
            className="w-full sm:w-auto px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <IconX size={16} />
            Cerrar
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default NotificationModal;
