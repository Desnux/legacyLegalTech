import { RECEPTHOR_CAPTCHA_TOKEN, RECEPTHOR_EMAIL, RECEPTHOR_PASSWORD, RECEPTHOR_SKIP_CAPTCHA_TOKEN, RECEPTHOR_URL } from "@/config";
import { toast } from "react-toastify";
import { AssignCaseResponse, CreateTaskRequest, ErrorResponse, RecepthorLoginErrorResponse, RecepthorLoginRequest, RecepthorLoginResponse, Receptor, ReceptorsResponse, SearchAndAssignCaseRequest, Task, Tasks } from "@/types/recepthor";
import { getRecepthorAuthTokenClient } from "@/utils/auth-token";
import { handleError, handleErrorStatus } from "@/utils/handle-http-status";

export async function loginToRecepthor(): Promise<RecepthorLoginResponse> {
    const url = `${RECEPTHOR_URL}/auth/login`;
    const body: RecepthorLoginRequest = {
        captchaToken: RECEPTHOR_CAPTCHA_TOKEN,
        email: RECEPTHOR_EMAIL,
        password: RECEPTHOR_PASSWORD,
        skipCaptchaToken: RECEPTHOR_SKIP_CAPTCHA_TOKEN,
    };
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "captchaToken": RECEPTHOR_CAPTCHA_TOKEN,
            "email": RECEPTHOR_EMAIL,
            "password": RECEPTHOR_PASSWORD,
            "skipCaptchaToken": RECEPTHOR_SKIP_CAPTCHA_TOKEN,
        },
        body: JSON.stringify(body),
    });
    const data = await response.json();

    if (data.error) {

    }

    return data as RecepthorLoginResponse;
}

async function fetchReceptorsByTribunalId(tribunalId: string): Promise<ReceptorsResponse> {
    const page = 1;
    const pageSize = 500;
    const url = `${RECEPTHOR_URL}/receptors?currentPage=${page}&pageSize=${pageSize}&tribunalId=${tribunalId}`;
    const token = getRecepthorAuthTokenClient();

    if (!token) {
      return {
        pagination: {
          currentPage: 0,
          pageSize: 0,
          totalPages: 0,
          totalRecords: 0,
        }, results: []
      } as ReceptorsResponse;
    }
  
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
  
      const data = await response.json();

      if (data.error) {
        manageErrorResponse(data, response);
      }
  
      return data as ReceptorsResponse;
    } catch (error) {
      console.error("Error fetching case details:", error);
      toast.error("Error al obtener detalles del caso en Recepthor.");
      throw new Error("No fue posible obtener los detalles del caso.");
    }
}

export async function fetchReceptorsById(id: string): Promise<Receptor> {
  const url = `${RECEPTHOR_URL}/receptors/${id}`;
  const token = getRecepthorAuthTokenClient();

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

    const data = await response.json();

    if (data.error) {
      manageErrorResponse(data, response);
    }

    return data as Receptor;
  } catch (error) {
    console.error("Error fetching receptors by id:", error);
    toast.error("Error al obtener receptores por id en Recepthor.");
    throw new Error("No fue posible obtener receptores por id.");
  }
}

export async function createTask(task: CreateTaskRequest): Promise<Task> {
  const url = `${RECEPTHOR_URL}/tasks`;
  const token = getRecepthorAuthTokenClient();

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
      body: JSON.stringify(task),
    });

    const data = await response.json();

    if (data.error) {
      manageErrorResponse(data, response);
    }

    return data as Task;
  } catch (error) {
    console.error("Error creating task:", error);
    toast.error("Error al crear tarea en Recepthor.");
    throw new Error("No fue posible crear tarea.");
  }
}

export async function fetchTaskById(id: string): Promise<Task> {
  const url = `${RECEPTHOR_URL}/tasks/${id}`;
  const token = getRecepthorAuthTokenClient();

  if (!token) {
    throw new Error("Recepthor requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.error) {
      manageErrorResponse(data, response);
    }

    return data as Task;
  } catch (error) {
    console.error("Error fetching task by id:", error);
    toast.error("Error al obtener tarea por id en Recepthor.");
    throw new Error("No fue posible obtener tarea por id.");
  }
}

export async function fetchTaskByCaseId(caseId: string): Promise<Tasks> {
  const page = 1;
  const pageSize = 50;
  const url = `${RECEPTHOR_URL}/tasks?currentPage=${page}&pageSize=${pageSize}`;
  const token = getRecepthorAuthTokenClient();

  if (!token) {
    throw new Error("Recepthor requiere autenticación.");
  }

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.error) {
      manageErrorResponse(data, response);
    }
    const filteredData: Tasks | null = data.results.find((task: Tasks) => task.firmCase.case.id === caseId) || null;

    return filteredData as Tasks;
  } catch (error) {
    console.error("Error fetching task by id:", error);
    toast.error("Error al obtener tarea por id en Recepthor.");
    throw new Error("No fue posible obtener tarea por id.");
  }
}

export async function searchAndAssignCase(request: SearchAndAssignCaseRequest): Promise<AssignCaseResponse> {
  const url = `${RECEPTHOR_URL}/cases`;
  const token = getRecepthorAuthTokenClient();

  if (!token) {
    throw new Error("Recepthor requiere autenticación.");
  }

  try {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  const data = await response.json();

  if (data.error) {
    manageErrorResponse(data, response);
  }
  return data as AssignCaseResponse;
  } catch (error) {
    console.error("Error searching and assigning case:", error);
    toast.error("Error al buscar y asignar caso en Recepthor.");
    throw new Error("No fue posible buscar y asignar caso.");
  }
}

export async function manageErrorResponse(data: ErrorResponse, response: Response) {
  const error = data as ErrorResponse;
        
  if (error.error && error.error.statusCode) {
    handleErrorStatus(error.error.statusCode);
  } else {
    console.log('Error structure is different than expected:', error);
    handleErrorStatus(response.status);
  }
  
  return handleError(response);
}