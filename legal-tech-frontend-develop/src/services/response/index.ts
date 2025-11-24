import { ResponseFile } from "@/types/response-text";
import { sendRequest } from "../base";
import { getAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";
import { BACKEND_URL } from "@/config";
import { ResponseTextStructure } from "@/types/response-text";

export interface SuggestionResponse {
  message:     string;
  code:        number;
  suggestions: Suggestion[];
  event_id:    string;
}

export interface Suggestion {
  id:      string;
  name:    string;
  content: ResponseTextStructure;
  score:   number;
  type:    string;
}

export interface UpdateSuggestionResponse {
  name: string;
  content: ResponseTextStructure;
  score: number;
}

export interface UpdateSuggestionResponseSuccess {
  message: string;
  suggestion_id: string;
  updated_fields: string[];
}

async function extractResponseDispatchResolutionTextInput(
  case_id: string,
  files: ResponseFile[], 
  ): Promise<SuggestionResponse> {
  
  const formData = new FormData();
  
  files.forEach((file) => {
    if (file.file) {
      formData.append('file', file.file, file.file.name);
    }
  });
  
  if (files.length === 0 || !files.some(f => f.file)) {
    throw new Error("Se requiere al menos un archivo PDF");
  }
  
  return await sendRequest<SuggestionResponse>(
    `/simulate/case/${case_id}/dispatch-resolution-event/`, 
    "POST", 
    formData
  );
}
async function extractResponseExceptionTextInput(
  case_id: string,
  files: ResponseFile[], 
  ): Promise<SuggestionResponse> {
  
  const formData = new FormData();
  
  files.forEach((file) => {
    if (file.file) {
      formData.append('file', file.file, file.file.name);
    }
  });
  
  if (files.length === 0 || !files.some(f => f.file)) {
    throw new Error("Se requiere al menos un archivo PDF");
  }
  
  return await sendRequest<SuggestionResponse>(
    `/simulate/case/${case_id}/demand-exception-event/`, 
    "POST", 
    formData
  );
}

async function updateSuggestionResponse(
  case_id: string,
  suggestion_id: string,
  event_id: string,
  suggestion: UpdateSuggestionResponse,
  ): Promise<UpdateSuggestionResponseSuccess> {
  
  const url = `${BACKEND_URL}/case/${case_id}/event/${event_id}/suggestion/${suggestion_id}/`;
  const token = getAuthTokenClient();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const response = await fetch(url, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(suggestion),
  });

  if (!response.ok) {
    handleErrorStatus(response.status);
    return handleError(response);
  }

  const data = await response.json();
  return data as UpdateSuggestionResponseSuccess;
}

export { extractResponseDispatchResolutionTextInput, extractResponseExceptionTextInput, updateSuggestionResponse };