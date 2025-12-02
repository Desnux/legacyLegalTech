"use client";

import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { Tooltip } from "react-tooltip";
import classNames from "classnames";
import { useRouter, useSearchParams } from "next/navigation";
import { 
  IconCaretLeftFilled,
  IconCaretRightFilled,
  IconChevronDown,
  IconChevronUp,
  IconFileTypeZip,
  IconInfoCircleFilled,
  IconSelector,
  IconChevronRight,
  IconChevronLeft,
  IconFilter,
  IconSortAscending,
  IconFolder,
  IconAlertTriangle,
  IconUser,
  IconBolt,
  IconClock,
  IconCheck,
  IconHome,
  IconTrash,
  IconFileText,
  IconFileTypePdf,
} from "@tabler/icons-react";
import { Spinner } from "@/components/state";
import StatusBar from "@/components/case/status-bar";
import Dropdown from "@/components/input/dropdown";
import { CaseListType, CaseListResponse,  CaseStatsParams } from "@/types/case";
import { formatDate } from "@/utils/date";
import { translatedEventNames } from "@/utils/event-types";
import { formatCurrency } from "@/utils/currency";
import { translatedLegalSubjects } from "@/utils/case-details";

const FILTER_OPTIONS = [
  { id: "draft", label: "Preparación", icon: IconFolder, count: 0 },
  { id: "active", label: "Activo", icon: IconBolt, count: 0 },
  { id: "finished", label: "Terminado", icon: IconCheck, count: 0 },
  { id: "archived", label: "Archivado", icon: IconClock, count: 0 }
];

const ORDER_BY = [
  { id: "status", label: "Estado" },
  { id: "created_at", label: "Fecha de creación" },
  { id: "events", label: "Eventos" }
];

const AMOUNT_FILTERS = [
  { value: "all", label: "Todos los montos" },
  { value: "0-50", label: "0 - 50 millones" },
  { value: "50-100", label: "50 - 100 millones" },
  { value: "100-150", label: "100 - 150 millones" },
  { value: "150-200", label: "150 - 200 millones" },
  { value: "200+", label: "200+ millones" }
];

const resultsPerPage = 30;

const translations: Record<string, string> = {
  promisory_note_collection: "Cobro de pagaré",
  promissory_note_collection: "Cobro de pagaré",
  bill_collection: "Cobro de factura",
  plaintiffs: "Ejecutantes",
  defendants: "Ejecutados",
  active: "Activo",
  draft: "Preparación",
  finished: "Terminado",
  notification: "Notificación",
  demand_start: "Ingreso demanda",
  documents: "Preparación documentos",
  asset_seizure: "Traba de embargo",
  demand_text: "Ingreso demanda",
  dispatch_resolution: "Resolución despáchese",
  legal_sentence: "Sentencia",
  exceptions: "Excepciones",
  exceptions_response: "Respuesta a excepciones",
  "To be assigned": "Por Definir",
};

interface CaseListProps {
  title: string;
  subtitle: string;
  linkedCases?: boolean;
  onDownload?: () => Promise<void>;
  onFetch: (params: CaseStatsParams) => Promise<CaseListResponse>;
  params: { bank?: string };
}

