import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";

export interface CreateActionRequest {
    action_to_follow: string;
    responsible: string;
    deadline: string;
    completed?: boolean;
    comment: string;
}

export interface ActionResponse {
    total_count: number;
    actions:    Action[];
}

export interface Action {
    id: string;
    case_id: string;
    action_to_follow: string;
    responsible: string;
    deadline: string;
    completed: boolean;
    comment: string;
}

async function fetchActionsByCaseId(caseId: string, skip: number, limit: number): Promise<ActionResponse> {
    const url = `${BACKEND_URL}/case/${caseId}/actions/?skip=${skip}&limit=${limit}`;
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
      return data as ActionResponse;
    } catch (error) {
      console.error("Error fetching actions by case id:", error);
      throw new Error("No fue posible obtener las acciones del caso.");
    }
}

async function fetchActions(skip: number, limit: number): Promise<ActionResponse> {
  const url = `${BACKEND_URL}/case/actions/?skip=${skip}&limit=${limit}`;
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
    return data as ActionResponse;
  } catch (error) {
    console.error("Error fetching actions:", error);
    throw new Error("No fue posible obtener las acciones.");
  }
}

async function sendCreateActionRequest(caseId: string, request: CreateActionRequest): Promise<ActionResponse | null> {
    const url = `${BACKEND_URL}/case/${caseId}/actions/`;
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
      if(data.error) {
        throw new Error("No fue posible crear la acción.");
      }
      return data as ActionResponse;
    } catch (error) {
      console.error("Error creating action:", error);
      throw new Error("No fue posible crear la acción.");
    }
  }


export { sendCreateActionRequest, fetchActionsByCaseId, fetchActions };
