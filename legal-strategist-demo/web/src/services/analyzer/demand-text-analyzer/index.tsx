import { BACKEND_URL } from "@/config";
import { DemandTextAnalysis, DemandTextStructure } from "@/types/demand-text";
import { getAuthToken } from "@/utils/auth-token";

async function sendDemandTextAnalyzerRequest(input: DemandTextStructure, control?: DemandTextStructure): Promise<DemandTextAnalysis> {
  const url = `${BACKEND_URL}/analyze/judicial_collection_demand_text_by_structured`;
  const token = getAuthToken();

  if (!token) {
    throw new Error("Requiere autenticación.");
  }

  const formData = new FormData();
  formData.append("input", JSON.stringify(input));
  if (control) {
    formData.append("control", JSON.stringify(control));
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
    console.error("Error sending analysis request:", error);
    throw new Error("No fue posible analizar el texto de demanda.");
  }
}

export { sendDemandTextAnalyzerRequest };
