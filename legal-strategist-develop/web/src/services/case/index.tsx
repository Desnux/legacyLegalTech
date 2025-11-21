import { toast } from "react-toastify";
import { BACKEND_URL } from "@/config";
import { sendParamsRequest } from "@/services/base";
import { Case, CaseEventSuggestion } from "@/types/case";
import { Event } from "@/types/event";
import { CaseStatsParams, CaseStatsResponse } from "@/types/case";
import { EventDocument } from "@/types/event-document";
import { getAuthTokenClient } from "@/utils/auth-token";

// Obtener casos
export async function fetchCases(params: CaseStatsParams): Promise<CaseStatsResponse> {
  return await sendParamsRequest<CaseStatsResponse>("/case/cases/", {...params});
}

// Obtener detalles de un caso
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

// Obtener eventos de un caso
export async function fetchCaseEvents(id: string): Promise<Event[]> {
  const url = `${BACKEND_URL}/case/${id}/events`;
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

// obtener documentos asociados a un evento
export async function fetchEventDocuments(caseId: string, eventId: string): Promise<EventDocument[]> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/documents`;
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

// obtener alernativas de respuesta asociadas a un evento
export async function fetchEventSuggestions(caseId: string, eventId: string): Promise<CaseEventSuggestion[]> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/suggestions`;
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

// enviar alternativa seleccionada al backend
export async function sendSuggestion(caseId: string, eventId: string, suggestionId: string, blob: Blob, password: string, rut: string): Promise<any> {
  const url = `${BACKEND_URL}/case/${caseId}/event/${eventId}/suggestions`;
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

// obtener info avenimiento
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

// Manejo de errores HTTP
function handleError(response: Response): never {
  if (response.status === 401) {
    throw new Error("Error de credenciales. Por favor, inicia sesión.");
  }
  if (response.status === 404) {
    throw new Error("Caso no encontrado. Por favor, verifica el ID.");
  }
  if (response.status === 500) {
    throw new Error("Error interno del servidor. Intenta nuevamente más tarde.");
  }
  throw new Error(`Error inesperado: ${response.statusText}`);
}

function handleErrorStatus(status: number) {
  switch (status) {
    case 400:
      toast.error("Solicitud inválida. Verifique los datos enviados.");
      break;
    case 401:
      toast.error("No autorizado. Inicie sesión nuevamente.");
      break;
    case 402:
      toast.error("Error de pago. Contacte al soporte.");
      break;
    case 404:
      toast.error("Recurso no encontrado.");
      break;
    case 500:
      toast.error("Error interno del servidor. Intente más tarde.");
      break;
    default:
      toast.error(`Error inesperado (${status}).`);
      break;
  }
}