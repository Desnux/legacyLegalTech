import { BACKEND_URL } from "@/config";

async function sendValidateTokenRequest(authToken: string): Promise<boolean> {
  const url = `${BACKEND_URL}/auth/validate-token`;
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

    const data = await response.json();
    return data.message === "Token is valid";
  } catch (error) {
    console.error("Error validating token:", error);
    return false; 
  }
}

export { sendValidateTokenRequest };
