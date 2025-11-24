import { Tribunal } from "@/types/case";
import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";
import { toast } from "react-toastify";


  export async function fetchTribunals(): Promise<Tribunal[]> {
    const url = `${BACKEND_URL}/tribunals?limit=300`;
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
  
      return data as Tribunal[];
    } catch (error) {
      console.error("Error fetching tribunals:", error);
      toast.error("Error al obtener tribunales.");
      throw new Error("No fue posible obtener los tribunales.");
    }
  }
