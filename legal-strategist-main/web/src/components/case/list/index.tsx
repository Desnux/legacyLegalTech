"use client";

import { useEffect, useState } from "react";
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
} from "@tabler/icons-react";
import { Spinner } from "@/components/state";
import StatusBar from "@/components/case/status-bar";
import { CaseStats, CaseStatsParams, CaseStatsResponse } from "@/types/case";
import { formatDate } from "@/utils/date";

const FILTER_OPTIONS = [
  { id: "draft", label: "Preparación" },
  { id: "active", label: "Activo" },
  { id: "finished", label: "Terminado" },
  { id: "archived", label: "Archivado" }
];

const ORDER_BY = [
  { id: "title", label: "Caratulado" },
  { id: "created_at", label: "Fecha de creación" },
  { id: "events", label: "Eventos" }
];

const resultsPerPage = 10;

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
  exceptions_response: "Respuesta a excepciones"
};

interface CaseListProps {
  label: string;
  linkedCases?: boolean;
  onDownload?: () => Promise<void>;
  onFetch: (params: CaseStatsParams) => Promise<CaseStatsResponse>;
  params: { bank?: string };
}

const CaseList = ({ label, linkedCases = false, onDownload, onFetch, params }: CaseListProps) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialOrderBy = searchParams.get("order_by") || null;
  const initialOrderDirection = 
    searchParams.get("order_direction") === "asc" || 
    searchParams.get("order_direction") === "desc"
      ? (searchParams.get("order_direction") as "asc" | "desc")
      : null;
  const [cases, setCases] = useState<CaseStats[]>([]);
  const [caseCount, setCaseCount] = useState<number>(0);
  const [downloading, setDownloading] = useState<boolean>(false);
  const [filters, setFilters] = useState<string[]>(() => {
    const params = new URLSearchParams(searchParams.toString());
    return params.getAll("status") || [];
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [orderBy, setOrderBy] = useState<string | null>(initialOrderBy);
  const [orderDirection, setOrderDirection] = useState<"asc" | "desc" | null>(initialOrderDirection);
  const [showOrderDirection, setShowOrderDirection] = useState<boolean>(true);
  const { bank } = params;

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
    const newDirection =
      orderDirection === null ? "asc" : orderDirection === "asc" ? "desc" : null;
    setOrderDirection(newDirection);
    const params = new URLSearchParams(searchParams.toString());
    if (newDirection === null) {
      params.delete("order_direction");
    } else {
      params.set("order_direction", newDirection);
    }
    router.push(`?${params.toString()}`);
  };

  const handleOrderBy = (id: string) => {
    const newOrderBy = orderBy === id ? null : id;
    setOrderBy(newOrderBy);
    const params = new URLSearchParams(searchParams.toString());
    if (newOrderBy === null) {
      params.delete("order_by");
    } else {
      params.set("order_by", newOrderBy);
    }
    router.push(`?${params.toString()}`);
  };

  const toggleFilter = (id: string) => {
    const newFilters = filters.includes(id)
      ? filters.filter((v) => v !== id)
      : [...filters, id];
    setFilters(newFilters);
    const params = new URLSearchParams(searchParams.toString());
    params.delete("status");
    newFilters.forEach((filter) => {
      params.append("status", filter);
    });
    router.push(`?${params.toString()}`);
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
  }, [searchParams, bank]);

  const totalPages = Math.ceil(caseCount / resultsPerPage);
  const currentPage = searchParams.get("page") ? parseInt(searchParams.get("page")!, 10) : 1;

  return (
    <div className="p-6 flex flex-col flex-1">
      <div className="flex items-center mb-6">
        <h1 className="text-xl md:text-2xl flex-1 truncate font-bold">
          { label }
        </h1>
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
      
      <div className="flex flex-col md:flex-row gap-y-2 gap-x-8 flex-wrap mb-4">
        <div>
          <p className="text-sm font-semibold mb-2">Filtros:</p>
          {FILTER_OPTIONS.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => toggleFilter(id)}
              className={`px-3 py-1 rounded-full text-sm font-medium border transition ml-2 mb-4
                ${filters.includes(id)
                  ? "bg-blue-500 text-white border-blue-500"
                  : "bg-gray-100 text-gray-800 border-gray-300"
                }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div>
          <span className="text-sm font-semibold block mb-2">Ordenar por:</span>
          <div className="flex flex-wrap gap-2 ml-2">
            {ORDER_BY.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => handleOrderBy(id)}
                className={`px-3 py-1 rounded-full text-sm font-medium border transition
                  ${orderBy === id
                    ? "bg-blue-500 text-white border-blue-500"
                    : "bg-gray-100 text-gray-800 border-gray-300"
                  }`
                }
              >
                {label}
              </button>
            ))}
            {showOrderDirection && (
              <button
                onClick={handleDirectionToggle}
                className={`rounded-full border transition flex items-center justify-center w-[38px] h-[30px]
                  ${orderDirection === "asc" || orderDirection === "desc"
                    ? "bg-blue-500 border-blue-500"
                    : "bg-transparent border-gray-300"}
                `}
              >
                {orderDirection === "asc" && (
                  <IconChevronUp size={20} stroke={2.5} className="text-white" />
                )}
                {orderDirection === "desc" && (
                  <IconChevronDown size={20} stroke={2.5} className="text-white" />
                )}
                {orderDirection === null && (
                  <IconSelector size={20} stroke={3.5} className="text-gray-300" />
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {loading ? (
        <Spinner className="flex-1"/>
      ) : (
        <div className="flex flex-col gap-4 flex-1">
          {cases.length === 0 && (
            <div className="text-center flex flex-col justify-center items-center text-gray-700 w-full flex-1">
              Sin casos
            </div>
          )}
          {cases.map((c) => (
            <div
              key={c.id}
              className={classNames(
                "border rounded-lg p-4 flex justify-between items-center bg-white shadow-md",
                (c.link || linkedCases) && "cursor-pointer"
              )}
              onClick={c.link || linkedCases ? () => router.push(`/case/${c.id}`) : undefined}
            >
              <div className="text-sm md:text-base w-full md:w-3/4">
                <div className="flex items-center">
                  <h2 className="text-base md:text-lg font-semibold">
                    {c.title}
                  </h2>
                  {c.simulated && false && (
                    <>
                      <IconInfoCircleFilled
                        data-tooltip-id="simulated-case-tooltip"
                        className="text-blue-400 ml-2 cursor-help hover:text-blue-600"
                        size={20}
                      />
                      <Tooltip id="simulated-case-tooltip" place="top">
                        Este caso es simulado
                      </Tooltip>
                    </>
                  )}
                </div>
                <p className="flex flex-col md:flex-row md:items-center gap-2 gap-y-0 text-gray-800">
                  <span>{translations[c.legal_subject]}</span>
                  <span className="hidden md:inline text-gray-500">•</span>
                  <span>{c.court}</span>
                  {c.created_at && (
                    <>
                      <span className="hidden md:inline text-gray-500">•</span>
                      <span>{formatDate(c.created_at)}</span>
                    </>
                  )}
                </p>
                <p>{c.winner && `Ganador: ${translations[c.winner]}`}</p>
                <div className="justify-center mt-1 pt-2 pb-2">
                  <StatusBar receivedEvents={c.events || []}/>
                </div>
              </div>
              <div className="w-1/4 hidden md:block text-right">
                <p className="text-lg md:text-xl font-bold">
                  {translations[c.status] || c.status}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className={classNames(
        "justify-center mt-6",
        totalPages <= 1 && "hidden",
        totalPages > 1 && "flex",
      )}>
        <button
          className={classNames(
            "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
            currentPage > 1 && "text-blue-700 hover:text-blue-800",
            currentPage <= 1 && "text-gray-600",
          )}
          disabled={currentPage <= 1}
          onClick={() => router.push(`?page=${currentPage - 1}`)}
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
          onClick={() => router.push(`?page=${currentPage + 1}`)}
        >
          <IconCaretRightFilled/>
        </button>
      </div>
    </div>
  );
}

export default CaseList;
