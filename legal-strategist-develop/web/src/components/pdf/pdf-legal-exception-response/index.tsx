import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFDocument, PDFParagraphText, PDFRequestText, PDFSummaryText } from "@/components/pdf";
import { LegalExceptionResponseStructure } from "@/types/legal-exception-response-structure";

const styles = StyleSheet.create({
  summary: {
    marginBottom: 24,
  },
  court: {
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 24,
  },
  exception_responses: {
    marginBottom: 8,
  },
  opening: {
    marginBottom: 8,
  },
  main_request: {
    marginBottom: 8,
  }
});

interface PDFLegalExceptionResponseProps extends LegalExceptionResponseStructure { }

const PDFLegalExceptionResponse = ({ summary, court, opening, exception_responses, main_request, additional_requests }: PDFLegalExceptionResponseProps) => {
  return (
    <PDFDocument subject="Respuesta a excepciones" title="Respuesta a excepciones">      
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { opening && <PDFParagraphText style={styles.opening} text={opening}/>}
      { exception_responses && exception_responses.map((segment, index) => <PDFParagraphText key={index} style={styles.exception_responses} text={segment}/>)}
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
      { additional_requests && <PDFRequestText text={additional_requests}/> }
    </PDFDocument>
  );
};

export default PDFLegalExceptionResponse;
