import React, { useEffect, useState } from 'react';
import { Milestone } from '@/types/milestone';
import { IconFile, IconX, IconEye, IconEdit, IconCheck, IconX as IconClose, IconCaretRightFilled, IconCaretLeftFilled } from '@tabler/icons-react';
import ModalDocumentsList from '@/components/modal/modal-documents-list';
import { Action, fetchActionsByCaseId, sendCreateActionRequest } from '@/services/action';
import { toast } from 'react-toastify';
import classNames from 'classnames';

interface RecentMilestoneCardProps {
  milestone: Milestone;
  caseId: string;
  onMilestoneClick?: (milestone: Milestone) => void;
  onDocumentClick?: (documents: string[]) => void;
  onAnnexClick?: (annexes: string[]) => void;
  onMilestoneUpdate?: (updatedMilestone: Milestone) => void;
  className?: string;
}
const resultsPerPage = 12;

const ActionsCard: React.FC<RecentMilestoneCardProps> = ({
  milestone,
  caseId,
  onMilestoneClick,
  onDocumentClick,
  onAnnexClick,
  onMilestoneUpdate,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isAnnexModalVisible, setIsAnnexModalVisible] = useState(false);
  const [selectedAnnexes, setSelectedAnnexes] = useState<string[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [localMilestone, setLocalMilestone] = useState<Milestone>(milestone);
  const [showActionForm, setShowActionForm] = useState(false);
  const [actions, setActions] = useState<Action[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [actionForm, setActionForm] = useState<{
    actionToFollow: string;
    responsiblePerson: string;
    deadline: string;
    comment?: string;
    completed: boolean;
  }>({
    actionToFollow: '',
    responsiblePerson: '',
    deadline: '',
    comment: '',
    completed: false
  });

  useEffect(() => {
    loadActions();
  }, [currentPage]);

  const loadActions = async () => {
    try {
      const skip = (currentPage - 1) * resultsPerPage;
      const actionsResponse = await fetchActionsByCaseId(caseId, skip, resultsPerPage);
      if (actionsResponse) {
        setActions(actionsResponse.actions);
        setTotalCount(actionsResponse.total_count);
      }
    } catch (error) {
      console.error("Error fetching actions:", error);
      toast.error("No fue posible obtener las acciones");
    }
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

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

  const handleAddAction = () => {
    setShowActionForm(true);
    setActionForm({
      actionToFollow: '',
      responsiblePerson: '',
      deadline: '',
      comment: '',
      completed: false
    });
  };

  const handleSaveAction = async () => {
    await sendCreateActionRequest(caseId, {
      action_to_follow: actionForm.actionToFollow,
      responsible: actionForm.responsiblePerson,
      deadline: actionForm.deadline,
      comment: actionForm.comment || '',
    });
    setShowActionForm(false);
    setActionForm({ 
      actionToFollow: '', 
      responsiblePerson: '', 
      deadline: '', 
      comment: '', 
      completed: false 
    });
    loadActions();
  };

  const handleCancelAction = () => {
    setShowActionForm(false);
    setActionForm({ 
      actionToFollow: '', 
      responsiblePerson: '', 
      deadline: '', 
      comment: '', 
      completed: false 
    });
  };

  const handleDeleteAction = (actionId: string) => {
  };

  const totalPages = Math.ceil(totalCount / resultsPerPage);


  return (
    <div className={`bg-white mt-4 rounded-lg border border-gray-200 shadow-sm overflow-hidden w-full ${className}`}>
      {/* Header */}
      <div className="bg-teal-700 text-white px-4 py-3">
        <h3 className="text-lg font-semibold">Gestión de Acciones</h3>
      </div>

      {/* Contenido de tarjeta */}
      <div className="p-4 w-full">
        {localMilestone ? (
          <div className="w-full">
            <div className="w-full">
              {/* Botón Agregar Acción */}
              <div className="mb-6">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAddAction();
                  }}
                  className="flex items-center gap-2 w-full px-4 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg transition-colors"
                >
                  <IconEdit size={16} />
                  <span className="font-medium">Agregar Acción</span>
                </button>
              </div>

                            {/* Formulario de Acción */}
              {showActionForm && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-700 mb-4">Nueva Acción</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Acción a Seguir */}
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Acción a Seguir</label>
                      <div className="mt-1">
                        <input
                          type="text"
                          value={actionForm.actionToFollow}
                          onChange={(e) => setActionForm({...actionForm, actionToFollow: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                          placeholder="Ingrese la acción a seguir"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    </div>

                    {/* Responsable */}
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Responsable</label>
                      <div className="mt-1">
                        <input
                          type="text"
                          value={actionForm.responsiblePerson}
                          onChange={(e) => setActionForm({...actionForm, responsiblePerson: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                          placeholder="Ingrese el responsable"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    </div>

                    {/* Plazo */}
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Plazo</label>
                      <div className="mt-1">
                        <input
                          type="date"
                          value={actionForm.deadline}
                          onChange={(e) => setActionForm({...actionForm, deadline: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200"
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    </div>

                    {/* Realizado */}
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">¿Realizado?</label>
                      <div className="mt-1">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setActionForm({...actionForm, completed: !actionForm.completed});
                            }}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                              actionForm.completed ? 'bg-green-600' : 'bg-gray-300'
                            }`}
                          >
                            <span
                              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                actionForm.completed ? 'translate-x-6' : 'translate-x-1'
                              }`}
                            />
                          </button>
                          <span className="text-sm text-gray-700">
                            {actionForm.completed ? 'Sí' : 'No'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Comentario */}
                    <div className="md:col-span-2">
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Comentario</label>
                      <div className="mt-1">
                        <textarea
                          value={actionForm.comment || ''}
                          onChange={(e) => setActionForm({...actionForm, comment: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-200 resize-none"
                          placeholder="Ingrese un comentario"
                          rows={3}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Botones de acción */}
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <div className="flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSaveAction();
                        }}
                        className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 transition-colors"
                      >
                        <IconCheck size={14} className="inline mr-1" />
                        Guardar Acción
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCancelAction();
                        }}
                        className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors"
                      >
                        <IconClose size={14} className="inline mr-1" />
                        Cancelar
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Lista de Acciones */}
              {actions.length > 0 && (
                <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-700 mb-4">Acciones Registradas ({actions.length})</h4>
                  
                  <div className="space-y-3">
                    {actions.map((action) => (
                      <div key={action.id} className="p-3 bg-gray-50 rounded-lg border-l-4 border-l-blue-500">
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="text-sm font-medium text-gray-900">{action.action_to_follow}</h5>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs text-gray-600">
                          <div><strong>Responsable:</strong> {action.responsible}</div>
                          <div><strong>Plazo:</strong> {action.deadline ? new Date(action.deadline).toLocaleDateString() : 'Sin definir'}</div>
                          <div><strong>Estado:</strong> 
                            <span className={`ml-1 ${action.completed ? 'text-green-600' : 'text-yellow-600'}`}>
                              {action.completed ? 'Completado' : 'Pendiente'}
                            </span>
                          </div>
                        </div>
                        
                        {action.comment && (
                          <div className="mt-2 text-xs text-gray-600">
                            <strong>Comentario:</strong> {action.comment}
                          </div>
                        )}
                      </div>
                    ))}

                     {/* Pagination */}
                     <div className="justify-center my-2">
                       <button
                         className={classNames(
                           "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
                           currentPage > 1 && "text-blue-700 hover:text-blue-800",
                           currentPage <= 1 && "text-gray-600",
                         )}
                         disabled={currentPage <= 1}
                         onClick={() => handlePageChange(currentPage - 1)}
                       >
                         <IconCaretLeftFilled/>
                       </button>
                       <span className="px-4 py-2 mx-2 text-sm md:text-base">
                         {totalPages > 0 ? currentPage : 0} / {totalPages}
                       </span>
                       <button
                         className={classNames(
                           "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
                           currentPage < totalPages && "text-blue-700 hover:text-blue-800",
                           currentPage >= totalPages && "text-gray-600",
                         )} 
                         disabled={currentPage >= totalPages}
                         onClick={() => handlePageChange(currentPage + 1)}
                       >
                         <IconCaretRightFilled/>
                       </button>
                     </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <IconEye size={48} className="mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">No hay trámite registrado</p>
            <p className="text-sm">El trámite aparecerá aquí cuando esté disponible</p>
          </div>
        )}
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

export default ActionsCard;
