import { Court } from "@/types/case";
import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";
import { toast } from "react-toastify";

  export async function fetchCourts(): Promise<Court[]> {
    const url = `${BACKEND_URL}/courts?limit=100`;
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
  
      return data as Court[];
    } catch (error) {
      console.error("Error fetching courts:", error);
      toast.error("Error al obtener cortes.");
      throw new Error("No fue posible obtener las cortes.");
    }
  }
