import { BACKEND_URL } from "@/config";
import { DemandTextCorrectionForm, DemandTextStructure } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { getAuthToken } from "@/utils/auth-token";

interface DemandTextGeneratorResponse {
  raw_text: string;
  structured_output: DemandTextStructure;
  correction_form: DemandTextCorrectionForm;
}

async function sendDemandTextGeneratorRequest(content: string, files: FileWithContext[], seed?: number, dollarCertificate?: File): Promise<DemandTextGeneratorResponse> {
  const url = `${BACKEND_URL}/network/chat`;
  const token = getAuthToken();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const formData = new FormData();
  formData.append("content", content);
  if (seed) {
    formData.append("seed", seed.toString());
  }

  files.forEach((file) => {
    formData.append("files", file.file);
    formData.append("file_types", file.fileType);
  });

  if (dollarCertificate) {
    formData.append("dollar_certificate", dollarCertificate);
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
    console.error("Error sending chat request:", error);
    throw new Error("No fue posible generar el texto de demanda.");
  }
}

export { sendDemandTextGeneratorRequest };
export type { DemandTextGeneratorResponse };
