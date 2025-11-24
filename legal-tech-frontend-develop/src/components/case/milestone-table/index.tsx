import React, { useState, useMemo, useEffect, useRef } from 'react';
import { Milestone } from '@/types/milestone';
import { CaseDetailInfo } from '@/types/case';
import { IconFile, IconX, IconEye, IconEdit, IconCheck, IconX as IconClose, IconChevronDown, IconChevronUp, IconCalendarEvent, IconSearch } from '@tabler/icons-react';
import ModalDocumentsList from '@/components/modal/modal-documents-list';

// Etapas principales del proceso de scraping con tiempos estimados basados en logs reales (~71 segundos)
// Tiempos basados en: 13:10:19 - 13:11:30
const SCRAPER_STAGES = [
  { text: 'Autenticando...', delay: 2000 },
  { text: 'Buscando caso en PJUD...', delay: 2000 },
  { text: 'Seleccionando datos del caso...', delay: 10000 },
  { text: 'Extrayendo trámites...', delay: 10000 },
  { text: 'Identificando hitos...', delay: 2000 },
  { text: 'Guardando en base de datos...', delay: 2000 },
  { text: 'Procesando eventos...', delay: 7000 }
];

interface MilestoneTableProps {
  milestones: Milestone[];
  onMilestoneClick?: (milestone: Milestone) => void;
  onDocumentClick?: (documents: string[]) => void;
  onAnnexClick?: (annexes: string[]) => void;
  onMilestoneUpdate?: (index: number, updatedMilestone: Milestone) => void;
  onScrapeCaseNotebook?: () => void;
  loadingScraper?: boolean;
  caseDetails?: CaseDetailInfo | null;
  className?: string;
}

