import { BACKEND_URL } from "@/config";

interface TokenResponse {
  message: string;
  group: string | null;
}

async function sendValidateTokenRequest(authToken: string): Promise<boolean | TokenResponse> {
  const url = `${BACKEND_URL}/auth/validate-token/`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: authToken,
      },
    });

    if (!response.ok) {
      console.error(`Failed to validate token: ${response.statusText}`);
      return false;
    }

    const data = await response.json() as TokenResponse;
    if (data.message !== "Token is valid") {
      return false
    }
    return data;
  } catch (error) {
    console.error("Error validating token:", error);
    return false; 
  }
}

export { sendValidateTokenRequest };
