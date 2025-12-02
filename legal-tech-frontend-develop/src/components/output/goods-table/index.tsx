import { useEffect, useState } from "react";
import classNames from "classnames";
import { IconBuilding, IconCar, IconHome, IconSearch, IconExternalLink } from "@tabler/icons-react";
import { DefendantSocietyInformation, DefendantVehicleInformation, DefendantPropertyInformation } from "@/services/demand-text";
import SubtleLoader from "@/components/loading/subtle-loader";

export interface GoodsGroup {
  sources?: { source: string, url: string}[];
  source: string;
  url: string;
  headers: string[];
  values: string[][];
}

export interface NewGoodsGroup {
  societies: DefendantSocietyInformation[];
  vehicles: DefendantVehicleInformation[];
  properties: DefendantPropertyInformation[];
}

interface GoodsTableProps {
  className?: string;
  goods: NewGoodsGroup;
  loading?: boolean;
  loadingStates?: {
    societies: boolean;
    vehicles: boolean;
    properties: boolean;
  };
}

const GOODS_TABLE_STAGES = [
  { text: 'Conectando a HomesPotter.', delay: 2000 },
  { text: 'Solicitando información de bienes.', delay: 2000 },
  { text: 'Procesando información.', delay: 2000 },
  { text: 'Esperando respuesta de HomesPotter.', delay: 2000 },
];

