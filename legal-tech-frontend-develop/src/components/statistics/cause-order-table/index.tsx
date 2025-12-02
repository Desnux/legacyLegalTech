import { CauseOrderData } from "@/utils/test-data";
import { formatCurrency } from "@/utils/currency";
import { IconFileText, IconCalculator } from "@tabler/icons-react";

type LawyerOfficeFilter = 'all' | 'IFBL Abogados' | 'Braun y Asociados';

interface CauseOrderTableProps {
  data: CauseOrderData[];
  activeFilter?: LawyerOfficeFilter;
}

export default function CauseOrderTable({ data, activeFilter = 'all' }: CauseOrderTableProps) {
  const getFilteredData = () => {
    if (activeFilter === 'all') {
      return data;
    }
    
    return data.filter(item => item.lawyer_office === activeFilter);
  };

  const filteredData = getFilteredData();

  return (
    <div className="w-full">
      {/* Tabla */}
      <div className="bg-pure-white overflow-hidden">
        {/* Header de la tabla */}
        <div className="bg-gradient-to-r from-petroleum-blue to-petroleum-blue/90">
          <div className="px-6 py-4">
            <div className="flex items-center justify-center mb-3">
              <div className="bg-pure-white/20 rounded-full p-2 mr-3">
                <IconFileText size={20} className="text-pure-white" />
              </div>
              <h3 className="text-h3 font-serif text-pure-white">
                Orden de Causas por Monto
              </h3>
            </div>
          </div>
          
          <div className="grid grid-cols-6 gap-0 w-full bg-pure-white/10 backdrop-blur-sm">
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Causa
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Deudor
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Capital
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Intereses
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Calificación
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
            <div className="p-3 border-r border-pure-white/20">
              <h4 className="font-semibold text-pure-white text-center text-small mb-1">
                Plazos
              </h4>
              <div className="w-8 h-0.5 bg-pure-white/60 mx-auto rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Filas de datos */}
        <div className="divide-y divide-medium-gray">
          {filteredData.map((item, index) => (
            <div
              key={item.id}
              className={`grid grid-cols-6 gap-0 w-full p-3 ${
                item.isSummary 
                  ? "bg-gradient-to-r from-teal-green/10 to-petroleum-blue/10 border-l-4 border-teal-green" 
                  : index % 2 === 0 
                    ? "bg-light-gray" 
                    : "bg-pure-white"
              }`}
            >
              <div className="text-center">
                <span className={`text-body-sm font-medium ${
                  item.isSummary 
                    ? 'text-petroleum-blue font-bold' 
                    : 'text-charcoal-gray'
                }`}>
                  {item.cause}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-medium ${
                  item.isSummary 
                    ? 'text-petroleum-blue font-bold' 
                    : 'text-charcoal-gray'
                }`}>
                  {item.debtor}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-medium ${
                  item.isSummary 
                    ? 'text-petroleum-blue font-bold' 
                    : item.capital === 0 
                      ? 'text-medium-gray' 
                      : 'text-charcoal-gray'
                }`}>
                  {item.capital > 0 ? formatCurrency(item.capital) : ''}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-medium ${
                  item.isSummary 
                    ? 'text-petroleum-blue font-bold' 
                    : item.interest === 0 
                      ? 'text-medium-gray' 
                      : 'text-charcoal-gray'
                }`}>
                  {item.interest > 0 ? formatCurrency(item.interest) : ''}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-medium px-2 py-1 rounded-full ${
                  item.qualification === "Alto Riesgo" 
                    ? "bg-red-100 text-red-700" 
                    : item.qualification === "Medio Riesgo"
                    ? "bg-yellow-100 text-yellow-700"
                    : item.qualification === "Bajo Riesgo"
                    ? "bg-green-100 text-green-700"
                    : "text-medium-gray"
                }`}>
                  {item.qualification}
                </span>
              </div>
              <div className="text-center">
                <span className={`text-body-sm font-medium px-2 py-1 rounded-full ${
                  item.terms ? "bg-blue-100 text-blue-700" : "text-medium-gray"
                }`}>
                  {item.terms}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer con resumen */}
      <div className="py-4 border-t border-medium-gray flex items-center justify-center gap-6 text-small text-medium-gray">
        <div className="flex items-center">
          <IconCalculator size={16} className="mr-2" />
          <span>Total de causas: {filteredData.filter(item => !item.isSummary && item.capital > 0).length}</span>
        </div>
        <div className="flex items-center">
          <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
          <span>Alto Riesgo: {filteredData.filter(item => !item.isSummary && item.qualification === "Alto Riesgo").length}</span>
        </div>
        <div className="flex items-center">
          <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
          <span>Medio Riesgo: {filteredData.filter(item => !item.isSummary && item.qualification === "Medio Riesgo").length}</span>
        </div>
        <div className="flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          <span>Bajo Riesgo: {filteredData.filter(item => !item.isSummary && item.qualification === "Bajo Riesgo").length}</span>
        </div>
      </div>
    </div>
  );
} 