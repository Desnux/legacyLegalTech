import { Tasks, Quote } from "@/types/recepthor";
import { formatDate } from "@/utils/date";
import { IconCircleCheck, IconChevronDown, IconChevronUp } from "@tabler/icons-react";
import { useState } from "react";
import AcceptQuoteModal from "./accept-quote";

interface QuotesProps {
    tasksData: Tasks;
}

const Quotes: React.FC<QuotesProps> = ({
    tasksData,
}) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);

    const handleAcceptClick = (quote: Quote) => {
        setSelectedQuote(quote);
        setIsModalOpen(true);
    };

    const handleConfirmAccept = () => {
        setIsModalOpen(false);
        setSelectedQuote(null);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setSelectedQuote(null);
    };

return (
    <>
    {tasksData && tasksData.quotes && tasksData.quotes.length > 0 && (
        <div className="md:col-span-3">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
            <div className="bg-teal-700 rounded-t-lg text-white px-4 py-3 flex items-center justify-between cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
                <h2 className="text-lg font-semibold">Notificación Receptor</h2>
                {isExpanded ? (
                    <IconChevronUp size={20} className="text-white cursor-pointer" />
                  ) : (
                    <IconChevronDown size={20} className="text-white cursor-pointer" />
                  )}
            </div>
            
            {isExpanded && (
              <div>
                <div className="p-2">
                  <p className="text-sm text-black">Fecha límite para recibir cotizaciones: {formatDate(new Date(new Date(tasksData.createdAt).getTime() + 3 * 24 * 60 * 60 * 1000).toISOString())} 
                    <br /><span className="text-xs text-gray-500">*En caso de que no se acepte una cotización, automáticamente se seleccionará la opción de menor precio.</span>
                  </p>
                  <p className="text-sm text-black mb-4">Fecha límite notificación: {formatDate(new Date(new Date(tasksData.deadline).getTime() + 3 * 24 * 60 * 60 * 1000).toISOString())}</p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-2 px-3 font-medium text-gray-700">Receptor</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-700">Email</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-700">Precio</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-700">Fecha Estimada</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-700">Estado</th>
                        <th className="text-left py-2 px-3 font-medium text-gray-700"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {tasksData.quotes.map((quote) => (
                        <tr key={quote.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-2 px-3">
                            <div className="font-medium text-gray-800">
                              {quote.receptor.user.firstName} {quote.receptor.user.lastName}
                            </div>
                          </td>
                          <td className="py-2 px-3 text-gray-600">
                            {quote.receptor.primaryEmail}
                          </td>
                          <td className="py-2 px-3 text-gray-600">
                            {quote.price ? `$${quote.price}` : 'Sin precio'}
                          </td>
                          <td className="py-2 px-3 text-gray-600">
                            {quote.dateOffered ? new Date(quote.dateOffered).toLocaleDateString() : 'Sin fecha'}
                          </td>
                          <td className="py-2 px-3 text-white">
                            <span className="bg-yellow-500 px-1 py-1 rounded-md">{quote.status}</span>
                          </td>
                          <td className="py-2 px-3 text-gray-600">
                            <button 
                              onClick={() => handleAcceptClick(quote)}
                              className="p-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg transition-colors duration-200 flex items-center justify-center gap-1"
                            >
                              <IconCircleCheck size={18} />
                              Aceptar
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      <AcceptQuoteModal
        isVisible={isModalOpen}
        onClose={handleCloseModal}
        onConfirm={handleConfirmAccept}
        quote={selectedQuote}
      />
    </>
  )

}

export default Quotes;
