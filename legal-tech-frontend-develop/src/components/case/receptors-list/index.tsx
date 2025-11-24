import React, { useState } from "react";
import { IconEye, IconEyeOff, IconChevronLeft, IconChevronRight, IconChevronUp, IconChevronDown } from "@tabler/icons-react";
import { ReceptorsResponse } from "@/services/receptor";

interface ReceptorsListProps {
  receptorsData: ReceptorsResponse[];
  tribunalName?: string;
  onCreateNotification: () => void;
}

const ReceptorsList: React.FC<ReceptorsListProps> = ({
  receptorsData,
  tribunalName,
  onCreateNotification,
}) => {
  const [showReceptors, setShowReceptors] = useState(false);
  const [currentReceptorPage, setCurrentReceptorPage] = useState(1);
  const [isTableVisible, setIsTableVisible] = useState(false);

  if (!receptorsData || receptorsData.length === 0) {
    return null;
  }

  const receptorsPerPage = 5;
  const totalPages = Math.ceil(receptorsData.length / receptorsPerPage);
  const startIndex = (currentReceptorPage - 1) * receptorsPerPage;
  const endIndex = startIndex + receptorsPerPage;
  const currentReceptors = receptorsData.slice(startIndex, endIndex);

  const handleToggleReceptors = () => {
    setShowReceptors(!showReceptors);
    if (showReceptors) {
      setCurrentReceptorPage(1);
    }
  };

  const handlePreviousPage = () => {
    setCurrentReceptorPage(prev => Math.max(1, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentReceptorPage(prev => Math.min(totalPages, prev + 1));
  };

  const toggleTableVisibility = () => {
    setIsTableVisible(!isTableVisible);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
      {/* Header con botón para mostrar/ocultar sección */}
      <div className="bg-teal-700 text-white px-6 py-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold text-white mb-1">Receptores</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTableVisibility}
              className="flex items-center gap-2 px-3 py-1 bg-teal-800 hover:bg-teal-900 rounded-md transition-colors text-sm font-medium"
            >
              {isTableVisible ? (
                <>
                  <IconChevronUp size={16} />
                  Ocultar receptores
                </>
              ) : (
                <>
                  <IconChevronDown size={16} />
                  Ver receptores
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Contenido - solo visible cuando isTableVisible es true */}
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isTableVisible ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="p-4">
          <p className="text-sm text-gray-500 mb-4">
            Hay {receptorsData.length} Receptores asociados al tribunal: {tribunalName}
          </p>

          <div className="flex gap-2 mb-4">
            <button
              onClick={handleToggleReceptors}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              {showReceptors ? <IconEyeOff size={18} /> : <IconEye size={18} />}
              {showReceptors ? 'Ocultar Receptores' : 'Ver Receptores Disponibles'}
            </button>

            <button
              onClick={onCreateNotification}
              className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
            >
              Crear Aviso
            </button>
          </div>

          {showReceptors && (
            <div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Nombre
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email Principal
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Teléfono Principal
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dirección
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {currentReceptors.map((receptor, index) => (
                      <tr key={receptor.id || index} className="hover:bg-gray-50">
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                          {receptor.name || 'N/A'}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                          {receptor.primary_email || 'N/A'}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                          {receptor.primary_phone || 'N/A'}
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                          {receptor.address || 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-700">
                    Mostrando {startIndex + 1} - {Math.min(endIndex, receptorsData.length)} de {receptorsData.length} receptores
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handlePreviousPage}
                      disabled={currentReceptorPage === 1}
                      className={`px-3 py-2 rounded-lg transition-colors duration-200 flex items-center gap-1 ${
                        currentReceptorPage === 1
                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                          : 'bg-teal-600 hover:bg-teal-700 text-white'
                      }`}
                    >
                      <IconChevronLeft size={16} />
                      Anterior
                    </button>
                    <span className="px-4 py-2 text-sm text-gray-700 flex items-center">
                      Página {currentReceptorPage} de {totalPages}
                    </span>
                    <button
                      onClick={handleNextPage}
                      disabled={currentReceptorPage === totalPages}
                      className={`px-3 py-2 rounded-lg transition-colors duration-200 flex items-center gap-1 ${
                        currentReceptorPage === totalPages
                          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                          : 'bg-teal-600 hover:bg-teal-700 text-white'
                      }`}
                    >
                      Siguiente
                      <IconChevronRight size={16} />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReceptorsList;

