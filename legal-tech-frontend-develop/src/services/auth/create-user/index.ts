import { BACKEND_URL } from "@/config";

export interface CreateUserRequest {
    name: string;
    password: string;
    role: string;
    law_firm_id?: string | null;
}

export interface CreateUserResponse {
    id: string;
    name: string;
    role: string;
    active: boolean;
    created_at: string;
}

export interface CreateUserError {
    detail: {
        type: string;
        loc: string[];
        msg: string;
        input: string;
        ctx: {
            error: {};
        };
    }[];
}

async function sendCreateUserRequest(request: CreateUserRequest): Promise<CreateUserResponse | null> {
    const url = `${BACKEND_URL}/auth/register/`;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });
      const data = await response.json();
      if(data.detail) {
        return null;
      }
      return data as CreateUserResponse;
    } catch (error: any) {
      console.error("Error creating user:", error);
      throw new Error(error.message);
    }
  }


export { sendCreateUserRequest };