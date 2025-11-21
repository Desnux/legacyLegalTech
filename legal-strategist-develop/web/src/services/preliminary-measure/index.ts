import { sendRequest } from "@/services/base";
import { PreliminaryMeasureInputInformation } from "@/types/preliminary-measure";
import { Output } from "@/types/output";

/**
 * Sends a request to extract a preliminary measure input from the provided fields.
 */
async function extractPreliminaryMeasureInput(
  local_police_number: number | null,
  communication_date: string,
  file: FileList,
  coopeuch_registry_image: FileList | null,
  transaction_to_self_image: FileList | null,
  payment_to_account_image: FileList | null,
  user_report_image: FileList | null,
  safesigner_report_image: FileList | null,
  mastercard_connect_report_image: FileList | null,
  celmedia_report_image: FileList | null,
): Promise<Output<PreliminaryMeasureInputInformation>> {
  const formData = new FormData();
  formData.append("communication_date", communication_date);
  if (local_police_number !== null && local_police_number > 0) {
    formData.append("local_police_number", local_police_number.toString());
  }

  for (let i = 0; i < file.length; i++) {
    formData.append("file", file[i]);
  }
  if (coopeuch_registry_image) {
    for (let i = 0; i < coopeuch_registry_image.length; i++) {
      formData.append("coopeuch_registry_image", coopeuch_registry_image[i]);
    }  
  }
  if (transaction_to_self_image) {
    for (let i = 0; i < transaction_to_self_image.length; i++) {
      formData.append("transaction_to_self_image", transaction_to_self_image[i]);
    }  
  }
  if (user_report_image) {
    for (let i = 0; i < user_report_image.length; i++) {
      formData.append("user_report_image", user_report_image[i]);
    }  
  }
  if (payment_to_account_image) {
    for (let i = 0; i < payment_to_account_image.length; i++) {
      formData.append("payment_to_account_image", payment_to_account_image[i]);
    }  
  }
  if (safesigner_report_image) {
    for (let i = 0; i < safesigner_report_image.length; i++) {
      formData.append("safesigner_report_image", safesigner_report_image[i]);
    }  
  }
  if (mastercard_connect_report_image) {
    for (let i = 0; i < mastercard_connect_report_image.length; i++) {
      formData.append("mastercard_connect_report_image", mastercard_connect_report_image[i]);
    }  
  }
  if (celmedia_report_image) {
    for (let i = 0; i < celmedia_report_image.length; i++) {
      formData.append("celmedia_report_image", celmedia_report_image[i]);
    }  
  }

  return await sendRequest<Output<PreliminaryMeasureInputInformation>>(
    "/extract/preliminary-measure-input/",
    "POST",
    formData,
  );
}

/**
 * Sends a request to generate preliminary measure with the provided structure.
 */
async function generatePreliminaryMeasureFromStructure(
  structure: PreliminaryMeasureInputInformation,
): Promise<Blob> {
  return await sendRequest<Blob>(
    "/generate/preliminary-measure-from-structure/",
    "POST",
    JSON.stringify(structure),
    { "Content-Type": "application/json" },
  );
}

export { extractPreliminaryMeasureInput, generatePreliminaryMeasureFromStructure };
