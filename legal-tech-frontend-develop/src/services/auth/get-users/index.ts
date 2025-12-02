import { BACKEND_URL } from "@/config";
import { LawFirm } from "@/types/law-firm";
import { getAuthTokenClient } from "@/utils/auth-token";

export interface User {
  id: string;
  name: string;
  role: string;
  active: boolean;
  created_at: string;
  law_firm: LawFirm;
}


async function sendGetUsersRequest(): Promise<User[]> {
  const url = `${BACKEND_URL}/auth/users/`;
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
      if (response.status === 401) {
        throw new Error("Error de autenticación.");
      }
      if (response.status === 403) {
        throw new Error("No tienes permisos para ver usuarios.");
      }
      throw new Error("Error al obtener usuarios.");
    }

    const data = await response.json();
    return data as User[];
  } catch (error) {
    console.error("Error fetching users:", error);
    throw error;
  }
}

export { sendGetUsersRequest }; 