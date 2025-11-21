import { BACKEND_URL } from "@/config";
import { getAuthTokenClient } from "@/utils/auth-token";

/**
 * Sends a request to the backend API with the provided form data.
 * This function handles authentication and error management automatically.
 *
 * @param endpoint - The API endpoint to send the request to.
 * @param method - The HTTP method (e.g., "GET", "POST").
 * @param body - The body of the request, typically a FormData object.
 * @param headers - The headers of the request.
 * 
 * @returns A promise that resolves to the parsed response data of the specified type.
 * 
 * @throws {Error} Throws an error if the request fails, if the token is missing, or if the response is not successful.
 */
async function sendRequest<T>(
  endpoint: string, 
  method: string, 
  body: any,
  headers: Record<string, string> = {}
): Promise<T> {
  const url = `${BACKEND_URL}${endpoint}`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method,
      body,
      headers: {
        "Authorization": `Bearer ${token}`,
        ...headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const contentType = response.headers.get("Content-Type");
    if (contentType && contentType.includes("application/json")) {
      const data = await response.json();
      return data as T;
    } else {
      const blobData = await response.blob();
      return blobData as unknown as T;
    }

  } catch (error) {
    console.error("Error sending request:", error);
    throw new Error("No fue posible completar la solicitud.");
  }
}

/**
 * Sends a GET request to the backend API with query parameters.
 * This function handles authentication and error management automatically.
 *
 * @param endpoint - The API endpoint to send the request to.
 * @param params - An object containing query parameters.
 * @param headers - Optional additional headers.
 * 
 * @returns A promise that resolves to the parsed response data of type T.
 * 
 * @throws {Error} Throws an error if the request fails or if authentication is missing.
 */
async function sendParamsRequest<T>(
  endpoint: string, 
  params: Record<string, string | number | boolean | (string | number | boolean)[]>,
  headers: Record<string, string> = {}
): Promise<T> {
  const url = new URL(`${BACKEND_URL}${endpoint}`);
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  Object.entries(params).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach(val => url.searchParams.append(key, String(val)));
    } else if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value));
    }
  });
  
  try {
    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        ...headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data as T;

  } catch (error) {
    console.error("Error sending request:", error);
    throw new Error("No fue posible completar la solicitud.");
  }
}

export { sendParamsRequest, sendRequest };
