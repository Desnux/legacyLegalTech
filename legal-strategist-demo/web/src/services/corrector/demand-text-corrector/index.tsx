import { BACKEND_URL } from "@/config";
import { DemandTextGeneratorResponse } from "@/services/generator";
import { DemandTextCorrectionForm, DemandTextStructure } from "@/types/demand-text";
import { getAuthToken } from "@/utils/auth-token";

async function sendDemandTextCorrectorRequest(structure: DemandTextStructure, correctionForm: DemandTextCorrectionForm): Promise<DemandTextGeneratorResponse> {
  const url = `${BACKEND_URL}/correct/demand_text_by_structured`;
  const token = getAuthToken();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const body = {
    structured_output: structure,
    correction_form: correctionForm,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify(body),
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Error sending correction request:", error);
    throw new Error("No fue posible ajustar el texto de demanda.");
  }
}

export { sendDemandTextCorrectorRequest };
