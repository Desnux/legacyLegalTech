import React, { useEffect, useState } from "react";
import { toast, ToastContainer } from "react-toastify";
import { IconEdit, IconCheck, IconSearch, IconChevronDown, IconChevronUp } from "@tabler/icons-react";
import Advent from "@/components/case/advent";
import MilestoneTable from "@/components/case/milestone-table";
import { FullPageOverlay } from "@/components/loading";
import { Spinner } from "@/components/state";
import { Dropdown } from "@/components/input";
import { createDetails, fetchCaseDetails, fetchCaseEvents } from "@/services/case";
import { Case, CreateCaseDetail, Tribunal, Court } from "@/types/case";
import { Milestone } from "@/types/milestone";
import "react-toastify/dist/ReactToastify.css";
import { Event } from "@/types/event";
import { Receptor, Tasks } from "@/types/recepthor";
import { formatDate, formatProcedureDate } from "@/utils/date";
import NotificationModal from "../notification";
import { fetchAllFolios, fetchFolioFromPjud, scrapeCaseNotebook } from "@/services/pjud";
import { Folio } from "@/types/pjud";
import { fetchTribunals } from "@/services/tribunal";
import { fetchCourts } from "@/services/court";
import CaseEvents from "../case-events";
import LastMilestone from "../last-milestone";
import ActionsCard from "../actions-card";
import Quotes from "../quotes";
import ReceptorsList from "../receptors-list";
import { partyLabels, partyRoles, statusColors, statusLabels, translatedLegalSubjects } from "@/utils/case-details";
import { RECEPTORS_MOCK_DATA, TASKS_MOCK_DATA } from "@/utils/test-data";
import SubtleLoader from "@/components/loading/subtle-loader";
import { fetchReceptors, fetchReceptorsByTribunalId, ReceptorsResponse } from "@/services/receptor";

type Props = {
  caseId: string;
};

