import { toast } from "react-toastify";
import { getAuthTokenClient } from "@/utils/auth-token";
import { BACKEND_URL } from "@/config";
import { Folio, FoliosResponse } from "@/types/pjud";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";

export async function fetchAllFolios(caseNumber: number, year: number): Promise<FoliosResponse> {
    const url = `${BACKEND_URL}/pjud/folios/?case_number=${caseNumber}&year=${year}&limit=100&skip=0`;
    const token = getAuthTokenClient();
  
    if (!token) {
      throw new Error("Requiere autenticación.");
    }
  
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
  
      if (!response.ok) {
        handleErrorStatus(response.status);
        return handleError(response);
      }

      const data = await response.json();
      return data as FoliosResponse;
    } catch (error) {
      console.error("Error fetching all folios:", error);
      toast.error("Error al obtener todos los folios.");
      throw new Error("No fue posible obtener todos los folios.");
    }
  }

  export interface FetchFolioFromPjudRequest {
    case_number: string;
    year: number;
    tribunal_id: string;
    debug: boolean;
    save_to_db: boolean;
  }

  export interface FetchFolioFromPjudRespose {
    message: string;
    status: number;
    data: {
      folio_number: number;
      document: string;
      stage: string;
      procedure: string;
      procedure_description: string;
      procedure_date: string;
      page: number;
      milestone: string | null;
    }[];
    total_items: number;
    offset: number;
    limit: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  }

export async function fetchFolioFromPjud(request: FetchFolioFromPjudRequest, case_id: string): Promise<FetchFolioFromPjudRespose> {
    const url = `${BACKEND_URL}/pjud/scraper/${case_id}/case-notebook/`;
    const token = getAuthTokenClient();
    try {
      const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as FetchFolioFromPjudRespose;
  } catch (error) {
    console.error("Error fetching folio from pjud:", error);
    toast.error("Error al obtener el folio desde pjud.");
    throw new Error("No fue posible obtener el folio desde pjud.");
  }
}

export interface ScrapeCaseNotebookRequest {
  case_number: string;
  year: number;
  tribunal_id: string;
  debug: boolean;
  save_to_db: boolean;
}

export interface ScrapeCaseNotebookResponse {
  message: string;
  status: number;
  data: any;
}

export async function scrapeCaseNotebook(
  request: ScrapeCaseNotebookRequest,
  case_id: string,
  offset: number = 0,
  limit: number = 100
): Promise<ScrapeCaseNotebookResponse> {
  const url = `${BACKEND_URL}/pjud/scraper/${case_id}/case-notebook?offset=${offset}&limit=${limit}`;
  const token = getAuthTokenClient();
  
  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as ScrapeCaseNotebookResponse;
  } catch (error) {
    console.error("Error scraping case notebook:", error);
    toast.error("Error al ejecutar el scraper del cuaderno del caso.");
    throw new Error("No fue posible ejecutar el scraper del cuaderno del caso.");
  }
}
