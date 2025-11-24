import { DemandExceptionStructure, DemandTextStructure, DispatchResolutionStructure } from "@/types/demand-text";
import { LegalResolutionStructure } from "@/types/legal-resolution-structure";


  
  export function isDemandTextStructure(content: any): content is DemandTextStructure {
    return (
      typeof
        content.header === "string" ||
        content.header === null &&
      typeof
        content.summary === "string" ||
        content.summary === null &&
      typeof
        content.court === "string" ||
        content.court === null &&
      typeof
        content.opening === "string" ||
        content.opening === null &&
      Array.isArray(content.missing_payment_arguments) &&
      typeof
        content.main_request === "string" ||
        content.main_request === null &&
      typeof
        content.additional_requests === "string" ||
        content.additional_requests === null
    );
  }
  
  export function isDispatchResolutionStructure(content: any): content is DispatchResolutionStructure {
    return (
      typeof
        content.header === "string" ||
        content.header === null &&
      typeof
        content.date_line === "string" ||
        content.date_line === null &&
      typeof
        content.resolution === "string" ||
        content.resolution === null &&
      typeof
        content.footer === "string" ||
        content.footer === null
    );
  }
  
  export function isLegalResolutionStructure(content: any): content is LegalResolutionStructure {
    return (
      typeof
        content.header === "string" ||
        content.header === null &&
      typeof
        content.date_line === "string" ||
        content.date_line === null &&
      typeof
        content.resolution === "string" ||
        content.resolution === null &&
      typeof
        content.footer === "string" ||
        content.footer === null
    );
  }
  
  export function isDemandExceptionStructure(content: any): content is DemandExceptionStructure {
    return (
      typeof
        content.header === "string" ||
        content.header === null &&
      typeof
        content.court === "string" ||
        content.court === null &&
      typeof
        content.opening === "string" ||
        content.opening === null &&
      typeof
        content.summary === "string" ||
        content.summary === null &&
      typeof
        content.exceptions === "string" ||
        content.exceptions === null &&
      typeof
        content.main_request === "string" ||
        content.main_request === null &&
      typeof
        content.additional_requests === "string" ||
        content.additional_requests === null
    );
  }