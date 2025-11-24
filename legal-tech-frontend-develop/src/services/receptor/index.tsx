import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";


export interface ReceptorsResponse {
    id: string;
    recepthor_external_id: string;
    name: string;
    primary_email: string;
    secondary_email: string;
    primary_phone: string;
    secondary_phone: string;
    address: string | null;
    details: ReceptorDetails[];
}

export interface ReceptorDetails {
    id: string;
    tribunal: TribunalDetails;
}

export interface TribunalDetails {
    id: string;
    recepthor_id: string;
    name: string;
    code: number;
}

export async function fetchReceptorsByTribunalId(tribunalId: string): Promise<ReceptorsResponse[]> {
    console.log("tribunalId", tribunalId);
    const url = `${BACKEND_URL}/receptor/tribunal/${tribunalId}/`;
    const token = getAuthTokenClient();
    try {
      const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      }
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as ReceptorsResponse[];
  } catch (error) {
    console.error("Error fetching receptors by tribunal id:", error);
    throw new Error("No fue posible obtener receptores por tribunal id.");
  }
}

export async function fetchReceptors(skip?: number, limit?: number): Promise<ReceptorsResponse[]> {
    if (!skip) {
        skip = 0;
    }
    if (!limit) {
        limit = 700;
    }
    const url = `${BACKEND_URL}/receptor/?skip=${skip}&limit=${limit}`;
    const token = getAuthTokenClient();
    try {
      const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      }
    });

    if (!response.ok) {
      handleErrorStatus(response.status);
      return handleError(response);
    }

    const data = await response.json();
    return data as ReceptorsResponse[];
  } catch (error) {
    console.error("Error fetching receptors:", error);
    throw new Error("No fue posible obtener receptores.");
  }
}
