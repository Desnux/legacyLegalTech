import { BACKEND_URL } from "@/config";
import { sendParamsRequest } from "@/services/base";
import { CaseStatsParams, CaseStatsResponse } from "@/types/case";
import { getAuthTokenClient } from "@/utils/auth-token";

// Obtener eventos estadisticos
export async function fetchCaseStats(params: CaseStatsParams): Promise<CaseStatsResponse> {
  return await sendParamsRequest<CaseStatsResponse>("/information/cases/", {...params});
}

// Obtener eventos estadisticos en archivos tabulados
export async function fetchCaseStatsCSV({ bank }: { bank: string }): Promise<Blob> {
  try {
    const token = getAuthTokenClient();
    if (!token) {
      throw new Error("Authentication token is missing.");
    }
    const url = `${BACKEND_URL}/information/cases/${bank}/csv/`;
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch CSV case stats: ${response.statusText}`);
    }
    return await response.blob();
  } catch (error) {
    console.error("Error fetching CSV case stats:", error);
    throw error;
  }
}