const CaseDetails: React.FC<Props> = ({ caseId }) => {
  const [caseData, setCaseData] = useState<Case | null>(null);
  const [relatedEvents, setRelatedEvents] = useState<Event[]>([]);
  const [tribunalsData, setTribunalsData] = useState<Tribunal[] | null>(null);
  const [courtsData, setCourtsData] = useState<Court[] | null>(null);
  const [eventsData, setEventsData] = useState<Event[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [lastMilestone, setLastMilestone] = useState<Milestone | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingFolios, setLoadingFolios] = useState(false);
  const [loadingCompromise, setLoadingCompromise] = useState(false);
  const [loadingScraper, setLoadingScraper] = useState(false);
  const [toastMessage, setToastMessage] = useState<string>("");
  const [receptorsData, setReceptorsData] = useState<ReceptorsResponse[]>([]);
  const [isNotificationModalVisible, setIsNotificationModalVisible] = useState(false);
  const [tasksData, setTasksData] = useState<Tasks | null>(null);
  const [rolValue, setRolValue] = useState<number | null>(null);
  const [tribunalValue, setTribunalValue] = useState("");
  const [courtValue, setCourtValue] = useState("");
  const [yearValue, setYearValue] = useState("");
  const [updatingCase, setUpdatingCase] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isParticipantsVisible, setIsParticipantsVisible] = useState(false);
  const [creationDate, setCreationDate] = useState<string | null>(null);

  const loadCaseData = async () => {
    try {
      setLoading(true);
      const data = await fetchCaseDetails(caseId);
      if (!data) {
        toast.error("No se encontró el caso");
        return;
      }
      setCaseData(data);
      setCreationDate(data.created_at ? formatDate(data.created_at) : null);
      if(data.details === null) {
        const courtsData = await fetchCourts();
        setCourtsData(courtsData);
        const tribunalsData = await fetchTribunals();
        setTribunalsData(tribunalsData);
      } else {
        // const tasksData = await fetchTaskByCaseId(data.case_recepthor_id || caseId);
        // setTasksData(tasksData);

        if(data.details.tribunal && data.details.tribunal.recepthor_id) {
          try {
            const tribunalId = data.details.tribunal.recepthor_id;
            const receptorsData = await fetchReceptors(); //TODO: change to fetchReceptorsByTribunalId
            setReceptorsData(receptorsData);
          } catch (error) {
            console.error("Error al obtener receptores por tribunal:", error);
            toast.error("No se pudieron cargar los receptores del tribunal");
          }
        } else {
          console.warn("No se encontró tribunal o recepthor_id en los detalles del caso");
        }

        //FOR DEMO PURPOSES
        const tasksData = TASKS_MOCK_DATA.find((task) => task.firmCase.case.id === caseId);
        setTasksData(tasksData!);

        if(!tasksData) {
          //Disabled until Recepthor is working
          // const receptorsData = await fetchReceptorsByTribunalId(data.details.tribunal_id);
          // setReceptorsData(receptorsData);
        }
        const caseNumber = data.details.role
        await loadFoliosData(caseNumber, data.details.year);
      }

      await loadEventsData();
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  }

  const loadFoliosData = async (caseNumber: number, year: number) => {
    const foliosData = await fetchAllFolios(caseNumber, year);
    initializeMilestones(foliosData.items);
  }

  const loadEventsData = async () => {
    const eventsData = await fetchCaseEvents(caseId);
    const dispatchStartEvent = eventsData.find((event) => event.type === "dispatch_start");
    if(dispatchStartEvent) {
      setCreationDate(dispatchStartEvent.created_at);
    } else {
      setCreationDate(caseData?.created_at ?? null);
    }
    setEventsData(eventsData);
  }

  const initializeMilestones = (foliosData: Folio[]) => {
    if (foliosData && foliosData.length > 0) {
      const allMilestones = foliosData.map(folio => ({
        id: folio.id.toString(),
        folio: folio.folio.toString(),
        document: folio.doc ? [folio.doc] : [],
        annex: [],
        stage: folio.stage,
        procedure: folio.procedure,
        procedureDescription: folio.procedure_description,
        procedureDate: formatProcedureDate(folio.procedure_date.toString()),
        page: folio.page,
        actionToFollow: '',
        responsiblePerson: '',
        deadline: '',
        createdAt: new Date(folio.created_at).toISOString(),
        updatedAt: new Date(folio.updated_at).toISOString()
      }));
      
      if (allMilestones.length > 0) {
        const mostRecentMilestone = allMilestones.reduce((mostRecent, current) => {
          const mostRecentFolio = parseInt(mostRecent.folio || '0', 10);
          const currentFolio = parseInt(current.folio || '0', 10);
          return currentFolio > mostRecentFolio ? current : mostRecent;
        });
        
        const otherMilestones = allMilestones.filter(milestone => 
          milestone.folio !== mostRecentMilestone.folio
        ).sort((a, b) => parseInt(b.id) - parseInt(a.id));
        
        setLastMilestone(mostRecentMilestone);
        setMilestones(otherMilestones);
      } else {
        setLastMilestone(null);
        setMilestones([]);
      }
    }
  }

  const handleMilestoneClick = (milestone: Milestone) => {
    console.log('Milestone clicked:', milestone);
    // Aquí puedes agregar lógica para mostrar detalles del milestone
  };

  const handleDocumentClick = (documents: string[]) => {
    console.log('Documents clicked:', documents);
    // Aquí puedes agregar lógica para mostrar los documentos
  };

  const handleAnnexClick = (annexes: string[]) => {
    console.log('Annexes clicked:', annexes);
    // Aquí puedes agregar lógica para mostrar los anexos
  };

  const handleMilestoneUpdate = (index: number, updatedMilestone: Milestone) => {
    const updatedMilestones = [...milestones];
    updatedMilestones[index] = updatedMilestone;
    setMilestones(updatedMilestones);
    toast.success('Información del trámite actualizada correctamente');
  };



  const handleSaveCaseDetails = async () => {
    if (!caseData) return;
    
    if (!rolValue || !tribunalValue.trim() || !courtValue.trim() || !yearValue.trim()) {
      toast.error("Todos los campos son obligatorios");
      return;
    }
    
    try {
      setUpdatingCase(true);
      setToastMessage("Guardando cambios...");
      const caseDetails: CreateCaseDetail = {
        year: parseInt(yearValue),
        role: rolValue || 0,
        tribunal_id: tribunalValue,
        court_id: courtValue,
      };
      
      // const courtCode = courtsData!.find((court) => court.id === courtValue)?.code;
      // const tribunalCode = tribunalsData!.find((tribunal) => tribunal.id === tribunalValue)?.code;
      // if(!courtCode || !tribunalCode) {
      //   toast.error("No se encontraron los datos de la corte o tribunal");
      //   return;
      // }
      await createDetails(caseId, caseDetails);
      // const assignCaseRequest: SearchAndAssignCaseRequest = {
      //   bookType: 'C',
      //   competence: '3',
      //   court: courtCode?.toString(),
      //   rol: rolValue.toString(),
      //   tribunalCode: tribunalCode.toString(),
      //   year: yearValue,
      // };
      // await searchAndAssignCase(assignCaseRequest); // TODO: descomentar cuando recepthor este funcionando
      loadCaseData();
      setIsEditing(false);
    } catch (error: any) {
      toast.error(error.message);
    } finally {
      setUpdatingCase(false);
      setToastMessage("");
    }
  };

  const areAllFieldsFilled = () => {
    return rolValue !== null && tribunalValue.trim() !== "" && courtValue.trim() !== "" && yearValue.trim() !== "";
  };

  const handleCancelEdit = () => {
    setRolValue(caseData?.details?.role || null);
    setTribunalValue(caseData?.details?.tribunal_id || "");
    setCourtValue(caseData?.details?.court_id || "");
    setYearValue(caseData?.details?.year?.toString() || "");
    setIsEditing(false);
  };

  const handleStartEdit = () => {
    setIsEditing(true);
  };

  const getFolios = async () => {
    setLoadingFolios(true);
    try {
      if(!caseData || !caseData.details) {
        toast.error("No se encontraron detalles del caso");
        return;
      }
      await fetchFolioFromPjud({
        case_number: caseData.details.role.toString(),
        year: caseData.details.year,
        tribunal_id: caseData.details.tribunal_id,
        debug: false,
        save_to_db: true,
      }, caseId);
      const foliosData = await fetchAllFolios(caseData.details.role, caseData.details.year);
      initializeMilestones(foliosData.items);
      await loadEventsData();
    } catch (error) {
      toast.error("Error al obtener los folios desde PJUD, intentando cargar folios existentes...");
      try {
        if(caseData && caseData.details) {
          await loadFoliosData(caseData.details.role, caseData.details.year);
        }
      } catch (fallbackError) {
        toast.error("No se pudieron cargar los folios");
      }
    }
    finally {
      setLoadingFolios(false);
    }
  }

  const handleScrapeCaseNotebook = async () => {
    if(!caseData || !caseData.details) {
      toast.error("No se encontraron detalles del caso");
      return;
    }

    setLoadingScraper(true);
    try {
      await scrapeCaseNotebook(
        {
          case_number: caseData.details.role.toString(),
          year: caseData.details.year,
          tribunal_id: caseData.details.tribunal.id,
          debug: true,
          save_to_db: true,
        },
        caseId,
        0,
        100
      );
      toast.success("Scraper ejecutado correctamente");
      // Recargar los datos del caso después del scraper
      await loadCaseData();
    } catch (error: any) {
      toast.error(error.message || "Error al ejecutar el scraper");
    } finally {
      setLoadingScraper(false);
    }
  }

  useEffect(() => {
    if (caseData) {
      setRolValue(caseData.details?.role || null);
      setTribunalValue(caseData.details?.tribunal_id || "");
      setCourtValue(caseData.details?.court_id || "");
      setYearValue(caseData.details?.year?.toString() || "");
    }
  }, [caseData]);

  useEffect(() => {
    loadCaseData();
  }, [caseId]);

  if (loading) {
    return <Spinner className="flex-1 w-full h-full" />;
  }

  if (!caseData) {
    return <p>No se encontraron detalles del caso.</p>;
  }

  return (
    <div className="p-6 md:p-8 bg-white md:rounded-xl md:shadow-lg md:mb-4 relative">
      {/* Header del caso - Diseño más formal */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm mb-6 mt-1">
        <div className="px-6 py-3 border-b bg-teal-700 border-gray-100 rounded-t-lg">
          <h1 className="text-xl font-semibold text-white mb-1">{caseData.title}</h1>
        </div>
        <div className="px-6 py-3">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex flex-col">
              <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Materia Legal</span>
              <span className="text-sm text-gray-900 mt-1">{translatedLegalSubjects[caseData.legal_subject]}</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Estado</span>
              <div className="mt-1">
                <span className={statusColors[caseData.status] + " inline-flex px-3 py-1 rounded-full text-xs font-medium"}>
                  {statusLabels[caseData.status]}
                </span>
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-gray-500 uppercase tracking-wide">Fecha Presentación Demanda</span>
              <span className="text-sm text-gray-900 mt-1">{creationDate ?? "-"}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 grid-cols-1 md:grid-cols-4 mt-2 items-stretch">
        {/* Sección de detalles del caso */}
        <div className="md:col-span-2">
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-visible min-h-[230px] h-full">
            <div className="bg-teal-700 text-white px-6 py-3 min-h-[60px] rounded-t-lg">
              <h1 className="text-xl font-semibold text-white">
                Datos del caso en PJUD
              </h1>
            </div>
            <div className="">
            {/* Sección de campos faltantes */}
            {(!caseData.details) && (
              <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                      <span className="text-yellow-800 text-xs font-bold">!</span>
                    </div>
                    <h3 className="text-sm font-semibold text-yellow-800">
                      Falta ingresar datos del caso en PJUD
                    </h3>
                  </div>
                  {!isEditing && (
                    <button
                      onClick={handleStartEdit}
                      className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-white rounded-lg transition-colors duration-200 flex items-center gap-2 text-sm"
                    >
                      <IconEdit size={14} />
                      Editar
                    </button>
                  )}
                </div>
              </div>
            )}
            
            {/* Contenedor unificado para todos los campos */}
            {isEditing && (
            <div className="mt-4 p-6 bg-white border border-gray-200 rounded-lg shadow-sm relative overflow-visible">
              
              {/* Campo Rol */}
              <div className="text-sm md:text-base">
                <div className="flex items-center gap-2 mb-1">
                  <strong className="text-teal-700 font-semibold">Rol del caso</strong>
                  {!caseData.details?.role && (
                    <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full font-medium">
                      Requerido
                    </span>
                  )}
                </div>
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={rolValue || ""}
                      onChange={(e) => setRolValue(parseInt(e.target.value))}
                      className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-200 transition-colors duration-200 bg-white"
                      placeholder="Ingrese el rol del caso"
                      disabled={updatingCase}
                    />
                  </div>
              </div>

              {/* Campo Corte */}
              <div className="text-sm md:text-base mt-1">
                <div className="flex items-center gap-2 mb-1">
                  <strong className="text-teal-700 font-semibold">Corte</strong>
                  {!caseData.details?.court_id && (
                    <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full font-medium">
                      Requerido
                    </span>
                  )}
                </div>
                  <Dropdown
                    options={courtsData!.map((court) => ({
                      value: court.id,
                      label: court.name
                    }))}
                    value={courtValue}
                    onChange={(value) => setCourtValue(value)}
                    placeholder="Seleccionar corte"
                    disabled={updatingCase}
                  />
              </div>

              {/* Campo Tribunal */}
              <div className="text-sm md:text-base mt-1">
                <div className="flex items-center gap-2 mb-1">
                  <strong className="text-teal-700 font-semibold">Tribunal</strong>
                  {!caseData.details?.tribunal_id && (
                    <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full font-medium">
                      Requerido
                    </span>
                  )}
                </div>
                  <Dropdown
                    options={tribunalsData!.filter((tribunal) => tribunal.court_id === courtValue).map((tribunal) => ({
                      value: tribunal.id,
                      label: tribunal.name
                    })).sort((a, b) => a.label.localeCompare(b.label))}
                    value={tribunalValue}
                    onChange={(value) => setTribunalValue(value)}
                    placeholder="Seleccionar tribunal"
                    disabled={updatingCase || !courtValue}
                  />
              </div>

              {/* Campo Año */}
              <div className="text-sm md:text-base mt-1">
                <div className="flex items-center gap-2 mb-1">
                  <strong className="text-teal-700 font-semibold">Año</strong>
                  {!caseData.details?.year && (
                    <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full font-medium">
                      Requerido
                    </span>
                  )}
                </div>
                  <input
                    type="number"
                    value={yearValue}
                    onChange={(e) => setYearValue(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-200 transition-colors duration-200 bg-white"
                    placeholder="Ingrese el año (ej: 2024)"
                    min="2020"
                    max={new Date().getFullYear() + 1}
                    disabled={updatingCase}
                  />
              </div>

              {/* Botones de acción globales */}
                <div className="mt-6 flex justify-start gap-2">
                  <button
                    onClick={handleSaveCaseDetails}
                    disabled={updatingCase || !areAllFieldsFilled()}
                    className={`px-6 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2 ${
                      updatingCase || !areAllFieldsFilled()
                        ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                        : 'bg-teal-500 hover:bg-teal-600 text-white'
                    }`}
                  >
                    {updatingCase ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Guardando...
                      </>
                    ) : (
                      <>
                        <IconCheck size={16} />
                        Guardar Cambios
                      </>
                    )}
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    disabled={updatingCase}
                    className="px-6 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Cancelar
                  </button>
                </div>
            </div>
            )}
            </div>
              <div className="grid grid-cols-2 gap-1 p-2">
                {/* Primera columna - Datos del caso */}
                <div className="col-span-1">
                  {caseData.details && (
                    <div className="">
                      <div className="">
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Rol del caso: </span>
                        <span className="ml-1 text-sm text-gray-900">{caseData.details.role}</span>
                      </div>
                      <div className="">
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Tribunal: </span>
                        <span className="ml-1 text-sm text-gray-900">{caseData.details.tribunal.name}</span>
                      </div>
                      <div className="">
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Corte: </span>
                        <span className="ml-1 text-sm text-gray-900">{caseData.details.court.name}</span>
                      </div>
                      <div className="">
                        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Año: </span>
                        <span className="ml-1 text-sm text-gray-900">{caseData.details.year}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Segunda columna - Etapa actual */}
                <div className="col-span-1">
                {caseData.details && (

                  <div className="">
                    <div className="">
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Etapa: </span>
                      <span className="ml-1 text-sm text-gray-900">{lastMilestone?.procedure || '-'}</span>
                    </div>
                    <div className="">
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Folio: </span>
                      <span className="ml-1 text-sm text-gray-900">{lastMilestone?.folio || '-'}</span>
                    </div>
                    <div className="">
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Fecha Folio: </span>
                      <span className="ml-1 text-sm text-gray-900">{lastMilestone?.procedureDate || '-'}</span>
                    </div>
                    <div className="">
                      <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Descripción: </span>
                      <span className="ml-1 text-sm text-gray-900">{lastMilestone?.procedureDescription || '-'}</span>
                    </div>
                  </div>
                )}
            </div>
          </div>
        </div>
        </div>

        {/* Componente de avenimiento */}
        <div className="md:col-span-2">
        <Advent
          caseId={caseData.id}
          status={caseData.status}
          lastEvent={'other'}
          loading={loadingCompromise}
          setLoading={setLoadingCompromise}
          winner={caseData.winner}
          stats={caseData.stats}
        />
        </div>

        <div className="bg-white border border-gray-200 rounded-lg shadow-sm md:col-span-4 h-full">
          <div className="px-6 py-3 border-b rounded-lg bg-teal-700 text-white border-gray-100">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-semibold text-white mb-1">Participantes</h1>
              <button
                onClick={() => setIsParticipantsVisible(!isParticipantsVisible)}
                className="flex items-center gap-2 px-3 py-1 bg-teal-800 hover:bg-teal-900 rounded-md transition-colors text-sm font-medium"
              >
                {isParticipantsVisible ? (
                  <>
                    <IconChevronUp size={16} />
                    Ocultar
                  </>
                ) : (
                  <>
                    <IconChevronDown size={16} />
                    Ver participantes
                  </>
                )}
              </button>
            </div>
          </div>
          <div 
            className={`overflow-hidden transition-all duration-300 ease-in-out ${
              isParticipantsVisible ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="px-6 py-5 md:py-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Columna Izquierda - Demandantes */}
                <div className="flex flex-col gap-4">
                  {caseData.litigants
                    .filter((litigant) => 
                      ['plaintiff', 'sponsoring_attorney', 'plaintiff_legal_representative'].includes(litigant.role)
                    )
                    .reduce((acc: any[], litigant) => {
                      if (litigant.role === 'legal_representative') {
                        const hasLegalRep = acc.some(item => item.role === 'legal_representative');
                        if (!hasLegalRep) {
                          acc.push(litigant);
                        }
                      } else {
                        acc.push(litigant);
                      }
                      return acc;
                    }, [])
                    .sort((a, b) => {
                      const order = ['plaintiff', 'sponsoring_attorney', 'plaintiff_legal_representative', 'legal_representative'];
                      return order.indexOf(a.role) - order.indexOf(b.role);
                    })
                    .map((litigant) => (
                      <div key={litigant.id || litigant.name} className="flex flex-col">
                        <span className="text-sm text-black font-bold uppercase tracking-wide">{partyRoles[litigant.role]}</span>
                        <span className="text-sm text-gray-900 mt-1">{litigant.name}</span>
                      </div>
                    ))}
                </div>
                
                {/* Columna Derecha - Demandados y otros */}
                <div className="flex flex-col gap-4">
                  {caseData.litigants
                    .filter((litigant) => 
                      ['defendant', 'guarantee', 'defendant_attorney', 'court', 'external_party'].includes(litigant.role)
                    )
                    .sort((a, b) => {
                      const order = ['defendant', 'guarantee', 'defendant_attorney', 'court', 'external_party'];
                      return order.indexOf(a.role) - order.indexOf(b.role);
                    })
                    .map((litigant) => (
                      <div key={litigant.id || litigant.name} className="flex flex-col">
                        <span className="text-sm text-black font-bold uppercase tracking-wide">{partyRoles[litigant.role]}</span>
                        <span className="text-sm text-gray-900 mt-1">{litigant.name}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="md:col-span-4">
          <ReceptorsList
            receptorsData={receptorsData}
            tribunalName={caseData.details?.tribunal.name}
            onCreateNotification={() => setIsNotificationModalVisible(true)}
          />
        </div>

        {/* Sección de Quotes */}
        <div className="md:col-span-3">
          <Quotes
            tasksData={tasksData!}
          />
        </div>

      
      </div>

      {/* Sección de Actions */}
      {lastMilestone && (
        <div>
        <ActionsCard
          caseId={caseId}
          milestone={lastMilestone!}
          onMilestoneClick={handleMilestoneClick}
          onDocumentClick={handleDocumentClick}
          onAnnexClick={handleAnnexClick}
          className="hidden"
        />
      </div>
      )}

      {/* Sección de milestones */}
      <div className="mt-6 mb-10">
        <MilestoneTable
          milestones={milestones}
          onMilestoneClick={handleMilestoneClick}
          onDocumentClick={handleDocumentClick}
          onAnnexClick={handleAnnexClick}
          onMilestoneUpdate={handleMilestoneUpdate}
          onScrapeCaseNotebook={caseData.details ? handleScrapeCaseNotebook : undefined}
          loadingScraper={loadingScraper}
          caseDetails={caseData.details}
        />
      </div>

      {/* Sección de eventos */}
      <CaseEvents
        events={eventsData}
        caseId={caseId}
        caseData={caseData}
        loadCaseData={loadCaseData}
        milestones={milestones}
        onDispatchStartDate={(date) => setCreationDate(
          date ? formatProcedureDate(date) : (caseData.created_at ? formatDate(caseData.created_at) : null)
        )}
      />
  
      <ToastContainer toastStyle={{ zIndex: 9999 }} />
      <FullPageOverlay isVisible={loadingCompromise || updatingCase} toastMessage={toastMessage} />
      

      <NotificationModal
          isVisible={isNotificationModalVisible}
          caseData={caseData}
          onClose={() => setIsNotificationModalVisible(false)}
          caseId={caseData.case_recepthor_id || caseId}
          receptors={receptorsData || []}
          onSuccess={loadCaseData}
      />
      
    </div>
  );
  
};

export default CaseDetails;
