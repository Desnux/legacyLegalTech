"use client";

import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import classNames from "classnames";
import { useRouter } from "next/navigation";
import { 
  IconCaretLeftFilled,
  IconCaretRightFilled,
  IconChevronDown,
  IconChevronUp,
  IconSelector,
  IconFilter,
  IconSortAscending,
  IconTrash,
  IconUser,
  IconClock,
  IconCheck,
  IconFileText,
  IconCalendar,
} from "@tabler/icons-react";
import { Spinner } from "@/components/state";
import Dropdown from "@/components/input/dropdown";
import { fetchActions, ActionResponse, Action } from "@/services/action";
import { formatDate } from "@/utils/date";

const ORDER_BY = [
  { id: "action_to_follow", label: "Acción a seguir" },
  { id: "responsible", label: "Responsable" },
  { id: "deadline", label: "Fecha límite" },
  { id: "completed", label: "Estado" },
];

const resultsPerPage = 30;

const ActionsList = () => {
  const router = useRouter();
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [orderBy, setOrderBy] = useState<string | null>(null);
  const [orderDirection, setOrderDirection] = useState<"asc" | "desc" | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);

  const handleDirectionToggle = () => {
    const newDirection =
      orderDirection === null ? "asc" : orderDirection === "asc" ? "desc" : null;
    setOrderDirection(newDirection);
  };

  const handleOrderBy = (id: string) => {
    const newOrderBy = orderBy === id ? null : id;
    setOrderBy(newOrderBy);
  };

  const fetchActionsData = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * resultsPerPage;
      const data = await fetchActions(skip, resultsPerPage);
      setActions(data.actions || []);
      setTotalCount(data.total_count || 0);
    } catch (error) {
      console.error("Error fetching actions:", error);
      toast.error("No fue posible obtener las acciones");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActionsData();
  }, [currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const actionsFilteredBySearch = (actions || []).filter(action => {
    const searchMatch = !searchTerm || 
      action.action_to_follow.toLowerCase().includes(searchTerm.toLowerCase()) ||
      action.responsible.toLowerCase().includes(searchTerm.toLowerCase()) ||
      action.comment.toLowerCase().includes(searchTerm.toLowerCase()) ||
      action.case_id.toLowerCase().includes(searchTerm.toLowerCase());
    return searchMatch;
  });

  const sortedActions = [...actionsFilteredBySearch].sort((a, b) => {
    if (!orderBy) return 0;
    
    let aValue: any;
    let bValue: any;
    
    switch (orderBy) {
      case "action_to_follow":
        aValue = a.action_to_follow;
        bValue = b.action_to_follow;
        break;
      case "responsible":
        aValue = a.responsible;
        bValue = b.responsible;
        break;
      case "deadline":
        aValue = new Date(a.deadline);
        bValue = new Date(b.deadline);
        break;
      case "completed":
        aValue = a.completed ? 1 : 0;
        bValue = b.completed ? 1 : 0;
        break;
      default:
        return 0;
    }
    
    if (aValue === null || aValue === undefined) return 1;
    if (bValue === null || bValue === undefined) return -1;
    
    let comparison = 0;
    if (typeof aValue === "string" && typeof bValue === "string") {
      comparison = aValue.localeCompare(bValue);
    } else if (aValue instanceof Date && bValue instanceof Date) {
      comparison = aValue.getTime() - bValue.getTime();
    } else {
      comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    }
    
    return orderDirection === "desc" ? -comparison : comparison;
  });

  const paginatedActions = sortedActions;
  const totalPages = Math.ceil(totalCount / resultsPerPage);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="my-6 flex flex-col flex-1 rounded-2xl shadow-lg border border-medium-gray bg-pure-white">
      <div className="">
        <div className="m-8">
          <h1 className="text-h2 font-serif text-petroleum-blue mb-1">
            Gestionar de Juicios
          </h1>
          <p className="text-body-sm text-charcoal-gray max-w-2xl">
            Gestiona y monitorea todas las acciones pendientes y completadas de los casos.
          </p>
        </div>
      </div>

      {/* Filters and Sorting */}
      <div className="flex items-center justify-between p-2 border-t border-gray-300 pt-4">
        <div className="flex items-center gap-4">
          {/* Buscador */}
          <div className="flex items-center gap-2">
            <IconFilter size={16} className="text-gray-600" />
            <span className="text-sm text-gray-600">Buscar:</span>
            <input
              type="text"
              placeholder="Buscar en acciones..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white border border-gray-300 text-gray-700 text-sm rounded-lg px-3 py-1 w-64 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                className="p-1 hover:bg-gray-200 rounded transition-colors"
                title="Limpiar búsqueda"
              >
                <IconTrash size={16} className="text-red-600" />
              </button>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <IconSortAscending size={16} className="text-gray-600" />
            <span className="text-sm text-gray-600">Ordenar:</span>
            <Dropdown
              options={ORDER_BY.map(({ id, label }) => ({ value: id, label }))}
              value={orderBy || "created_at"}
              onChange={handleOrderBy}
              placeholder="Seleccionar orden"
              className="w-48"
            />
            <button
              onClick={handleDirectionToggle}
              className={classNames(
                "p-2 rounded-lg border transition-all duration-200 flex items-center justify-center",
                orderDirection === "asc" || orderDirection === "desc"
                  ? "bg-blue-600 border-blue-600 text-white hover:bg-blue-700"
                  : "bg-gray-100 border-gray-300 text-gray-600 hover:bg-gray-200"
              )}
              title={orderDirection === "asc" ? "Ascendente" : orderDirection === "desc" ? "Descendente" : "Sin orden"}
            >
              {orderDirection === "asc" && (
                <IconChevronUp size={16} />
              )}
              {orderDirection === "desc" && (
                <IconChevronDown size={16} />
              )}
              {orderDirection === null && (
                <IconSelector size={16} />
              )}
            </button>
          </div>
          
        </div>
      </div>

      {loading ? (
        <Spinner className="flex-1"/>
      ) : (
        <div className="flex flex-col flex-1">
          {actions && actions.length === 0 && (
            <div className="text-center flex flex-col justify-center items-center text-gray-700 w-full flex-1">
              Sin acciones
            </div>
          )}
          
          {actions && actions.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse bg-pure-white overflow-hidden">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Caso
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Acción a Seguir
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Responsable
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Fecha Límite
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Estado
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b">
                      Comentario
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedActions.map((action, index) => (
                    <tr 
                      key={action.id}
                      className={classNames(
                        "border-b transition-all duration-200 ease-in-out hover:bg-gray-50 animate-slideIn"
                      )}
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <td className="px-4 py-3 text-sm text-gray-900">
                        <button
                          onClick={() => router.push(`/case/${action.case_id}`)}
                          className="flex items-center gap-2 text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          <IconFileText size={16} />
                          {`Caso ${action.case_id}`}
                        </button>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={action.action_to_follow}>
                          {action.action_to_follow}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        <div className="flex items-center gap-2">
                          <IconUser size={16} className="text-gray-500" />
                          {action.responsible}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        <div className="flex items-center gap-2">
                          <IconCalendar size={16} className="text-gray-500" />
                          {formatDate(action.deadline)}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900">
                        <span className={classNames(
                          "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium",
                          {
                            "bg-green-100 text-green-800": action.completed,
                            "bg-yellow-100 text-yellow-800": !action.completed
                          }
                        )}>
                          {action.completed ? (
                            <>
                              <IconCheck size={12} />
                              Completada
                            </>
                          ) : (
                            <>
                              <IconClock size={12} />
                              Pendiente
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-900 max-w-xs">
                        <div className="truncate" title={action.comment}>
                          {action.comment || "Sin comentario"}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      <div className={classNames(
        "justify-center my-2",
        sortedActions && sortedActions.length === 0 && "hidden",
        sortedActions && sortedActions.length > 0 && "flex",
      )}>
        <button
          className={classNames(
            "px-4 py-2 mx-2 bg-transparent disabled:cursor-not-allowed",
            currentPage > 1 && "text-blue-700 hover:text-blue-800",
            currentPage <= 1 && "text-gray-600",
          )}
          disabled={currentPage <= 1}
          onClick={() => handlePageChange(currentPage - 1)}
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
          onClick={() => handlePageChange(currentPage + 1)}
        >
          <IconCaretRightFilled/>
        </button>
      </div>
    </div>
  );
};

export default ActionsList;
