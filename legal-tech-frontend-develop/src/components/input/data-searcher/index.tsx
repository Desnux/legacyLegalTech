import { useState } from "react";
import classNames from "classnames";
import Button from "@/components/button";
import { GoodsTable } from "@/components/output";
import { getDefendantPropertyInformation, getDefendantSocietyInformation, getDefendantVehicleInformation } from "@/services/demand-text";
import { NewGoodsGroup } from "@/components/output/goods-table";
const DATA_SEARCH_PARTICIPANT_TYPES = [
  { value: 'defendant', label: 'Ejecutado' },
  { value: 'legal_representative', label: 'Representante Legal' },
  { value: 'guarantee', label: 'Aval' },
] as const;
import { Dropdown } from "@/components/input";
import { Participant } from "@/types/demand-text";

interface DataSearcherProps {
  className?: string;
  label?: string;
  onIncorporate?: (content: string) => void;
  participants?: Participant[];
}

const DataSearcher = ({ className, label = "Bienes Embargables", onIncorporate, participants }: DataSearcherProps) => {
  const [goodsQuery, setGoodsQuery] = useState<string>("");
  const [goodsResult, setGoodsResult] = useState<NewGoodsGroup | null>(null);
  const [loadingStates, setLoadingStates] = useState<{
    societies: boolean;
    vehicles: boolean;
    properties: boolean;
  }>({
    societies: false,
    vehicles: false,
    properties: false,
  });
  const [accumulatedContent, setAccumulatedContent] = useState<string>("");

  const selectableParticipants = participants?.filter(p => 
    p.role === 'defendant'  || p.role === 'guarantee'
  ) || [];

  const handleSearch = async () => {
    const normalize = (text: string) =>
      text
        .toLowerCase()
        .replace(/[.\s]/g, "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");
  
    // Inicializar loadings individuales
    setLoadingStates({
      societies: true,
      vehicles: true,
      properties: true,
    });
    
    await new Promise((resolve) => setTimeout(resolve, 500));

    const query = normalize(goodsQuery);
    
    // Inicializar con estructura vacía
    const initialResult: NewGoodsGroup = {
      societies: [],
      vehicles: [],
      properties: [],
    };
    
    setGoodsResult(initialResult);
    
    // Ejecutar las consultas en paralelo y actualizar resultados progresivamente
    const promises = [
      getDefendantSocietyInformation(query).then(societyRes => {
        setGoodsResult(prev => prev ? { ...prev, societies: societyRes } : { ...initialResult, societies: societyRes });
        setLoadingStates(prev => ({ ...prev, societies: false }));
        return societyRes;
      }).catch(() => {
        setLoadingStates(prev => ({ ...prev, societies: false }));
        return [];
      }),
      getDefendantVehicleInformation(query).then(vehicleRes => {
        setGoodsResult(prev => prev ? { ...prev, vehicles: vehicleRes } : { ...initialResult, vehicles: vehicleRes });
        setLoadingStates(prev => ({ ...prev, vehicles: false }));
        return vehicleRes;
      }).catch(() => {
        setLoadingStates(prev => ({ ...prev, vehicles: false }));
        return [];
      }),
      getDefendantPropertyInformation(query).then(propertyRes => {
        setGoodsResult(prev => prev ? { ...prev, properties: propertyRes } : { ...initialResult, properties: propertyRes });
        setLoadingStates(prev => ({ ...prev, properties: false }));
        return propertyRes;
      }).catch(() => {
        setLoadingStates(prev => ({ ...prev, properties: false }));
        return [];
      })
    ];
    
    // Esperar a que todas terminen
    await Promise.allSettled(promises);
  };


  const handleIncorporate = () => {
    if (onIncorporate === undefined || goodsResult === null) {
      return;
    }
    let content: string[] = [];
    let participation: string[] = [];

    const hasProperties = goodsResult.properties.length > 0;
    const hasVehicles = goodsResult.vehicles.length > 0;
    const hasSocieties = goodsResult.societies.length > 0;
    
    const selectedParticipant = selectableParticipants.find(p => {
      return p.dni === goodsQuery;
    });
    
    const participantRole = selectedParticipant 
      ? DATA_SEARCH_PARTICIPANT_TYPES.find(p => p.value === selectedParticipant.role)?.label 
      : null;
    
    
    if (hasProperties || hasVehicles || hasSocieties) {
      const roleText = participantRole ? `${participantRole}` : "";
      content.push(`Bienes encontrados para el ${roleText}:`);
    }

    goodsResult.properties.forEach((property) => {
      content.push(`- El inmueble inscrito a fojas ${property.foja} Nº ${property.number} del Registro de Propiedad del Conservador de Bienes Raíces de ${property.comuna} del año ${property.year}, ubicado en ${property.address}, ROL ${property.rol}.`);
    });

    goodsResult.vehicles.forEach((vehicle) => {
      const marcaText = vehicle.brand ? ` marca ${vehicle.brand}` : "";
      const modeloText = vehicle.model ? ` modelo ${vehicle.model}` : "";
      const anioText = vehicle.year ? ` del año ${vehicle.year}` : "";
      content.push(`- Vehículo${marcaText}${modeloText}, patente ${vehicle.patente}${anioText}, con valor fiscal de $${vehicle.fiscalValue.toLocaleString('es-CL')}.`);
    });

    goodsResult.societies.forEach((society) => {
      participation.push(`${society.societyName}, RUT Nº ${society.rut}${society.participation ? `, participación ${society.participation}` : ""}`);
    });

    if (participation.length > 0) {
      content.push("- La participación accionaria o derechos en las siguientes sociedades: " + participation.join("; ") + ".");
    }
    
    const newContent = content.join("\n");
    
    const updatedContent = accumulatedContent 
      ? `${accumulatedContent}\n\n${newContent}`
      : newContent;
    
    setAccumulatedContent(updatedContent);
    
    onIncorporate(updatedContent);
    
    setGoodsQuery("");
    setGoodsResult(null);
    setLoadingStates({ societies: false, vehicles: false, properties: false });
  };

  const handleClearAccumulated = () => {
    setAccumulatedContent("");
    if (onIncorporate) {
      onIncorporate("");
    }
  };

  return (
    <div className={classNames("flex flex-col gap-2", className)}>
      <div className="block text-h3 font-semibold text-petroleum-blue">{ label }</div>
      {(loadingStates.societies || loadingStates.vehicles || loadingStates.properties || goodsResult) && (
        <GoodsTable 
          goods={goodsResult || { societies: [], vehicles: [], properties: [] }} 
          loading={loadingStates.societies || loadingStates.vehicles || loadingStates.properties}
          loadingStates={loadingStates}
        />
      )}
      
      {accumulatedContent && (
        <div className="bg-pure-white rounded-xl border border-medium-gray shadow-sm overflow-hidden">
          {/* Header con gradiente */}
          <div className="bg-gradient-to-r from-teal-green/10 to-petroleum-blue/10 px-6 py-4 border-b border-medium-gray">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-teal-green/20 rounded-lg">
                  <svg className="w-5 h-5 text-teal-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <h4 className="text-h3 font-semibold text-petroleum-blue">Bienes a embargar</h4>
                  <p className="text-small text-medium-gray">Bienes encontrados para incorporar</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearAccumulated}
                className="text-red-500 hover:text-red-700 hover:bg-red-50"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Limpiar
              </Button>
            </div>
          </div>
          
          {/* Contenido */}
          <div className="p-6">
            <div className="bg-light-gray/50 rounded-lg p-4 max-h-48 overflow-y-auto">
              {(() => {
                const lines = accumulatedContent.split('\n');
                const sections: Array<{title: string, items: Array<{name: string, rut: string, type: string}>}> = [];
                let currentSection: string | null = null;
                let currentItems: Array<{name: string, rut: string, type: string}> = [];

                // Procesar el contenido para extraer secciones y elementos
                lines.forEach((line, index) => {
                  if (line.includes('Bienes encontrados para')) {
                    // Guardar sección anterior si existe
                    if (currentSection && currentItems.length > 0) {
                      sections.push({ title: currentSection, items: currentItems });
                    }
                    // Iniciar nueva sección
                    currentSection = line.replace(':', '').trim();
                    currentItems = [];
                  } else if (line.includes('siguientes sociedades:') && currentSection) {
                    // Extraer información de múltiples sociedades en una línea
                    const societyText = line.replace('- La participación accionaria o derechos en las siguientes sociedades: ', '').replace(/\.$/, '');
                    const societies = societyText.split('; ');
                    
                    societies.forEach(society => {
                      const match = society.match(/(.+),\s*RUT Nº\s*(\d{1,2}\.\d{3}\.\d{3}-?\d)/);
                      if (match) {
                        currentItems.push({
                          name: match[1].trim(),
                          rut: match[2],
                          type: 'Sociedad'
                        });
                      }
                    });
                  } else if (line.includes('RUT Nº') && currentSection && !line.includes('siguientes sociedades:')) {
                    // Extraer información de una sola sociedad
                    const match = line.match(/(.+),\s*RUT Nº\s*(\d{1,2}\.\d{3}\.\d{3}-?\d)/);
                    if (match) {
                      currentItems.push({
                        name: match[1].trim(),
                        rut: match[2],
                        type: 'Sociedad'
                      });
                    }
                  } else if (line.includes('patente') && currentSection) {
                    // Extraer información de vehículo
                    const match = line.match(/patente\s+([A-Z]{2}[A-Z0-9]{2}[0-9]{2})/);
                    if (match) {
                      currentItems.push({
                        name: `Vehículo ${match[1]}`,
                        rut: match[1],
                        type: 'Vehículo'
                      });
                    }
                  } else if (line.includes('ROL') && currentSection) {
                    // Extraer información de propiedad
                    const match = line.match(/ROL\s+(\d+)/);
                    if (match) {
                      currentItems.push({
                        name: `Propiedad ROL ${match[1]}`,
                        rut: match[1],
                        type: 'Propiedad'
                      });
                    }
                  }
                });

                // Agregar la última sección
                if (currentSection && currentItems.length > 0) {
                  sections.push({ title: currentSection, items: currentItems });
                }

                // Si no hay secciones pero hay contenido, intentar parsear directamente
                if (sections.length === 0 && accumulatedContent.trim()) {
                  // Intentar extraer sociedades directamente del contenido
                  const societyMatches = accumulatedContent.matchAll(/([^,]+),\s*RUT Nº\s*(\d{1,2}\.\d{3}\.\d{3}-?\d)/g);
                  const extractedSocieties = [];
                  let match;
                  while ((match = societyMatches.next().value) !== undefined) {
                    extractedSocieties.push({
                      name: match[1].trim(),
                      rut: match[2],
                      type: 'Sociedad'
                    });
                  }
                  
                  if (extractedSocieties.length > 0) {
                    return (
                      <div className="mb-6">
                        <h5 className="text-body font-semibold text-petroleum-blue mb-3 flex items-center gap-2">
                          <div className="w-2 h-2 bg-teal-green rounded-full"></div>
                          Bienes encontrados
                        </h5>
                        
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="border-b border-medium-gray">
                                <th className="text-left py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                                  Descripción
                                </th>
                                <th className="text-left py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                                  Identificador
                                </th>
                                <th className="text-center py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                                  Tipo
                                </th>
                                <th className="text-center py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                                  Estado
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {extractedSocieties.map((item, itemIndex) => (
                                <tr 
                                  key={itemIndex}
                                  className="border-b border-light-gray hover:bg-pure-white/50 transition-colors duration-200"
                                >
                                  <td className="py-3 px-3 text-body-sm text-charcoal-gray font-medium">
                                    {item.name}
                                  </td>
                                  <td className="py-3 px-3 text-body-sm text-charcoal-gray font-mono">
                                    {item.rut}
                                  </td>
                                  <td className="py-3 px-3 text-center">
                                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-petroleum-blue/10 text-petroleum-blue rounded-full">
                                      {item.type}
                                    </span>
                                  </td>
                                  <td className="py-3 px-3 text-center">
                                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-teal-green/10 text-teal-green rounded-full">
                                      <div className="w-1.5 h-1.5 bg-teal-green rounded-full mr-1"></div>
                                      Encontrado
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  }
                  
                  // Si no se pudo extraer nada, mostrar como texto
                  return (
                    <div className="text-body-sm text-charcoal-gray whitespace-pre-wrap">
                      {accumulatedContent}
                    </div>
                  );
                }

                return sections.map((section, sectionIndex) => (
                  <div key={sectionIndex} className="mb-6 last:mb-0">
                    <h5 className="text-body font-semibold text-petroleum-blue mb-3 flex items-center gap-2">
                      <div className="w-2 h-2 bg-teal-green rounded-full"></div>
                      {section.title}
                    </h5>
                    
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-medium-gray">
                            <th className="text-left py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                              Descripción
                            </th>
                            <th className="text-left py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                              Identificador
                            </th>
                            <th className="text-center py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                              Tipo
                            </th>
                            <th className="text-center py-2 px-3 text-small font-semibold text-charcoal-gray uppercase tracking-wide">
                              Estado
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {section.items.map((item, itemIndex) => (
                            <tr 
                              key={itemIndex}
                              className="border-b border-light-gray hover:bg-pure-white/50 transition-colors duration-200"
                            >
                              <td className="py-3 px-3 text-body-sm text-charcoal-gray font-medium">
                                {item.name}
                              </td>
                              <td className="py-3 px-3 text-body-sm text-charcoal-gray font-mono">
                                {item.rut}
                              </td>
                              <td className="py-3 px-3 text-center">
                                <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-petroleum-blue/10 text-petroleum-blue rounded-full">
                                  {item.type}
                                </span>
                              </td>
                              <td className="py-3 px-3 text-center">
                                <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-teal-green/10 text-teal-green rounded-full">
                                  <div className="w-1.5 h-1.5 bg-teal-green rounded-full mr-1"></div>
                                  Encontrado
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ));
              })()}
            </div>
            
            {/* Footer con estadísticas */}
            <div className="mt-4 flex items-center justify-between text-small text-medium-gray">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  {(() => {
                    const lines = accumulatedContent.split('\n');
                    let itemCount = 0;
                    
                    lines.forEach(line => {
                      if (line.includes('siguientes sociedades:')) {
                        // Contar sociedades en la línea de múltiples sociedades
                        const societyText = line.replace('- La participación accionaria o derechos en las siguientes sociedades: ', '').replace(/\.$/, '');
                        const societies = societyText.split('; ');
                        itemCount += societies.length;
                      } else if (line.includes('RUT Nº') && !line.includes('siguientes sociedades:')) {
                        itemCount++;
                      } else if (line.includes('patente') || line.includes('ROL')) {
                        itemCount++;
                      }
                    });
                    
                    return `${itemCount} ${itemCount === 1 ? 'bien encontrado' : 'bienes encontrados'}`;
                  })()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-teal-green rounded-full"></div>
                <span className="text-teal-green font-medium">Listo para incorporar</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="flex gap-x-2 text-xs md:text-sm">
        {selectableParticipants.length > 0 ? (
                      <Dropdown
              placeholder="Seleccionar RUT de demandado"
              options={selectableParticipants.map(participant => ({
                value: participant.dni,
                label: `${DATA_SEARCH_PARTICIPANT_TYPES.find((p: any) => p.value === participant.role)?.label} - ${participant.dni} - ${participant.name}`
              }))}
              value={goodsQuery}
              onChange={(value) => setGoodsQuery(value)}
              disabled={loadingStates.societies || loadingStates.vehicles || loadingStates.properties}
              className="flex-1"
            />
        ) : (
          <input
            value={goodsQuery}
            maxLength={12}
            autoComplete="off"
            type="text"
            disabled={loadingStates.societies || loadingStates.vehicles || loadingStates.properties}
            placeholder="RUT"
            className={classNames("p-2 border rounded-lg outline-none bg-pure-white flex-1 border-medium-gray focus:border-teal-green focus:ring-1 focus:ring-teal-green/20 transition-colors duration-200")}
            onChange={(e) => setGoodsQuery(e.target.value)}
          />
        )}
        <Button
          variant="primary"
          size="sm"
          disabled={loadingStates.societies || loadingStates.vehicles || loadingStates.properties || goodsResult === null}
          className={classNames("text-left w-min", (loadingStates.societies || loadingStates.vehicles || loadingStates.properties || goodsResult === null) && "hidden")}
          onClick={handleIncorporate}
        >
          Incorporar
        </Button>
        <Button
          variant="primary"
          size="sm"
          disabled={loadingStates.societies || loadingStates.vehicles || loadingStates.properties || goodsQuery.trim().length === 0}
          onClick={handleSearch}
        >
          Buscar
        </Button>
      </div>
      <p className="mt-1 text-small text-charcoal-gray">
        Presione para buscar posibles bienes de los demandados, extraídos desde sitios web públicos.
      </p>
    </div>
  );
};

export default DataSearcher;