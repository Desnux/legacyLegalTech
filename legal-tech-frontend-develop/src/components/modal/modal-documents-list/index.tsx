import React from 'react';
import { IconX, IconExternalLink, IconFile } from '@tabler/icons-react';

interface ModalDocumentsListProps {
  isVisible: boolean;
  onClose: () => void;
  documents: string[];
  title?: string;
}

const ModalDocumentsList: React.FC<ModalDocumentsListProps> = ({
  isVisible,
  onClose,
  documents,
  title = "Documentos"
}) => {
  if (!isVisible) return null;

  const handleDocumentClick = (document: string) => {
    // Si es una URL, abrir en nueva pestaña
    if (document.startsWith('http://') || document.startsWith('https://')) {
      window.open(document, '_blank');
    } else {
      // Si no es una URL, podrías implementar descarga o preview
      console.log('Documento clickeado:', document);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <IconX size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {documents.length === 0 ? (
            <div className="text-center py-8">
              <IconFile size={48} className="mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500">No hay documentos disponibles</p>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((document, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleDocumentClick(document)}
                >
                  <div className="flex items-center gap-3">
                    <IconFile size={20} className="text-blue-500" />
                    <span className="text-gray-900 font-medium">
                      {document.includes('/') ? document.split('/').pop() : document}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {document.startsWith('http://') || document.startsWith('https://') ? (
                      <IconExternalLink size={16} className="text-blue-500" />
                    ) : (
                      <IconFile size={16} className="text-gray-400" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalDocumentsList;
