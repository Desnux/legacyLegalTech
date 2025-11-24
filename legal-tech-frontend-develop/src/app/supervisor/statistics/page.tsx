'use client';

import { formatCurrency } from "@/utils/currency";
import { statisticsData, statisticsData2, statisticsData4, statisticsDataIFBL, statisticsDataBraun, causeOrderData } from "@/utils/test-data";
import CaseCount from "@/components/statistics/case-count";
import PieChart from "@/components/statistics/pie-chart";
import CaseTable from "@/components/statistics/case-table";
import CauseOrderTable from "@/components/statistics/cause-order-table";
import OfficeFilter from "@/components/statistics/office-filter";
import { useState } from "react";
import { IconChartPie, IconBuilding, IconScale, IconTrendingUp, IconFileText } from "@tabler/icons-react";

type LawyerOfficeFilter = 'all' | 'IFBL Abogados' | 'Braun y Asociados';

export default function SupervisorStatistics() {
  const [activeLawyerOffice, setActiveLawyerOffice] = useState<LawyerOfficeFilter>('all');

  const getFilteredOfficeData = () => {
    if (activeLawyerOffice === 'all') {
      return statisticsData4;
    }
    
    // Solo mostrar la oficina seleccionada
    const selectedOffice = statisticsData4.find(office => office.name === activeLawyerOffice);
    if (!selectedOffice) return [];
    
    // Calcular los datos filtrados basados en la tabla de hitos
    const officeCases = statisticsData2.flatMap(hito => 
      hito.quantity_detail.filter(detail => detail.lawyer_office === selectedOffice.name)
    );
    
    const totalQuantity = officeCases.reduce((sum, case_) => sum + case_.quantity, 0);
    const totalAmount = officeCases.reduce((sum, case_) => sum + case_.amount, 0);
    
    return [{
      ...selectedOffice,
      quantity: totalQuantity,
      amount: totalAmount
    }];
  };

  const getFilteredStatisticsData = () => {
    switch (activeLawyerOffice) {
      case 'IFBL Abogados':
        return statisticsDataIFBL;
      case 'Braun y Asociados':
        return statisticsDataBraun;
      default:
        return statisticsData;
    }
  };

  const filteredOfficeData = getFilteredOfficeData();
  const filteredStatisticsData = getFilteredStatisticsData();
  const totalAmount = filteredStatisticsData.reduce((acc, item) => acc + item.amount, 0);
  const totalCases = filteredStatisticsData.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <div className="min-h-screen bg-light-gray py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-gradient-to-r from-teal-green to-petroleum-blue rounded-full p-3 mr-4">
              <IconChartPie size={32} className="text-pure-white" />
            </div>
          </div>
          <h1 className="text-h1 font-serif text-petroleum-blue mb-4">
            Panel de Estadísticas
          </h1>
          <p className="text-body text-charcoal-gray max-w-2xl mx-auto">
            Análisis completo de juicios y distribución por rangos de monto, hitos de casos y estudios de abogados
          </p>
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {/* Global Office Filter */}
          <OfficeFilter 
            activeFilter={activeLawyerOffice}
            onFilterChange={setActiveLawyerOffice}
          />

          {/* Statistics Cards */}
          <section>
            <div className="flex items-center mb-6">
              <IconTrendingUp size={24} className="text-teal-green mr-3" />
              <h2 className="text-h2 font-serif text-charcoal-gray">
                Resumen de Juicios
              </h2>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-6 gap-6">
              {filteredStatisticsData.map((item) => (
                <CaseCount key={`${item.start_amount}-${item.end_amount}`} item={item} />
              ))}
              
              {/* Total Cases Card */}
              <div className="col-span-2 lg:col-span-1">
                <div className="bg-gradient-to-br from-petroleum-blue to-petroleum-blue/90 rounded-2xl p-6 shadow-lg border border-medium-gray h-full">
                  <div className="text-center">
                    <div className="bg-pure-white/20 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-4">
                      <IconScale size={24} className="text-pure-white" />
                    </div>
                    <h3 className="text-small font-semibold text-pure-white/90 mb-2">
                      Total Juicios
                    </h3>
                    <div className="text-h2 font-bold text-pure-white">
                      {totalCases}
                    </div>
                    <p className="text-body text-white mb-1">
                      Juicios
                    </p>
                    <p className="text-small font-semibold text-white">
                      {formatCurrency(totalAmount)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Charts Section */}
          <section>
            <div className="flex items-center mb-6">
              <IconChartPie size={24} className="text-teal-green mr-3" />
              <h2 className="text-h2 font-serif text-charcoal-gray">
                Análisis Gráfico
              </h2>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <PieChart 
                type="statistics" 
                title="Distribución por Rango de Monto" 
                data={filteredStatisticsData} 
              />
              <PieChart 
                type="case-table" 
                title="Distribución por Hitos de Casos" 
                data={statisticsData2} 
              />
            </div>
          </section>

          {/* Case Table Section */}
          <section>
            <div className="flex items-center mb-6">
              <IconScale size={24} className="text-teal-green mr-3" />
              <h2 className="text-h2 font-serif text-charcoal-gray">
                Detalle de Casos
              </h2>
            </div>
            
            <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden">
              <CaseTable 
                data={statisticsData2} 
                enableDetailModal={true} 
                activeFilter={activeLawyerOffice}
              />
            </div>
          </section>

          {/* Cause Order Table Section */}
          <section>
            <div className="flex items-center mb-6">
              <IconFileText size={24} className="text-teal-green mr-3" />
              <h2 className="text-h2 font-serif text-charcoal-gray">
                Orden de Causas por Monto
              </h2>
            </div>
            
            <div className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray overflow-hidden">
              <CauseOrderTable data={causeOrderData} activeFilter={activeLawyerOffice} />
            </div>
          </section>

          {/* Lawyer Offices Section */}
          <section>
            <div className="flex items-center mb-6">
              <IconBuilding size={24} className="text-teal-green mr-3" />
              <h2 className="text-h2 font-serif text-charcoal-gray">
                Estudios de Abogados
              </h2>
            </div>
            
            <div className="space-y-8">
              {/* Office Cards */}
              <div>
                <h3 className="text-h3 font-semibold text-charcoal-gray mb-4 text-center">
                  Juicios por Estudio de Abogados
                </h3>
                <div className={`grid gap-6 ${
                  activeLawyerOffice === 'all' 
                    ? 'grid-cols-1 md:grid-cols-2' 
                    : 'grid-cols-1 justify-items-center'
                }`}>
                  {filteredOfficeData.map((item) => (
                    <div 
                      key={item.name}
                      className="bg-pure-white rounded-2xl shadow-lg border border-medium-gray p-6 hover:shadow-xl transition-shadow duration-300"
                    >
                      <div className="text-center">
                        <div className="bg-teal-green/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                          <IconBuilding size={28} className="text-teal-green" />
                        </div>
                        <h4 className="text-h3 font-semibold text-petroleum-blue mb-2">
                          {item.name}
                        </h4>
                        <div className="text-h1 font-bold text-teal-green mb-2">
                          {item.quantity}
                        </div>
                        <p className="text-body text-charcoal-gray">
                          {formatCurrency(item.amount)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Office Distribution Chart */}
              <div>
                <PieChart 
                  type="lawyer-office" 
                  title="Distribución por Oficina de Abogados" 
                  data={filteredOfficeData} 
                />
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-medium-gray">
          <div className="text-center">
            <p className="text-small text-medium-gray">
              Última actualización: {new Date().toLocaleString('es-CL')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
