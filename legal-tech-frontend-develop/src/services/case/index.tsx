import { toast } from "react-toastify";
import { BACKEND_URL } from "@/config";
import { sendParamsRequest } from "@/services/base";
import { Case, CaseDetailInfo, CaseEventSuggestion, CaseListResponse, CreateCaseDetail } from "@/types/case";
import { Event } from "@/types/event";
import { CaseStatsParams, CaseStatsResponse } from "@/types/case";
import { EventDocument } from "@/types/event-document";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";

export async function fetchCases(params: CaseStatsParams): Promise<CaseListResponse> {
  return await sendParamsRequest<CaseListResponse>("/case/cases/", {...params});
}

export async function fetchCaseDetails(id: string): Promise<Case> {
  const url = `${BACKEND_URL}/case/${id}/`;
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

    return data as Case;
  } catch (error) {
    console.error("Error fetching case details:", error);
    toast.error("Error al obtener detalles del caso.");
    throw new Error("No fue posible obtener los detalles del caso.");
  }
}

export async function fetchCaseEvents(id: string): Promise<Event[]> {
  const url = `${BACKEND_URL}/case/${id}/events/`;
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
    return data as Event[];
  } catch (error) {
    console.error("Error fetching case events:", error);
    toast.error("Error al obtener los eventos del caso.");
    throw new Error("No fue posible obtener los eventos del caso.");
  }
}

export async function fetchEventDocuments(caseId: string, eventId: string): Promise<EventDocument[]> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/documents/`;
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
    return data as EventDocument[];;
  } catch (error) {
    console.error("Error fetching event documents:", error);
    toast.error("Error al obtener los documentos del evento.");
    throw new Error("No fue posible obtener los documentos del evento.");
  }
}

export async function fetchEventSuggestions(caseId: string, eventId: string): Promise<CaseEventSuggestion[]> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/suggestions/`;
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

    return data as CaseEventSuggestion[];
  } catch (error) {
    console.error("Error fetching event suggestions:", error);
    toast.error("Error al obtener las alternativas del evento.");
    throw new Error("No fue posible obtener las alternativas del evento.");
  }
}

export async function sendSuggestion(caseId: string, eventId: string, suggestionId: string, blob: Blob, password: string, rut: string): Promise<any> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/suggestions/`;
  const token = getAuthTokenClient();
  const file = new File([blob], "document.pdf", { type: "application/pdf" });

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const jsonData = JSON.stringify({
      id: suggestionId,
      password: password,
      rut: rut
    });
    formData.append('data', jsonData);

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();

    return data;
  } catch (error) {
    console.error("Error sending selected suggestion:", error);
    toast.error("Error al enviar la alternativa seleccionada.");
    throw new Error("No fue posible enviar la alternativa seleccionada.");
  }
}

export async function fetchAdvent(caseId: string) {
  const url = `${BACKEND_URL}/case/${caseId}/simulate/legal-compromise`;
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
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();

    return data;
  } catch (error) {
    console.error("Error fetching advent:", error);
    toast.error("Error al obtener avenimiento del evento.");
    throw new Error("No fue posible obtener el avenimiento.");
  }
}

// TODO: Remove this function
export async function simulateFutureEvents(caseId: string) {
  const url = `${BACKEND_URL}/simulate/case/${caseId}/future-events/`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Error simulating future events:", error);
    throw new Error("No fue posible obtener los eventos siguientes.");
  }
}

export async function createDetails(caseId: string, detail_request: CreateCaseDetail): Promise<CaseDetailInfo> {
  const url = `${BACKEND_URL}/case/${caseId}/details/`;
  const token = getAuthTokenClient();
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(detail_request),
  });
  if (!response.ok) {
    handleErrorStatus(response.status);
    return handleError(response);
  }
  const data = await response.json() as CaseDetailInfo;
  return data;
}

export async function updateCase(id: string, updateData: Partial<Case>): Promise<Case> {
  const url = `${BACKEND_URL}/case/${id}/`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as Case;
  } catch (error) {
    console.error("Error updating case:", error);
    toast.error("Error al actualizar el caso.");
    throw new Error("No fue posible actualizar el caso.");
  }
}

export async function simulateDemandStartEvent(caseId: string) {
  const url = `${BACKEND_URL}/simulate/case/${caseId}/dispatch-start-event/`;
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
      body: JSON.stringify({
        "content": "Notas adicionales sobre el despacho"
      }),
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as any;
  } catch (error) {
    console.error("Error updating case:", error);
    toast.error("Error al actualizar el caso.");
    throw new Error("No fue posible actualizar el caso.");
  }
}