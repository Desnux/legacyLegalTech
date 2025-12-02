import React from 'react';
import { DemandTextStructure } from '@/types/demand-text';
import Button from '@/components/button';

interface DemandTextChangesProps {
  originalContent: DemandTextStructure;
  modifiedContent: DemandTextStructure | null;
  showModifiedValues: boolean;
  onToggleComparison: () => void;
  onReset?: () => void;
}

interface ChangedField {
  field: string;
  original: string | null;
  modified: string | null;
  hasChanges: boolean;
}

export const DemandTextChanges: React.FC<DemandTextChangesProps> = ({
  originalContent,
  modifiedContent,
  showModifiedValues,
  onToggleComparison,
  onReset
}) => {
  const getChangedFields = (): ChangedField[] => {
    if (!modifiedContent) return [];
    
    const changes: ChangedField[] = [];
    if (modifiedContent.header !== originalContent.header) {
      changes.push({ 
        field: 'Header', 
        original: originalContent.header, 
        modified: modifiedContent.header,
        hasChanges: true
      });
    }
    if (modifiedContent.summary !== originalContent.summary) {
      changes.push({ 
        field: 'Resumen', 
        original: originalContent.summary, 
        modified: modifiedContent.summary,
        hasChanges: true
      });
    }
    if (modifiedContent.court !== originalContent.court) {
      changes.push({ 
        field: 'Juzgado', 
        original: originalContent.court, 
        modified: modifiedContent.court,
        hasChanges: true
      });
    }
    if (modifiedContent.opening !== originalContent.opening) {
      changes.push({ 
        field: 'Apertura', 
        original: originalContent.opening, 
        modified: modifiedContent.opening,
        hasChanges: true
      });
    }

    const originalArgs = originalContent.missing_payment_arguments || [];
    const modifiedArgs = modifiedContent.missing_payment_arguments || [];
    const originalArgsText = originalArgs.length > 0 ? originalArgs.map(arg => arg.argument).join('\n') : 'Sin argumentos';
    const modifiedArgsText = modifiedArgs.length > 0 ? modifiedArgs.map(arg => arg.argument).join('\n') : 'Sin argumentos';
    
    if (originalArgsText !== modifiedArgsText) {
      changes.push({ 
        field: 'Argumentos de pago', 
        original: originalArgsText, 
        modified: modifiedArgsText,
        hasChanges: true
      });
    }

    if (modifiedContent.main_request !== originalContent.main_request) {
      changes.push({ 
        field: 'Solicitud principal', 
        original: originalContent.main_request, 
        modified: modifiedContent.main_request,
        hasChanges: true
      });
    }
    if (modifiedContent.additional_requests !== originalContent.additional_requests) {
      changes.push({ 
        field: 'Solicitudes adicionales', 
        original: originalContent.additional_requests, 
        modified: modifiedContent.additional_requests,
        hasChanges: true
      });
    }
    

    
    return changes;
  };

  const getFieldContent = (content: DemandTextStructure, field: string): string => {
    switch (field) {
      case 'Header': return content.header || '';
      case 'Resumen': return content.summary || '';
      case 'Juzgado': return content.court || '';
      case 'Apertura': return content.opening || '';
      case 'Argumentos de pago': 
        const args = content.missing_payment_arguments || [];
        return args.length > 0 ? args.map(arg => arg.argument).join('\n') : 'Sin argumentos';
      case 'Solicitud principal': return content.main_request || '';
      case 'Solicitudes adicionales': return content.additional_requests || '';
      default: return '';
    }
  };

  const hasChanges = (): boolean => {
    if (!modifiedContent) return false;
    
    return (
      modifiedContent.header !== originalContent.header ||
      modifiedContent.summary !== originalContent.summary ||
      modifiedContent.court !== originalContent.court ||
      modifiedContent.opening !== originalContent.opening ||
      modifiedContent.main_request !== originalContent.main_request ||
      modifiedContent.additional_requests !== originalContent.additional_requests ||
      JSON.stringify(modifiedContent.missing_payment_arguments) !== JSON.stringify(originalContent.missing_payment_arguments)
    );
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4 px-1">
        {modifiedContent && (
          <div className="flex gap-2">
            {hasChanges() && (
              <Button
                variant="primary"
                size="sm"
                onClick={onToggleComparison}
              >
                {showModifiedValues ? "Ocultar comparación" : "Ver comparación"}
              </Button>
            )}
            {onReset && hasChanges() && (
              <Button
                variant="danger"
                size="sm"
                onClick={onReset}
              >
                Restablecer
              </Button>
            )}
          </div>
        )}
      </div>
      {showModifiedValues && modifiedContent && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
          <h3 className="font-semibold text-sm mb-3 text-yellow-800">Comparación de documentos:</h3>
          
          <div className="space-y-4 mb-4">
            {['Header', 'Resumen', 'Juzgado', 'Apertura', 'Argumentos de pago', 'Solicitud principal', 'Solicitudes adicionales'].map((field) => {
              const originalContentField = getFieldContent(originalContent, field);
              const modifiedContentField = getFieldContent(modifiedContent, field);
              const hasChanges = originalContentField !== modifiedContentField;
              
              return (
                <div key={field} className={`bg-white rounded-md border p-4 ${hasChanges ? 'border-red-300 bg-red-25' : 'border-gray-200'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-sm text-gray-700">{field}</h4>
                    {hasChanges && (
                      <span className="px-3 py-1 bg-red-100 text-red-800 text-xs rounded-full font-medium">Modificado</span>
                    )}
                  </div>
                  
                  {hasChanges ? (
                    <div className="space-y-3">
                      <div>
                        <div className="font-medium text-gray-600 mb-2 flex items-center">
                          <span className="w-3 h-3 bg-red-500 rounded-full mr-2"></span>
                          Original:
                        </div>
                        <div className="text-gray-800 bg-red-50 p-3 rounded border-l-4 border-red-400 text-sm">
                          {originalContentField || '(vacío)'}
                        </div>
                      </div>
                      
                      <div>
                        <div className="font-medium text-gray-600 mb-2 flex items-center">
                          <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                          Modificado:
                        </div>
                        <div className="text-gray-800 bg-green-50 p-3 rounded border-l-4 border-green-400 text-sm">
                          {modifiedContentField || '(vacío)'}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="font-medium text-gray-600 mb-2 flex items-center">
                        <span className="w-3 h-3 bg-gray-400 rounded-full mr-2"></span>
                        Sin cambios:
                      </div>
                      <div className="text-gray-800 bg-gray-50 p-3 rounded border-l-4 border-gray-300 text-sm">
                        {originalContentField || '(vacío)'}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          
          <div className="pt-3 border-t border-yellow-200">
            <h4 className="font-semibold text-sm mb-2 text-yellow-800">Resumen de cambios:</h4>
            <div className="text-xs text-yellow-700 space-y-1">
              {getChangedFields().length > 0 ? (
                getChangedFields().map((change, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                    <span><strong>{change.field}:</strong> Modificado</span>
                  </div>
                ))
              ) : (
                <div className="text-gray-500 italic">No se han realizado cambios aún</div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