const CaseList = ({ title, subtitle, linkedCases = false, onDownload, onFetch, params }: CaseListProps) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialOrderBy = searchParams.get("order_by") || "created_at";
  const initialOrderDirection = 
    searchParams.get("order_direction") === "asc" || 
    searchParams.get("order_direction") === "desc"
      ? (searchParams.get("order_direction") as "asc" | "desc")
      : "desc";
  const [cases, setCases] = useState<CaseListType[]>([]);
  const [caseCount, setCaseCount] = useState<number>(0);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [filters, setFilters] = useState<string[]>(() => {
    const params = new URLSearchParams(searchParams.toString());
    return params.getAll("status") || [];
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [orderBy, setOrderBy] = useState<string>(initialOrderBy);
  const [orderDirection, setOrderDirection] = useState<"asc" | "desc">(initialOrderDirection);
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [amountFilter, setAmountFilter] = useState<string>("all");
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const { bank } = params;
  const currentPage = searchParams.get("page") ? parseInt(searchParams.get("page")!, 10) : 1;

  const handleDownload = async () => {
    if (downloading || onDownload === undefined) {
      return;
    }
    setDownloading(true);
    try {
      await onDownload();
    } catch (error) {
      toast.error("No fue posible descargar los casos");
      console.error("Error downloading file:", error);
    } finally {
      setDownloading(false);
    }
  };

  const handleDirectionToggle = () => {
    const newDirection = orderDirection === "asc" ? "desc" : "asc";
    setOrderDirection(newDirection);
    const params = new URLSearchParams(searchParams.toString());
    params.set("order_direction", newDirection);
    router.push(`?${params.toString()}`);
  };

  const handleOrderBy = (id: string) => {
    const newOrderBy = orderBy === id ? orderBy : id;
    setOrderBy(newOrderBy);
    const params = new URLSearchParams(searchParams.toString());
    params.set("order_by", newOrderBy);
    if (!params.has("order_direction")) {
      params.set("order_direction", orderDirection);
    }
    router.push(`?${params.toString()}`);
  };

  const toggleFilter = (id: string) => {
    const newFilters = filters.includes(id) ? [] : [id];
    setFilters(newFilters);
  };

  const toggleRowExpansion = (caseId: string) => {
    const newExpandedRows = new Set(expandedRows);
    if (newExpandedRows.has(caseId)) {
      newExpandedRows.delete(caseId);
    } else {
      newExpandedRows.add(caseId);
    }
    setExpandedRows(newExpandedRows);
  };

  const handleDetailClick = (caseId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    router.push(`/case/${caseId}`);
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      if (sortDirection === "asc") {
        setSortDirection("desc");
      } else {
        setSortField(null);
        setSortDirection("asc");
      }
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };
  
  useEffect(() => {
    const queryParams: Record<string, string | string[]> = {};
    const pageParam = searchParams.get("page");
    const page = pageParam ? parseInt(pageParam, 10) : 1;
    const limit = resultsPerPage;
    const skip = (page - 1) * limit;
    if (bank) {
      queryParams["bank"] = bank;
    }
    queryParams["skip"] = skip.toString();
    queryParams["limit"] = limit.toString();

    searchParams.forEach((value, key) => {
      if (!["bank", "page", "skip", "limit"].includes(key)) {
        if (queryParams[key]) {
          queryParams[key] = Array.isArray(queryParams[key])
            ? [...(queryParams[key] as string[]), value]
            : [queryParams[key] as string, value];
        } else {
          queryParams[key] = value;
        }
      }
    });

    if (!queryParams["order_by"]) {
      queryParams["order_by"] = orderBy;
      queryParams["order_direction"] = orderDirection;
    }

    setLoading(true);
    onFetch(queryParams)
      .then((data) => {
        setCases(data.cases);
        setCaseCount(data.case_count);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching cases:", error);
        toast.error("No fue posible obtener los casos");
        setLoading(false);
      });
  }, [searchParams, bank, orderBy, orderDirection, onFetch]);

  const casesFilteredBySearchAndAmount = cases.filter(c => {
    const searchMatch = !searchTerm || 
      (c.court && c.court.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (c.created_at && formatDate(c.created_at).toLowerCase().includes(searchTerm.toLowerCase())) ||
      (c.latest_step && translatedEventNames[c.latest_step] && translatedEventNames[c.latest_step].toLowerCase().includes(searchTerm.toLowerCase())) ||
      (translations[c.status] && translations[c.status].toLowerCase().includes(searchTerm.toLowerCase()));
    
    const amountMatch = amountFilter === "all" || (() => {
      const amount = c.amount;
      switch (amountFilter) {
        case "0-50":
          return amount >= 0 && amount <= 50000000;
        case "50-100":
          return amount > 50000000 && amount <= 100000000;
        case "100-150":
          return amount > 100000000 && amount <= 150000000;
        case "150-200":
          return amount > 150000000 && amount <= 200000000;
        case "200+":
          return amount > 200000000;
        default:
          return true;
      }
    })();
    
    return searchMatch && amountMatch;
  });

  const filterCounts = {
    draft: casesFilteredBySearchAndAmount.filter(c => c.status === "draft").length,
    active: casesFilteredBySearchAndAmount.filter(c => c.status === "active").length,
    finished: casesFilteredBySearchAndAmount.filter(c => c.status === "finished").length,
    archived: casesFilteredBySearchAndAmount.filter(c => c.status === "archived").length,
  };

  const filteredCases = casesFilteredBySearchAndAmount.filter(c => {
    const statusMatch = filters.length === 0 || filters.includes(c.status);
    return statusMatch;
  });

  const sortedCases = [...filteredCases].sort((a, b) => {
    const activeSort = sortField || orderBy;
    const activeDirection = sortField ? sortDirection : orderDirection;
    
    if (!activeSort) return 0;
    
    let aValue: any;
    let bValue: any;
    
    switch (activeSort) {
      case "plaintiff":
        aValue = a.litigants.find((l) => l.role === 'plaintiff')?.name || "";
        bValue = b.litigants.find((l) => l.role === 'plaintiff')?.name || "";
        break;
      case "defendant":
        aValue = a.litigants.find((l) => l.role === 'defendant')?.name || "";
        bValue = b.litigants.find((l) => l.role === 'defendant')?.name || "";
        break;
      case "created_at":
        aValue = a.created_at;
        bValue = b.created_at;
        break;
      case "legal_subject":
        aValue = translatedLegalSubjects[a.legal_subject] || "";
        bValue = translatedLegalSubjects[b.legal_subject] || "";
        break;
      case "amount":
        aValue = a.amount || 0;
        bValue = b.amount || 0;
        break;
      case "tribunal":
        aValue = translations[a.tribunal] || a.tribunal || "";
        bValue = translations[b.tribunal] || b.tribunal || "";
        break;
      case "status":
        aValue = translations[a.status] || a.status;
        bValue = translations[b.status] || b.status;
        break;
      case "latest_step":
        aValue = translatedEventNames[a.latest_step] || "";
        bValue = translatedEventNames[b.latest_step] || "";
        break;
      case "events":
        aValue = a.events?.length || 0;
        bValue = b.events?.length || 0;
        break;
      default:
        return 0;
    }
    
    if (aValue === null || aValue === undefined) return 1;
    if (bValue === null || bValue === undefined) return -1;
    
    let comparison = 0;
    if (typeof aValue === "string" && typeof bValue === "string") {
      comparison = aValue.localeCompare(bValue);
    } else {
      comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    }
    
    return activeDirection === "desc" ? -comparison : comparison;
  });

  const totalPages = Math.ceil(caseCount / resultsPerPage);

  const getSortIcon = (field: string) => {
    const activeSort = sortField || orderBy;
    const activeDirection = sortField ? sortDirection : orderDirection;
    
    if (activeSort !== field) {
      return <IconSelector size={16} className="text-gray-400 ml-1" />;
    }
    return activeDirection === "asc" 
      ? <IconSortAscending size={16} className="text-teal-600 ml-1" />
      : <IconSortAscending size={16} className="text-teal-600 ml-1 transform rotate-180" />;
  };

  return (
    <div className="my-6 flex flex-col flex-1 rounded-2xl shadow-lg border border-medium-gray bg-pure-white">
      <div className="">
        <div className="m-8">
          <h1 className="text-h2 font-serif text-petroleum-blue mb-1">
            { title }
          </h1>
          <p className="text-body-sm text-charcoal-gray max-w-2xl">
            { subtitle }
          </p>
        </div>

        { cases.length > 0 && onDownload !== undefined && (
          <button 
            className={classNames(
              "shrink-0 text-gray-50 py-1 px-1 md:px-1.5 flex gap-x-2 rounded-lg hover:bg-blue-600 bg-blue-700 justify-center",
              downloading && "cursor-not-allowed",
            )}
            disabled={downloading}
            onClick={handleDownload}
          >
            <div className="flex-1 hidden md:block select-none">Descargar</div>
            <IconFileTypeZip/>
          </button>
        )}
      </div>

      {/* Filters and Sorting */}
      <div className="flex items-center justify-between px-6 py-3 border-t border-gray-200 mb-4 md:mb-6">
        <div className="flex items-center gap-8 lg:gap-10">
          {/* Buscador */}
          <div className="flex items-center gap-2">
            <IconFilter size={16} className="text-gray-600" />
            <span className="text-sm text-gray-600">Buscar:</span>
            <input
              type="text"
              placeholder="Buscar en casos..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white border border-gray-300 text-gray-700 text-sm rounded-lg px-3 h-9 w-72 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Limpiar búsqueda"
              >
                <IconTrash size={16} className="text-red-600" />
              </button>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <IconFilter size={16} className="text-gray-600" />
            <span className="text-sm text-gray-600">Filtrar por monto:</span>
            <Dropdown
              options={AMOUNT_FILTERS}
              value={amountFilter}
              onChange={setAmountFilter}
              placeholder="Seleccionar rango"
              className="w-56"
            />
          </div>
        </div>
      </div>

      {/* Status Navigation */}
      <div className="flex items-center gap-3 overflow-x-auto px-6 pb-2">
        <button 
          onClick={() => {
            setFilters([]);
          }}
          className={classNames(
            "flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors",
            filters.length === 0 
              ? "bg-blue-600 text-white" 
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          )}
        >
          <IconFolder size={16} />
          <span>Todos</span>
          <span className={classNames(
            "text-xs px-2 py-0.5 rounded-full",
            filters.length === 0 
              ? "bg-blue-500 text-white" 
              : "bg-gray-200 text-gray-700"
          )}>{sortedCases.length}</span>
        </button>
        {FILTER_OPTIONS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => toggleFilter(id)}
            className={classNames(
              "flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors",
              filters.includes(id)
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-blue-200"
            )}
          >
            <Icon size={16} />
            <span>{label}</span>
            <span className={classNames(
              "text-xs px-2 py-0.5 rounded-full",
              filters.includes(id)
                ? "bg-blue-500 text-white"
                : "bg-gray-200 text-gray-700"
            )}>{filterCounts[id as keyof typeof filterCounts] || 0}</span>
          </button>
        ))}
      </div>
      
              {loading ? (
          <Spinner className="flex-1"/>
        ) : (
          <div className="flex flex-col flex-1">
            {cases.length === 0 && (
              <div className="text-center flex flex-col justify-center items-center text-gray-700 w-full flex-1">
                Sin casos
              </div>
            )}
            
            {cases.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse bg-pure-white overflow-hidden">
                  <thead className="bg-gray-50">
                    <tr>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("plaintiff")}
                      >
                        <div className="flex items-center select-none">
                          Demandante
                          {getSortIcon("plaintiff")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("defendant")}
                      >
                        <div className="flex items-center select-none">
                          Demandado
                          {getSortIcon("defendant")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("created_at")}
                      >
                        <div className="flex items-center select-none">
                          Fecha Creación
                          {getSortIcon("created_at")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("legal_subject")}
                      >
                        <div className="flex items-center select-none">
                          Documento
                          {getSortIcon("legal_subject")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("amount")}
                      >
                        <div className="flex items-center select-none">
                          Monto
                          {getSortIcon("amount")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200"
                      >
                        <div className="flex items-center select-none">
                          Rol-Año
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("tribunal")}
                      >
                        <div className="flex items-center select-none">
                          Juzgado
                          {getSortIcon("tribunal")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("status")}
                      >
                        <div className="flex items-center select-none">
                          Estado
                          {getSortIcon("status")}
                        </div>
                      </th>
                      <th 
                        className="px-5 py-2.5 text-left text-xs font-semibold tracking-wide uppercase text-gray-600 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                        onClick={() => handleSort("latest_step")}
                      >
                        <div className="flex items-center select-none">
                          Hito
                          {getSortIcon("latest_step")}
                        </div>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedCases.map((c, index) => {
                      const isExpanded = expandedRows.has(c.id);
                      const plaintiff = c.litigants.find((l) => l.role === 'plaintiff')?.name || "Sin Definir";
                      const defendant = c.litigants.find((l) => l.role === 'defendant')?.name || "Sin Definir";
                      const legal_representative = c.litigants.find((l) => l.role === 'legal_representative')?.name || "Sin Definir";
                      const plaintiff_legal_representative = c.litigants.find((l) => l.role === 'plaintiff_legal_representative')?.name || "Sin Definir";
                      const sponsoring_attorney = c.litigants.find((l) => l.role === 'sponsoring_attorney')?.name || "Sin Definir";
                      return (
                        <React.Fragment key={c.id}>
                          <tr 
                            key={c.id}
                            className={classNames(
                              "border-b border-gray-100 transition-colors ease-in-out cursor-pointer table-row",
                              isExpanded && "bg-gray-100 hover:bg-gray-50",
                              !isExpanded && (index % 2 === 0 ? "bg-white hover:bg-gray-50" : "bg-gray-50 hover:bg-gray-50")
                            )}
                            onClick={(e) => handleDetailClick(c.id, e)}
                          >
                            <td className="pl-6 pr-4 py-2.5 text-sm text-gray-900 font-medium">
                              <div className="flex items-center gap-2 min-w-0">
                                <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      toggleRowExpansion(c.id);
                                    }}
                                    className="p-1 hover:bg-gray-200 rounded transition-all duration-200 shrink-0"
                                    title={isExpanded ? "Contraer" : "Expandir"}
                                  >
                                    <div className={classNames(
                                      "expand-icon transition-transform duration-200",
                                      isExpanded && "expanded"
                                    )}>
                                      <IconChevronRight size={16} className="text-gray-600" />
                                    </div>
                                  </button>
                                  <span className="truncate" title={plaintiff}>{plaintiff}</span>
                              </div>
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-900 font-medium">
                              {defendant}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-700">
                              {c.created_at ? formatDate(c.created_at) : "N/A"}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-700">
                              {translatedLegalSubjects[c.legal_subject] || "Sin Definir"}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-900">
                              {formatCurrency(c.amount)}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-700">
                              {c.rol ? c.rol : "-"}-{c.year ? c.year : "-"}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-700">
                              {translations[c.tribunal] || c.tribunal}
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-900">
                              <span className={classNames(
                                "px-2 py-1 rounded-full text-xs font-medium",
                                {
                                  "bg-blue-100 text-blue-800": c.status === "active",
                                  "bg-yellow-100 text-yellow-800": c.status === "draft",
                                  "bg-green-100 text-green-800": c.status === "finished",
                                  "bg-gray-100 text-gray-800": c.status === "archived"
                                }
                              )}>
                                {translations[c.status] || c.status}
                              </span>
                            </td>
                            <td className="px-5 py-2.5 text-sm text-gray-700">
                              {translatedEventNames[c.latest_step] || "Sin Hito"}
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr key={`${c.id}-expanded`} className="bg-gray-50 animate-expand">
                              <td colSpan={9} className="px-6 py-2">
                                <div className="flex flex-col gap-6 animate-fadeIn">
                                  {/* Título con icono */}
                                  <div className="flex items-center gap-3 mb-1">
                                    <IconFileText size={20} className="text-blue-600" />
                                    <h3 className="text-lg font-semibold text-gray-800">Detalles del Caso</h3>
                                  </div>
                                  
                                  {/* Detalles del caso en dos columnas */}
                                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                    {/* Columna izquierda */}
                                    <div className="flex flex-col gap-4">
                                      <div>
                                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Representante Ejecutado:</h4>
                                        <p className="text-sm text-gray-600">
                                          {legal_representative}
                                        </p>
                                      </div>

                                    </div>
                                    
                                    {/* Columna central */}
                                    <div className="flex flex-col gap-4">
                                      <div>
                                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Representante demandante:</h4>
                                        <p className="text-sm text-gray-600">
                                          {plaintiff_legal_representative}
                                        </p>
                                      </div>
                                    </div>

                                    <div className="flex flex-col gap-4">
                                      <div>
                                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Abogado Patrocinante:</h4>
                                        <p className="text-sm text-gray-600">
                                          {sponsoring_attorney}
                                        </p>
                                      </div>
                                    </div>

                                    <div className="flex flex-col gap-4">
                                      <div>
                                          <h4 className="text-sm font-semibold text-gray-700 mb-2">Archivo Demanda:</h4>
                                          <button
                                            onClick={() => {
                                              // TODO: Implementar descarga/visualización del PDF
                                              console.log('PDF Demanda clicked for case:', c.id);
                                            }}
                                            className="flex items-center gap-2 px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-colors duration-200"
                                            title="Ver PDF de la demanda"
                                          >
                                            <IconFileTypePdf size={16} />
                                            <span className="text-sm">Ver PDF</span>
                                          </button>
                                        </div>
                                    </div>
                                    
                                  </div>
                                  
                                  {/* Barra de progreso */}
                                  <div className="border-t py-2">
                                    <div className="flex items-center justify-center mb-3">
                                      <h4 className="text-sm font-semibold text-gray-700">Progreso del caso:</h4>
                                    </div>
                                    <div className="flex justify-center">
                                      <StatusBar receivedEvents={c.events || []}/>
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      <div className={classNames(
        "justify-center my-2",
        sortedCases.length === 0 && "hidden",
        sortedCases.length > 0 && "flex",
      )}>
        <button
          className={classNames(
            "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
            currentPage > 1 && "text-blue-700 hover:text-blue-800",
            currentPage <= 1 && "text-gray-600",
          )}
          disabled={currentPage <= 1}
          onClick={() => {
            const params = new URLSearchParams(searchParams.toString());
            params.set("page", (currentPage - 1).toString());
            router.push(`?${params.toString()}`);
          }}
        >
          <IconCaretLeftFilled/>
        </button>
        <span className="px-4 py-2 mx-2 text-sm md:text-base">
          {totalPages > 0 ? currentPage : 0} / {totalPages}
        </span>
        <button
          className={classNames(
            "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
            currentPage < totalPages && "text-blue-700 hover:text-blue-800",
            currentPage >= totalPages && "text-gray-600",
          )} 
          disabled={currentPage >= totalPages}
          onClick={() => {
            const params = new URLSearchParams(searchParams.toString());
            params.set("page", (currentPage + 1).toString());
            router.push(`?${params.toString()}`);
          }}
        >
          <IconCaretRightFilled/>
        </button>
      </div>
    </div>
  );
}

export default CaseList;
