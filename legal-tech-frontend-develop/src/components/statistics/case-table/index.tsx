import { CaseTableData } from "@/utils/test-data";
import { formatCurrency } from "@/utils/currency";
import { translatedEventNames } from "@/utils/event-types";
import DetailModal from "../detail-modal";
import { useState } from "react";
import { IconFilter, IconBuilding, IconScale } from "@tabler/icons-react";

type LawyerOfficeFilter = 'all' | 'IFBL Abogados' | 'Braun y Asociados';

interface CaseTableProps {
  data: CaseTableData[];
  enableDetailModal: boolean;
  activeFilter?: LawyerOfficeFilter;
}

export default function CaseTable({ data, enableDetailModal, activeFilter = 'all' }: CaseTableProps) {
  const [selectedEvent, setSelectedEvent] = useState<CaseTableData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleRowClick = (item: CaseTableData) => {
    setSelectedEvent(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedEvent(null);
  };

  const getFilteredData = () => {
    if (activeFilter === 'all') {
      return data;
    }
    
    return data.map(item => {
      const officeDetail = item.quantity_detail.find(detail => 
        detail.lawyer_office === activeFilter
      );
      
      if (officeDetail) {
        // Calcular la proporción de casos de esta oficina
        const proportion = officeDetail.quantity / item.quantity;
        
        // Estimar los valores de en plazo y fuera de plazo basados en la proporción
        const estimatedInPeriod = Math.round(item.quantity_in_period * proportion);
        const estimatedOutPeriod = Math.round(item.quantity_out_period * proportion);
        
        // Estimar los montos recuperados y pendientes basados en la proporción
        const estimatedRecoveredAmount = Math.round(item.recovered_amount * proportion);
        const estimatedPendingAmount = Math.round(item.pending_amount * proportion);
        
        return {
          ...item,
          quantity: officeDetail.quantity,
          amount: officeDetail.amount,
          quantity_in_period: estimatedInPeriod,
          quantity_out_period: estimatedOutPeriod,
          recovered_amount: estimatedRecoveredAmount,
          pending_amount: estimatedPendingAmount,
        };
      }
      
      return {
        ...item,
        quantity: 0,
        amount: 0,
        quantity_in_period: 0,
        quantity_out_period: 0,
        recovered_amount: 0,
        pending_amount: 0,
      };
    });
  };

  const filteredData = getFilteredData();

  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-h3 font-semibold text-charcoal-gray mb-4 mt-2 text-center">
          Juicios por Hito
        </h2>
        
        {/* Status indicator */}
        <div className="flex items-center justify-center text-small text-medium-gray mb-4">
          <IconBuilding size={16} className="mr-1" />
          {activeFilter === 'all' 
            ? `Mostrando todos los hitos` 
            : `Mostrando datos de ${activeFilter}`
          }
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden">
        {/* Header de la tabla */}
        <div className="bg-gradient-to-r from-teal-green via-teal-green/95 to-petroleum-blue">
          <div className="px-6 py-6">
            <div className="flex items-center justify-center mb-4">
              <div className="bg-pure-white/20 rounded-full p-2 mr-3">
                <IconScale size={20} className="text-pure-white" />
              </div>
              <h3 className="text-h3 font-serif text-pure-white">
                Detalle de Hitos de Casos
              </h3>
            </div>
            <p className="text-body text-pure-white/90 text-center">
              Análisis detallado por tipo de hito y cumplimiento de plazos
            </p>
          </div>
          
          <div className="grid grid-cols-8 gap-0 w-full bg-pure-white/10 backdrop-blur-sm">
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Tipo de Hito
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Días Plazo
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Tiempo Promedio
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Total Casos
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                En Plazo
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Fuera de Plazo
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Monto Recuperado
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-4">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Monto a Recuperar
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Filas de datos */}
        <div className="divide-y divide-medium-gray">
          {filteredData.map((item, index) => (
            <div
              key={index}
              className={`grid grid-cols-8 gap-0 w-full p-4 ${
                index % 2 === 0 ? "bg-light-gray" : "bg-pure-white"
              } ${enableDetailModal ? "cursor-pointer hover:bg-teal-green/5 transition-colors duration-200" : ""}`}
              onClick={() => enableDetailModal && handleRowClick(item)}
            >
              <div className="text-center">
                <span className="text-body-sm font-medium text-charcoal-gray py-1 px-3 rounded-full bg-petroleum-blue/10">
                  {translatedEventNames[item.event_type]}
                </span>
              </div>
              <div className="text-center">
                <span className="text-body-sm font-medium text-charcoal-gray">
                  {item.period}
                </span>
              </div>
              <div className="text-center">
                <span className="text-body-sm font-medium text-teal-green bg-teal-green/10 px-3 py-1 rounded-full">
                  {item.time}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-h3 font-bold ${
                  activeFilter !== 'all' && item.quantity === 0 
                    ? 'text-medium-gray' 
                    : 'text-charcoal-gray'
                }`}>
                  {item.quantity}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-semibold ${
                  activeFilter !== 'all' && item.quantity_in_period === 0 
                    ? 'text-medium-gray' 
                    : 'text-teal-green'
                }`}>
                  {item.quantity_in_period}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-semibold ${
                  activeFilter !== 'all' && item.quantity_out_period === 0 
                    ? 'text-medium-gray' 
                    : 'text-red-600'
                }`}>
                  {item.quantity_out_period}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-semibold ${
                  activeFilter !== 'all' && item.recovered_amount === 0 
                    ? 'text-medium-gray' 
                    : 'text-green-600'
                }`}>
                  {formatCurrency(item.recovered_amount)}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-semibold ${
                  activeFilter !== 'all' && item.pending_amount === 0 
                    ? 'text-medium-gray' 
                    : 'text-orange-600'
                }`}>
                  {formatCurrency(item.pending_amount)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal de detalles */}
      {selectedEvent && enableDetailModal && (
        <DetailModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          eventType={selectedEvent.event_type}
          quantityDetail={selectedEvent.quantity_detail}
          totalQuantity={selectedEvent.quantity}
          totalAmount={selectedEvent.amount}
        />
      )}
    </div>
  );
}
