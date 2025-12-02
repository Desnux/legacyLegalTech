import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFDocument, PDFParagraphText, PDFRequestText } from "@/components/pdf";
import { LegalResponseStructure } from "@/types/legal-response-structure";

const styles = StyleSheet.create({
  header: {
    marginBottom: 24,
  },
  court: {
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 24,
  },
  response: {
    marginBottom: 8,
  },
  request: {
    marginTop: 8,
  },
});

interface PDFLegalResponseProps extends LegalResponseStructure { }

const PDFLegalResponse = ({ header, court, response, request }: PDFLegalResponseProps) => {
  return (
    <PDFDocument subject="Respuesta" title="Respuesta">
      { header && <Text style={styles.header}>{header}</Text> }
      { court && <Text style={styles.court}>{court}</Text> }
      { response && <PDFParagraphText style={styles.response} text={response}/> }
      { request && <PDFRequestText style={styles.request} text={request}/> }
    </PDFDocument>
  );
};

export default PDFLegalResponse;
