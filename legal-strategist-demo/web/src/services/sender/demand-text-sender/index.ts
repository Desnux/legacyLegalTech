import { BACKEND_URL } from "@/config";
import { Attorney, Defendant, Plaintiff } from "@/types/litigant";
import { getAuthToken } from "@/utils/auth-token";

export type DemandTextSenderRequest = {
  demandTextPDF: Blob,
  contract: FileList,
  mandate: FileList,
  password: string,
  rut: string,
  legalSubject: string,
  extraFiles: File[],
  extraFilesLabels: string[],
  sponsoringAttorneys: Attorney[],
  plaintiffs: Plaintiff[],
  defendants: Defendant[],
  dollarCertificate?: File,
}

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
  const token = getAuthToken();

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
  const token = getAuthToken();

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
  const token = getAuthToken();

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

async function sendDemandTextSenderRequest({ 
  demandTextPDF,
  contract,
  mandate,
  password,
  rut,
  legalSubject,
  extraFiles,
  extraFilesLabels,
  sponsoringAttorneys,
  plaintiffs,
  defendants,
  dollarCertificate
}: DemandTextSenderRequest) {
  const url = `${BACKEND_URL}/send/demand_text`;
  const token = getAuthToken();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const input = {
    password: password,
    rut: rut,
    legal_subject: legalSubject,
    sponsoring_attorneys: sponsoringAttorneys,
    plaintiffs: plaintiffs,
    defendants: defendants,
  };

  const formData = new FormData();
  const file = new File([demandTextPDF], "demand_text.pdf", { type: "application/pdf" });

  formData.append("input", JSON.stringify(input));
  formData.append("demand_text", file);

  for (let i = 0; i < contract.length; i++) {
    formData.append("contract", contract[i]);
  }

  for (let i = 0; i < mandate.length; i++) {
    formData.append("mandate", mandate[i]);
  }

  if (extraFiles.length > 0 && extraFilesLabels.length === extraFiles.length) {
    extraFiles.forEach((file, index) => {
      formData.append("extra_files", file);
      formData.append("extra_files_labels", extraFilesLabels[index]);
    });
  }

  if (dollarCertificate) {
    formData.append("extra_files", dollarCertificate);
    formData.append("extra_files_labels", "Certificado dólar");
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Error sending demand text:", error);
    throw new Error("No fue posible enviar el texto de demanda.");
  }
}

export { sendDemandTextSenderRequest };
