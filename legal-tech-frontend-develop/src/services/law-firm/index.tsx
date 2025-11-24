import { BACKEND_URL } from "@/config";
import { LawFirm } from "@/types/law-firm";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";
import { toast } from "react-toastify";


  export async function fetchLawFirmsRequest(): Promise<LawFirm[]> {
    const url = `${BACKEND_URL}/law-firm?skip=0&limit=10`;
    const token = getAuthTokenClient();
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

    const data: LawFirm[] = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching law firms:", error);
    toast.error("Error al obtener las firmas de abogados.");
    throw new Error("No fue posible obtener las firmas de abogados.");
  }
}

