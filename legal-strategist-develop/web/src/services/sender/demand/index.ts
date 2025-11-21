import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";

export interface DemandResponse {
  status: number;
  message: string;
  data?: Demand[];
}

export interface Demand {
  title: string;
  creation_date: string;
  index: number;
  author: string;
  court: string;
  legal_subject: string;
}

// Obtener lista de demandas
export async function fetchDemandList(rut: string, password: string): Promise<DemandResponse> {
  const url = `${BACKEND_URL}/extract/demand_list/`;
  // const url = `http://localhost:8090/v1/extract/demand_list/`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const body = { rut: rut, password: password };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { status: 401, message: "Error de credenciales." };
      }

      if (response.status === 500) {
        return { status: 500, message: "No fue posible obtener la lista de demandas." };
      }
    }

    const data: DemandResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching demand list:", error);
    return { status: 500, message: "No fue posible obtener la lista de demandas." };
  }
}

// Enviar demanda
export async function sendDemand(rut: string, password: string, index: number): Promise<DemandResponse> {
  const url = `${BACKEND_URL}/send/demand/`;
  // const url = `http://localhost:8090/v1/send/demand/`;
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
      body: JSON.stringify({ rut, password, index }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { status: 401, message: "Error de credenciales." };
      }

      if (response.status === 500) {
        return { status: 500, message: "PJUD no funciona en este momento." };
      }
    }

    const data: DemandResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error sending demand:", error);
    return { status: 500, message: "No fue posible enviar la demanda." };
  }
}

// Eliminar demanda
export async function deleteDemand(rut: string, password: string, index: number): Promise<DemandResponse> {
  const url = `${BACKEND_URL}/send/demand/`;
  // const url = `http://localhost:8090/v1/send/demand/`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ rut, password, index }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { status: 401, message: "Error de credenciales." };
      }

      if (response.status === 500) {
        return { status: 500, message: "PJUD no funciona en este momento." };
      }
    }

    const data: DemandResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Error deleting demand:", error);
    return { status: 500, message: "No fue posible eliminar la demanda." };
  }
}
