'use client';

import { formatCurrency } from "@/utils/currency";
import { translatedEventNames } from "@/utils/event-types";
import { QuantityDetail } from '@/utils/test-data';
import { useState } from 'react';
import { IconX, IconFilter, IconBuilding, IconScale, IconCurrencyDollar } from "@tabler/icons-react";

type PeriodFilter = 'all' | 'in_period' | 'out_period';

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  eventType: string;
  quantityDetail: QuantityDetail[];
  totalQuantity: number;
  totalAmount: number;
}

export default function DetailModal({ 
  isOpen, 
  onClose, 
  eventType, 
  quantityDetail, 
  totalQuantity, 
  totalAmount 
}: DetailModalProps) {
  const [activePeriodFilter, setActivePeriodFilter] = useState<PeriodFilter>('all');
  
  // Función para obtener los datos filtrados según el plazo
  const getFilteredData = () => {
    if (activePeriodFilter === 'all') {
      return quantityDetail;
    }
    
    // Para simular datos de en plazo y fuera de plazo, vamos a dividir los casos
    // de cada oficina proporcionalmente
    return quantityDetail.map(detail => {
      const totalCases = detail.quantity;
      
      if (activePeriodFilter === 'in_period') {
        // Simular que el 70% de los casos están en plazo
        const inPeriodCases = Math.round(totalCases * 0.7);
        return {
          ...detail,
          quantity: inPeriodCases,
          amount: Math.round(detail.amount * (inPeriodCases / totalCases))
        };
      } else {
        // Simular que el 30% de los casos están fuera de plazo
        const outPeriodCases = Math.round(totalCases * 0.3);
        return {
          ...detail,
          quantity: outPeriodCases,
          amount: Math.round(detail.amount * (outPeriodCases / totalCases))
        };
      }
    });
  };

  const filteredDetail = getFilteredData();
  const filteredTotalQuantity = filteredDetail.reduce((sum, detail) => sum + detail.quantity, 0);
  const filteredTotalAmount = filteredDetail.reduce((sum, detail) => sum + detail.amount, 0);
  
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-pure-white rounded-2xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden border border-medium-gray">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-green to-petroleum-blue p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-h2 font-serif text-pure-white mb-1">
                Detalle por Estudio de Abogados
              </h2>
              <p className="text-body text-pure-white/90">
                {translatedEventNames[eventType]}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-pure-white hover:text-pure-white/80 text-2xl font-bold transition-colors duration-200"
            >
              <IconX size={24} />
            </button>
          </div>
        </div>
        
        <div className="p-6">
          {/* Filtros de plazo */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex items-center mb-3">
              <IconFilter size={20} className="text-teal-green mr-2" />
              <span className="text-small font-medium text-charcoal-gray">
                Filtrar por plazo:
              </span>
            </div>
            
            <div className="flex bg-light-gray rounded-xl p-1 mb-3">
              <button
                onClick={() => setActivePeriodFilter('all')}
                className={`px-4 py-2 rounded-lg text-small font-medium transition-all duration-200 ${
                  activePeriodFilter === 'all'
                    ? 'bg-pure-white text-teal-green shadow-sm'
                    : 'text-medium-gray hover:text-charcoal-gray hover:bg-pure-white/50'
                }`}
              >
                Todos los casos
              </button>
              <button
                onClick={() => setActivePeriodFilter('in_period')}
                className={`px-4 py-2 rounded-lg text-small font-medium transition-all duration-200 ${
                  activePeriodFilter === 'in_period'
                    ? 'bg-pure-white text-teal-green shadow-sm'
                    : 'text-medium-gray hover:text-charcoal-gray hover:bg-pure-white/50'
                }`}
              >
                En plazo
              </button>
              <button
                onClick={() => setActivePeriodFilter('out_period')}
                className={`px-4 py-2 rounded-lg text-small font-medium transition-all duration-200 ${
                  activePeriodFilter === 'out_period'
                    ? 'bg-pure-white text-teal-green shadow-sm'
                    : 'text-medium-gray hover:text-charcoal-gray hover:bg-pure-white/50'
                }`}
              >
                Fuera de plazo
              </button>
            </div>
            
            <div className="flex items-center text-small text-medium-gray">
              <IconBuilding size={16} className="mr-1" />
              {activePeriodFilter === 'all' 
                ? 'Mostrando todos los casos' 
                : activePeriodFilter === 'in_period'
                ? 'Mostrando casos en plazo'
                : 'Mostrando casos fuera de plazo'
              }
            </div>
          </div>

          {/* Resumen de estadísticas */}
          <div className="mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-teal-green/10 p-6 rounded-xl border border-teal-green/20">
                <div className="flex items-center mb-2">
                  <IconScale size={20} className="text-teal-green mr-2" />
                  <span className="text-small font-medium text-charcoal-gray">Total Juicios</span>
                </div>
                <div className="text-h1 font-bold text-teal-green">{filteredTotalQuantity}</div>
              </div>
              <div className="bg-petroleum-blue/10 p-6 rounded-xl border border-petroleum-blue/20">
                <div className="flex items-center mb-2">
                  <IconCurrencyDollar size={20} className="text-petroleum-blue mr-2" />
                  <span className="text-small font-medium text-charcoal-gray">Monto Total</span>
                </div>
                <div className="text-h1 font-bold text-petroleum-blue">{formatCurrency(filteredTotalAmount)}</div>
              </div>
            </div>
          </div>

          {/* Tabla de detalles */}
          <div className="bg-light-gray rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-petroleum-blue/10">
                    <th className="px-6 py-4 text-left text-small font-semibold text-petroleum-blue">Estudio de Abogados</th>
                    <th className="px-6 py-4 text-center text-small font-semibold text-petroleum-blue">Cantidad</th>
                    <th className="px-6 py-4 text-center text-small font-semibold text-petroleum-blue">Monto</th>
                    <th className="px-6 py-4 text-center text-small font-semibold text-petroleum-blue">% Monto</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-medium-gray">
                  {filteredDetail.map((detail, index) => {
                    const percentage = ((detail.amount / filteredTotalAmount) * 100).toFixed(1);
                    return (
                      <tr key={index} className="hover:bg-pure-white/50 transition-colors duration-200">
                        <td className="px-6 py-4 text-body-sm font-medium text-charcoal-gray">
                          {detail.lawyer_office}
                        </td>
                        <td className="px-6 py-4 text-body-sm text-center text-charcoal-gray">
                          {detail.quantity}
                        </td>
                        <td className="px-6 py-4 text-body-sm text-center text-charcoal-gray">
                          {formatCurrency(detail.amount)}
                        </td>
                        <td className="px-6 py-4 text-body-sm text-center text-charcoal-gray">
                          {percentage}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 