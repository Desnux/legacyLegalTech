import Button from "@/components/button";
import { Quote } from "@/types/recepthor";
import { IconUser, IconMail, IconCurrencyDollar, IconCalendar } from "@tabler/icons-react";

interface AcceptQuoteModalProps {
  isVisible: boolean;
  onClose: () => void;
  onConfirm: () => void;
  quote: Quote | null;
}

const AcceptQuoteModal = ({ 
  isVisible, 
  onClose, 
  onConfirm, 
  quote
}: AcceptQuoteModalProps) => {
  if (!isVisible || !quote) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-semibold text-teal-700 mb-4">
          Confirmar Aceptación de Receptor
        </h2>
        
        <p className="text-sm text-gray-600 mb-6">
          ¿Deseas aceptar a este receptor para realizar la notificación?
        </p>

        <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-3">
          <div className="flex items-start gap-3">
            <IconUser size={20} className="text-teal-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs text-gray-500 uppercase">Receptor</p>
              <p className="text-sm font-medium text-gray-800">
                {quote.receptor.user.firstName} {quote.receptor.user.lastName}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <IconMail size={20} className="text-teal-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs text-gray-500 uppercase">Email</p>
              <p className="text-sm font-medium text-gray-800">
                {quote.receptor.primaryEmail}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <IconCurrencyDollar size={20} className="text-teal-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs text-gray-500 uppercase">Precio</p>
              <p className="text-sm font-medium text-gray-800">
                {quote.price ? `$${quote.price.toLocaleString('es-CL')}` : 'Sin precio'}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <IconCalendar size={20} className="text-teal-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs text-gray-500 uppercase">Fecha Estimada</p>
              <p className="text-sm font-medium text-gray-800">
                {quote.dateOffered 
                  ? new Date(quote.dateOffered).toLocaleDateString('es-CL', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    })
                  : 'Sin fecha'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3 justify-end">
          <Button
            variant="secondary"
            onClick={onClose}
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            onClick={onConfirm}
          >
            Aceptar Receptor
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AcceptQuoteModal;
