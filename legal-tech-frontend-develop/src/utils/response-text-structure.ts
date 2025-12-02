import { DemandTextCorrectionStructure } from "@/types/demand-text-correction-structure";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";
import { LegalExceptionResponseStructure } from "@/types/legal-exception-response-structure";
import { LegalResponseStructure } from "@/types/legal-response-structure";

export function isLegalResponseStructure(content: any): content is LegalResponseStructure {
    return (
      (typeof content.header === "string" || content.header === null || content.header === undefined) &&
      (typeof content.court === "string" || content.court === null || content.court === undefined) &&
      (typeof content.response === "string" || content.response === null || content.response === undefined) &&
      (typeof content.request === "string" || content.request === null || content.request === undefined)
    );
  }
  
  export function isLegalExceptionResponseStructure(content: any): content is LegalExceptionResponseStructure {
    return (
      (typeof content.header === "string" || content.header === null || content.header === undefined) &&
      (typeof content.summary === "string" || content.summary === null || content.summary === undefined) &&
      (typeof content.court === "string" || content.court === null || content.court === undefined) &&
      (typeof content.opening === "string" || content.opening === null || content.opening === undefined) &&
      (typeof content.compromise_terms === "string" || content.compromise_terms === null || content.compromise_terms === undefined) &&
      (Array.isArray(content.exception_responses) || content.exception_responses === null || content.exception_responses === undefined) &&
      (typeof content.main_request === "string" || content.main_request === null || content.main_request === undefined) &&
      (typeof content.additional_requests === "string" || content.additional_requests === null || content.additional_requests === undefined) &&
      (typeof content.content === "string" || content.content === null || content.content === undefined)
    );
  }
  
  export function isLegalCompromiseStructure(content: any): content is LegalCompromiseStructure {
    return (
      (typeof content.header === "string" || content.header === null || content.header === undefined) &&
      (typeof content.summary === "string" || content.summary === null || content.summary === undefined) &&
      (typeof content.court === "string" || content.court === null || content.court === undefined) &&
      (typeof content.opening === "string" || content.opening === null || content.opening === undefined) &&
      (typeof content.compromise_terms === "string" || content.compromise_terms === null || content.compromise_terms === undefined) &&
      (typeof content.main_request === "string" || content.main_request === null || content.main_request === undefined) &&
      (typeof content.additional_requests === "string" || content.additional_requests === null || content.additional_requests === undefined)
    );
  }
  
  export function isDemandTextCorrectionStructure(content: any): content is DemandTextCorrectionStructure {
    return (
      (typeof content.summary === "string" || content.summary === null || content.summary === undefined) &&
      (typeof content.court === "string" || content.court === null || content.court === undefined) &&
      (typeof content.opening === "string" || content.opening === null || content.opening === undefined) &&
      (typeof content.corrections === "string" || content.corrections === null || content.corrections === undefined) &&
      (typeof content.main_request === "string" || content.main_request === null || content.main_request === undefined) &&
      (typeof content.additional_requests === "string" || content.additional_requests === null || content.additional_requests === undefined)
    );
  }