const MilestoneTable: React.FC<MilestoneTableProps> = ({
  milestones,
  onMilestoneClick,
  onDocumentClick,
  onAnnexClick,
  onMilestoneUpdate,
  onScrapeCaseNotebook,
  loadingScraper = false,
  caseDetails,
  className = ''
}) => {
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isAnnexModalVisible, setIsAnnexModalVisible] = useState(false);
  const [selectedAnnexes, setSelectedAnnexes] = useState<string[]>([]);
  const [editingRow, setEditingRow] = useState<number | null>(null);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<number>>(new Set());
  const [isTableVisible, setIsTableVisible] = useState(false);
  const [visibleCount, setVisibleCount] = useState(5);
  const [editForm, setEditForm] = useState<{
    actionToFollow: string;
    responsiblePerson: string;
    deadline: string;
  }>({
    actionToFollow: '',
    responsiblePerson: '',
    deadline: ''
  });
  const [currentStageIndex, setCurrentStageIndex] = useState(0);

  // Simular progreso de etapas cuando loadingScraper es true
  const timeoutsRef = useRef<NodeJS.Timeout[]>([]);

  useEffect(() => {
    if (loadingScraper) {
      setCurrentStageIndex(0);
      
      // Limpiar timeouts anteriores
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
      timeoutsRef.current = [];

      const scheduleNextStage = (index: number) => {
        if (index >= SCRAPER_STAGES.length - 1) {
          return;
        }
        
        const nextIndex = index + 1;
        const timeout = setTimeout(() => {
          setCurrentStageIndex(nextIndex);
          scheduleNextStage(nextIndex);
        }, SCRAPER_STAGES[index].delay);
        
        timeoutsRef.current.push(timeout);
      };

      scheduleNextStage(0);

      return () => {
        timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
        timeoutsRef.current = [];
      };
    } else {
      setCurrentStageIndex(0);
      timeoutsRef.current.forEach(timeout => clearTimeout(timeout));
      timeoutsRef.current = [];
    }
  }, [loadingScraper]);

  const getDocumentIcon = (documents?: string[]) => {
    if (!documents || documents.length === 0) return null;
    
    return (
      <div className="flex items-center gap-1">
        <IconFile size={16} className="text-red-500" />
        {documents.length > 1 && (
          <span className="text-xs text-red-500 font-medium">{documents.length}</span>
        )}
      </div>
    );
  };

  const getAnnexIcon = (annexes?: string[]) => {
    if (!annexes || annexes.length === 0) return null;
    
    return (
      <div className="flex items-center gap-1">
        <IconFile size={16} className="text-blue-500" />
        {annexes.length > 1 && (
          <span className="text-xs text-blue-500 font-medium">{annexes.length}</span>
        )}
      </div>
    );
  };



  const handleDocumentClick = (documents: string[]) => {
    setSelectedDocuments(documents);
    setIsModalVisible(true);
    onDocumentClick?.(documents);
  };

  const handleCloseModal = () => {
    setIsModalVisible(false);
    setSelectedDocuments([]);
  };

  const handleAnnexClick = (annexes: string[]) => {
    setSelectedAnnexes(annexes);
    setIsAnnexModalVisible(true);
    onAnnexClick?.(annexes);
  };

  const handleCloseAnnexModal = () => {
    setIsAnnexModalVisible(false);
    setSelectedAnnexes([]);
  };

  const handleStartEdit = (index: number, milestone: Milestone) => {
    setEditingRow(index);
    setEditForm({
      actionToFollow: milestone.actionToFollow || '',
      responsiblePerson: milestone.responsiblePerson || '',
      deadline: milestone.deadline || ''
    });
  };

  const handleSaveEdit = (index: number) => {
    const updatedMilestone = {
      ...milestones[index],
      ...editForm
    };
    onMilestoneUpdate?.(index, updatedMilestone);
    setEditingRow(null);
    setEditForm({ actionToFollow: '', responsiblePerson: '', deadline: '' });
  };

  const handleCancelEdit = () => {
    setEditingRow(null);
    setEditForm({ actionToFollow: '', responsiblePerson: '', deadline: '' });
  };

  const toggleDescription = (index: number) => {
    const newExpanded = new Set(expandedDescriptions);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedDescriptions(newExpanded);
  };

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const isMilestoneIncomplete = (milestone: Milestone) => {
    return !milestone.actionToFollow || 
           !milestone.responsiblePerson || 
           !milestone.deadline ||
           milestone.actionToFollow.trim() === '' ||
           milestone.responsiblePerson.trim() === '' ||
           milestone.deadline.trim() === '';
  };

  const toggleTableVisibility = () => {
    setIsTableVisible(!isTableVisible);
    if (!isTableVisible) {
      setVisibleCount(5);
    }
  };

  const loadMoreMilestones = () => {
    setVisibleCount(prev => Math.min(prev + 5, milestones.length));
  };

  const hasMoreMilestones = visibleCount < milestones.length;
  const visibleMilestones = milestones.slice(0, visibleCount);

  const foliosToday = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    return milestones.filter(milestone => {
      if (!milestone.createdAt) return false;
      const createdDate = new Date(milestone.createdAt);
      createdDate.setHours(0, 0, 0, 0);
      return createdDate.getTime() === today.getTime();
    }).length;
  }, [milestones]);

  // Función para obtener el texto del botón
  const getLoadMoreText = () => {
    const remaining = milestones.length - visibleCount;
    if (remaining <= 5) {
      return `Ver ${remaining} trámite${remaining > 1 ? 's' : ''} más`;
    }
    return 'Ver 5 trámites más';
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden ${className}`}>
      
      
      {/* Header con botón para mostrar/ocultar tabla */}
      <div className="bg-teal-700 text-white px-4 py-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold text-white">Trámites anteriores</h3>
          <div className="flex items-center gap-2">
            {caseDetails && onScrapeCaseNotebook && (
              <button
                onClick={onScrapeCaseNotebook}
                disabled={loadingScraper}
                className="flex items-center gap-2 px-3 py-1 bg-teal-800 hover:bg-teal-900 disabled:bg-gray-500 disabled:cursor-not-allowed rounded-md transition-colors text-sm font-medium"
              >
                <IconSearch size={16} />
                {loadingScraper ? "Obteniendo..." : "Actualizar trámites"}
              </button>
            )}
            <button
              onClick={toggleTableVisibility}
              className="flex items-center gap-2 px-3 py-1 bg-teal-800 hover:bg-teal-900 rounded-md transition-colors text-sm font-medium"
            >
              {isTableVisible ? (
                <>
                  <IconChevronUp size={16} />
                  Ocultar trámites
                </>
              ) : (
                <>
                  <IconChevronDown size={16} />
                  Ver trámites anteriores
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Loader dinámico */}
      {loadingScraper && (
        <div className="px-4 py-3 bg-white border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-teal-200 border-t-teal-600 rounded-full animate-spin"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-teal-800">Obteniendo trámites desde PJUD...</p>
              <p className="text-xs text-teal-600 mt-0.5">{SCRAPER_STAGES[currentStageIndex].text}</p>
            </div>
          </div>
        </div>
      )}

      {/* Cuadro de información de folios de hoy */}
      {isTableVisible && foliosToday > 0 && (
        <div className="bg-gradient-to-r from-teal-50 to-blue-50 border-b border-teal-200 px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="bg-teal-600 p-2 rounded-lg">
              <IconCalendarEvent size={20} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-teal-900">
                El día de hoy se han ingresado {foliosToday} {foliosToday === 1 ? 'folio' : 'folios'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabla - solo visible cuando isTableVisible es true */}
      <div 
        className={`transition-all duration-300 ease-in-out ${
          isTableVisible ? 'opacity-100' : 'max-h-0 opacity-0 overflow-hidden'
        }`}
      >
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1200px]">
            <thead className="bg-teal-700 text-white">
              <tr>
                <th className="px-2 py-3 text-left text-sm font-medium w-16">Folio</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-16">Doc.</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-16">Anexo</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-20">Etapa</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-24">Trámite</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-32">Desc. Trámite</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-24">Fec. Trámite</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-16">Foja</th>
                {/* <th className="px-2 py-3 text-left text-sm font-medium w-32">Acción a Seguir</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-24">Responsable</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-20">Plazo</th>
                <th className="px-2 py-3 text-left text-sm font-medium w-16">Acciones</th> */}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {visibleMilestones.map((milestone, index) => {
                const isIncomplete = isMilestoneIncomplete(milestone);
                return (
                  <tr
                    key={index}
                    className={`hover:bg-gray-50 transition-colors duration-200 ease-in-out cursor-pointer ${
                      hoveredRow === index ? 'bg-gray-50' : ''
                    } ${isIncomplete ? 'bg-yellow-50 border-l-4 border-l-yellow-400' : ''}`}
                    onMouseEnter={() => setHoveredRow(index)}
                    onMouseLeave={() => setHoveredRow(null)}
                    onClick={() => onMilestoneClick?.(milestone)}
                  >
                  <td className="px-2 py-3 text-sm text-gray-900 w-16">
                    {milestone.folio && milestone.folio !== '0' ? milestone.folio : '-'}
                  </td>
                  <td className="px-2 py-3 text-sm w-16">
                    {milestone.document && milestone.document.length > 0 ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDocumentClick(milestone.document!);
                        }}
                        className="flex items-center gap-1 hover:bg-red-50 p-1 rounded transition-colors"
                      >
                        {getDocumentIcon(milestone.document)}
                      </button>
                    ) : (
                      <div className="flex items-center gap-1">
                        <IconX size={16} className="text-red-500" />
                      </div>
                    )}
                  </td>
                  <td className="px-2 py-3 text-sm w-16">
                    {milestone.annex && milestone.annex.length > 0 ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleAnnexClick(milestone.annex!);
                        }}
                        className="flex items-center gap-1 hover:bg-blue-50 p-1 rounded transition-colors"
                      >
                        {getAnnexIcon(milestone.annex)}
                      </button>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-2 py-3 text-sm text-gray-900 w-20">
                    {milestone.stage || '-'}
                  </td>
                  <td className="px-2 py-3 text-sm text-gray-900 w-24">
                    {milestone.procedure || '-'}
                  </td>
                  <td className="px-2 py-3 text-sm text-gray-900 w-32">
                    <div className="relative">
                      {expandedDescriptions.has(index) ? (
                        <div className="text-xs" style={{ maxWidth: '128px', wordBreak: 'break-word' }}>
                          {milestone.procedureDescription || '-'}
                        </div>
                      ) : (
                        <div 
                          className="text-xs truncate" 
                          style={{ maxWidth: '128px' }}
                          title={milestone.procedureDescription || '-'}
                        >
                          {milestone.procedureDescription || '-'}
                        </div>
                      )}
                      {milestone.procedureDescription && milestone.procedureDescription.length > 25 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleDescription(index);
                          }}
                          className="text-teal-700 hover:text-teal-800 text-xs font-medium mt-1 block"
                        >
                          {expandedDescriptions.has(index) ? 'Ver menos' : 'Ver más'}
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-2 py-3 text-sm text-gray-900 w-24">
                    {milestone.procedureDate || '-'}
                  </td>
                  <td className="px-2 py-3 text-sm text-gray-900 w-16">
                    {milestone.page || '-'}
                  </td>
                  {/* <td className="px-2 py-3 text-sm w-32">
                    {editingRow === index ? (
                      <input
                        type="text"
                        value={editForm.actionToFollow}
                        onChange={(e) => setEditForm({...editForm, actionToFollow: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                        placeholder="Ingrese la acción a seguir"
                      />
                    ) : (
                      <span className={`${!milestone.actionToFollow || milestone.actionToFollow.trim() === '' ? 'text-yellow-600 font-medium' : 'text-gray-900'}`}>
                        {milestone.actionToFollow || '⚠️ Pendiente'}
                      </span>
                    )}
                  </td>
                  <td className="px-2 py-3 text-sm w-24">
                    {editingRow === index ? (
                      <input
                        type="text"
                        value={editForm.responsiblePerson}
                        onChange={(e) => setEditForm({...editForm, responsiblePerson: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                        placeholder="Ingrese el responsable"
                      />
                    ) : (
                      <span className={`${!milestone.responsiblePerson || milestone.responsiblePerson.trim() === '' ? 'text-yellow-600 font-medium' : 'text-gray-900'}`}>
                        {milestone.responsiblePerson || '⚠️ Pendiente'}
                      </span>
                    )}
                  </td>
                  <td className="px-2 py-3 text-sm w-20">
                    {editingRow === index ? (
                      <input
                        type="date"
                        value={editForm.deadline}
                        onChange={(e) => setEditForm({...editForm, deadline: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                      />
                    ) : (
                      <span className={`${!milestone.deadline || milestone.deadline.trim() === '' ? 'text-yellow-600 font-medium' : 'text-gray-900'}`}>
                        {milestone.deadline ? new Date(milestone.deadline).toLocaleDateString() : '⚠️ Pendiente'}
                      </span>
                    )}
                  </td>
                  <td className="px-2 py-3 text-sm w-16">
                    {editingRow === index ? (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleSaveEdit(index)}
                          className="p-1 text-green-600 hover:bg-green-50 rounded transition-colors"
                          title="Guardar"
                        >
                          <IconCheck size={16} />
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                          title="Cancelar"
                        >
                          <IconClose size={16} />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartEdit(index, milestone);
                          }}
                          className={`p-1 rounded transition-colors ${
                            isIncomplete 
                              ? 'text-yellow-600 hover:bg-yellow-50' 
                              : 'text-blue-600 hover:bg-blue-50'
                          }`}
                          title={isIncomplete ? "Completar información pendiente" : "Editar"}
                        >
                          <IconEdit size={16} />
                        </button>
                        {isIncomplete && (
                          <span className="text-yellow-500 text-xs">!</span>
                        )}
                      </div>
                    )}
                  </td> */}
                </tr>
              );
              })}
            </tbody>
          </table>
        </div>
        {hasMoreMilestones && (
          <div className="text-center py-4 border-t border-gray-200 bg-gray-50">
            <div className="flex flex-col items-center gap-2">
              <p className="text-sm text-gray-600">
                Mostrando {visibleCount} de {milestones.length} trámites
              </p>
              <button
                onClick={loadMoreMilestones}
                className="flex items-center gap-2 px-4 py-2 bg-teal-700 hover:bg-teal-700 text-white rounded-md transition-colors text-sm font-medium"
              >
                <IconChevronDown size={16} />
                {getLoadMoreText()}
              </button>
            </div>
          </div>
        )}
        {!hasMoreMilestones && milestones.length > 5 && (
          <div className="text-center py-4 border-t border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-600">
              Mostrando todos los {milestones.length} trámites
            </p>
          </div>
        )}
      </div>

      {/* Mensaje cuando no hay datos - solo visible cuando la tabla está abierta */}
      <div 
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isTableVisible && milestones.length === 0 ? 'max-h-[200px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="text-center py-8 text-gray-500">
          <IconEye size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">No hay trámites registrados</p>
          <p className="text-sm">Los trámites aparecerán aquí cuando estén disponibles</p>
        </div>
      </div>

      {/* Modal de documentos */}
      <ModalDocumentsList
        isVisible={isModalVisible}
        onClose={handleCloseModal}
        documents={selectedDocuments}
        title="Documentos del Trámite"
      />

      {/* Modal de anexos */}
      <ModalDocumentsList
        isVisible={isAnnexModalVisible}
        onClose={handleCloseAnnexModal}
        documents={selectedAnnexes}
        title="Anexos del Trámite"
      />
    </div>
  );
};

export default MilestoneTable;