const ModernTable = ({ 
  title, 
  icon: Icon, 
  headers, 
  data, 
  loading, 
  loadingMessage 
}: { 
  title: string; 
  icon: any; 
  headers: string[]; 
  data: any[]; 
  loading?: boolean; 
  loadingMessage: string;
}) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  useEffect(() => {
    if (loading) {
      setCurrentMessageIndex(0);
      const timeoutIds: NodeJS.Timeout[] = [];

      const scheduleNextMessage = (index: number) => {
        if (index >= GOODS_TABLE_STAGES.length - 1) {
          return;
        }
        
        const nextIndex = index + 1;
        const timeoutId = setTimeout(() => {
          setCurrentMessageIndex(nextIndex);
          scheduleNextMessage(nextIndex);
        }, GOODS_TABLE_STAGES[index].delay);
        
        timeoutIds.push(timeoutId);
      };

      scheduleNextMessage(0);

      return () => {
        timeoutIds.forEach(id => clearTimeout(id));
      };
    }
  }, [loading]);

  return (
    <div className="bg-pure-white rounded-xl border border-medium-gray shadow-sm overflow-hidden">
      {/* Header de la sección */}
      <div className="bg-gradient-to-r from-light-gray to-pure-white px-4 py-3 border-b border-medium-gray">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-teal-green/10 rounded-lg">
            <Icon size={16} className="text-teal-green" />
          </div>
          <h3 className="text-body font-semibold text-petroleum-blue">{title}</h3>
          {loading ? (
            <div className="ml-auto flex items-center gap-2">
              <div className="w-3 h-3 border border-teal-green/30 border-t-teal-green rounded-full animate-spin"></div>
              <span className="text-xs text-medium-gray">Cargando...</span>
            </div>
          ) : data.length > 0 ? (
            <span className="ml-auto bg-teal-green/10 text-teal-green text-xs font-medium px-2 py-0.5 rounded-full">
              {data.length} {data.length === 1 ? 'resultado' : 'resultados'}
            </span>
          ) : null}
        </div>
      </div>

      {/* Contenido */}
      <div className="p-4">
        {loading ? (
          <SubtleLoader message={GOODS_TABLE_STAGES[currentMessageIndex].text} />
      ) : data.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-light-gray">
                {headers.map((header, index) => (
                  <th 
                    key={index}
                    className="text-left py-4 px-4 text-small font-semibold text-charcoal-gray uppercase tracking-wide"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr 
                  key={index}
                  className={classNames(
                    "border-b border-light-gray transition-colors duration-200 hover:bg-light-gray/50",
                    index % 2 === 0 ? "bg-pure-white" : "bg-light-gray/30"
                  )}
                >
                  {Object.values(item).map((value: any, cellIndex) => (
                    <td 
                      key={cellIndex}
                      className="py-4 px-4 text-body-sm text-charcoal-gray"
                    >
                      {typeof value === 'number' && value > 1000
                        ? (headers[cellIndex]?.toLowerCase() === 'año' 
                            ? value
                            : `$${value.toLocaleString('es-CL')}`)
                        : value || '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-6">
          <div className="w-12 h-12 mx-auto mb-3 bg-light-gray rounded-full flex items-center justify-center">
            <IconSearch size={20} className="text-medium-gray" />
          </div>
          <p className="text-body-sm text-charcoal-gray font-medium">No se encontraron resultados</p>
          <p className="text-small text-medium-gray mt-1">Intenta con otro criterio de búsqueda</p>
        </div>
      )}
    </div>
  </div>
  );
};

const GoodsTable = ({ className, goods, loading = false, loadingStates }: GoodsTableProps) => {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  useEffect(() => {
    if (loading && !loadingStates) {
      setCurrentMessageIndex(0);
      const timeoutIds: NodeJS.Timeout[] = [];

      const scheduleNextMessage = (index: number) => {
        if (index >= GOODS_TABLE_STAGES.length - 1) {
          return;
        }
        
        const nextIndex = index + 1;
        const timeoutId = setTimeout(() => {
          setCurrentMessageIndex(nextIndex);
          scheduleNextMessage(nextIndex);
        }, GOODS_TABLE_STAGES[index].delay);
        
        timeoutIds.push(timeoutId);
      };

      scheduleNextMessage(0);

      return () => {
        timeoutIds.forEach(id => clearTimeout(id));
      };
    }
  }, [loading, loadingStates]);

  if (loading && !loadingStates) {
    return (
      <div className={classNames("bg-pure-white rounded-xl border border-medium-gray shadow-sm", className)}>
        <SubtleLoader message={GOODS_TABLE_STAGES[currentMessageIndex].text} />
      </div>
    );
  }

  // Verificar si hay algún loading activo
  const isAnyLoading = loadingStates?.societies || loadingStates?.vehicles || loadingStates?.properties || loading;
  
  // Solo mostrar "no se encontraron bienes" si no hay loading y no hay resultados
  if (!isAnyLoading && goods.societies.length === 0 && goods.vehicles.length === 0 && goods.properties.length === 0) {
    return (
      <div className={classNames("bg-pure-white rounded-xl border border-medium-gray shadow-sm p-8", className)}>
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-6 bg-light-gray rounded-full flex items-center justify-center">
            <IconSearch size={32} className="text-medium-gray" />
          </div>
          <h3 className="text-h3 font-semibold text-charcoal-gray mb-2">No se encontraron bienes</h3>
          <p className="text-body text-medium-gray">
            No se encontraron bienes asociados a la entidad solicitada.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={classNames("space-y-4", className)}>
      {/* Sección de Sociedades - Siempre visible */}
      <ModernTable
        title="Sociedades"
        icon={IconBuilding}
        headers={["Nombre de la Sociedad", "RUT", "Participación"]}
        data={goods.societies.map(society => ({
          societyName: society.societyName,
          rut: society.rut,
          participation: society.participation || 'No especificada'
        }))}
        loading={loadingStates?.societies}
        loadingMessage="Buscando sociedades..."
      />

      {/* Sección de Vehículos - Siempre visible */}
      <ModernTable
        title="Vehículos"
        icon={IconCar}
        headers={["Patente", "Marca", "Modelo", "Año", "Valor Fiscal"]}
        data={goods.vehicles.map(vehicle => ({
          patente: vehicle.patente,
          brand: vehicle.brand,
          model: vehicle.model,
          year: vehicle.year,
          fiscalValue: vehicle.fiscalValue
        }))}
        loading={loadingStates?.vehicles}
        loadingMessage="Buscando vehículos..."
      />

      {/* Sección de Propiedades - Siempre visible */}
      <ModernTable
        title="Propiedades"
        icon={IconHome}
        headers={["Dirección", "ROL", "Comuna", "Código Comuna", "Foja", "Número", "Año"]}
        data={goods.properties.map(property => ({
          address: property.address,
          rol: property.rol,
          comuna: property.comuna,
          comunaCode: property.comunaCode,
          foja: property.foja,
          number: property.number,
          year: property.year
        }))}
        loading={loadingStates?.properties}
        loadingMessage="Buscando propiedades..."
      />
    </div>
  );
};

export default GoodsTable;
