import { BACKEND_URL } from "@/config";

export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type:   string;
    user_id:      string;
    username:     string;
    role:         string;
    expires_at:   string;
}

async function sendLoginRequest(request: LoginRequest): Promise<LoginResponse | null> {
    const url = `${BACKEND_URL}/auth/login/`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      const data = await response.json();
      if(data.error) {
        return null;
      }
      return data as LoginResponse;
    } catch (error) {
      console.error("Error logging in:", error);
      return null; 
    }
  }


export { sendLoginRequest };