import { sendRequest, sendParamsRequest } from "@/services/base";
import { DemandTextAnalysis, DemandTextInputInformation, DemandTextStructure } from "@/types/demand-text";
import { FileWithContext } from "@/types/file";
import { Output } from "@/types/output";

interface DemandTextSenderRequest {
  demandTextPDF: Blob,
  contract: FileList | null,
  mandate: FileList,
  password: string,
  rut: string,
  debug: boolean,
  information: DemandTextInputInformation,
  structure: DemandTextStructure,
  extraFiles: File[],
  extraFilesLabels: string[],
  dollarCertificate?: File,
}

interface DemandTextSenderResponse {
  message: string,
  status: number,
  caseId?: string | null,
  case_id?: string | null,
}

export interface DefendantSocietyInformation {
  societyName: string;
  rut: string;
  participation: string;
}

export interface DefendantVehicleInformation {
  patente: string;
  brand: string;
  model: string;
  year: number;
  fiscalValue: number;
}

export interface DefendantPropertyInformation {
  address: string;
  rol: string;
  comuna: string;
  comunaCode: string;
  foja: string;
  number: string;
  year: string;
}

/**
 * Sends a request to analyze a demand text with the provided structure.
 */
async function analyzeDemandTextFromStructure(
  structure: DemandTextStructure,
): Promise<Output<DemandTextAnalysis>> {
  const formData = new FormData();
  formData.append("input", JSON.stringify(structure));

  return await sendRequest<Output<DemandTextAnalysis>>("/analyze/demand-text-from-structure/", "POST", formData);
}

/**
 * Sends a request to extract a demand text input from the provided text and files.
 */
async function extractDemandTextInput(
  text: string, 
  files: FileWithContext[], 
): Promise<Output<DemandTextInputInformation>> {
  const formData = new FormData();
  formData.append("text", text);

  files.forEach((file) => {
    formData.append("file_types", file.fileType);
    formData.append("files", file.file);
  });

  return await sendRequest<Output<DemandTextInputInformation>>("/extract/demand-text-input/", "POST", formData);
}

/**
 * Sends a request to generate a demand text with the provided structure.
 */
async function generateDemandTextFromStructure(
  structure: DemandTextInputInformation,
): Promise<Output<DemandTextStructure>> {
  return await sendRequest<Output<DemandTextStructure>>(
    "/generate/demand-text-from-structure/",
    "POST",
    JSON.stringify(structure),
    { "Content-Type": "application/json" },
  );
}

/**
 * Sends a request to send a demand text to PJUD with the provided structure and information.
 */
async function sendDemandText({ 
  demandTextPDF,
  contract,
  mandate,
  password,
  rut,
  structure,
  information,
  extraFiles,
  extraFilesLabels,
  dollarCertificate,
  debug
}: DemandTextSenderRequest) {
  const input = {
    password: password,
    rut: rut,
    debug: debug,
    information,
    structure,
  };

  const formData = new FormData();
  const file = new File([demandTextPDF], "demand_text.pdf", { type: "application/pdf" });

  formData.append("input", JSON.stringify(input));
  formData.append("demand_text", file);

  if (contract) {
    for (let i = 0; i < contract.length; i++) {
      formData.append("contract", contract[i]);
    }
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
    return await sendRequest<DemandTextSenderResponse>("/send/demand-text/", "POST", formData);
  } catch (error: any) {
    // Si el error es 504, lo propagamos con información del status
    if (error?.status === 504 || error?.message?.includes("504")) {
      const gatewayTimeoutError: any = new Error("Gateway Timeout");
      gatewayTimeoutError.status = 504;
      throw gatewayTimeoutError;
    }
    throw error;
  }
}

async function getDefendantSocietyInformation(rut: string): Promise<DefendantSocietyInformation[]> {
  return await sendParamsRequest<DefendantSocietyInformation[]>(`/homespotter/societies/by-owner/${rut}`, {});
}

async function getDefendantVehicleInformation(rut: string): Promise<DefendantVehicleInformation[]> {
  return await sendParamsRequest<DefendantVehicleInformation[]>(`/homespotter/vehicles/by-owner/${rut}`, {});
}

async function getDefendantPropertyInformation(rut: string): Promise<DefendantPropertyInformation[]> {
  return await sendParamsRequest<DefendantPropertyInformation[]>(`/homespotter/properties/by-owner/${rut}`, {});
}

export { analyzeDemandTextFromStructure, extractDemandTextInput, generateDemandTextFromStructure, sendDemandText, getDefendantSocietyInformation, getDefendantVehicleInformation, getDefendantPropertyInformation };
export type { DemandTextSenderRequest };
