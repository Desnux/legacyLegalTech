import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFDocument, PDFParagraphText, PDFRequestText, PDFSummaryText } from "@/components/pdf";
import { LegalCompromiseStructure } from "@/types/legal-compromise-structure";

const styles = StyleSheet.create({
  summary: {
    marginBottom: 24,
  },
  court: {
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 24,
  },
  opening: {
    marginBottom: 8,
  },
  missing_payment_arguments: {
    marginBottom: 8,
  },
  main_request: {
    marginBottom: 8,
  }
});

interface PDFLegalCompromiseProps extends LegalCompromiseStructure { }

const PDFLegalCompromise = ({ summary, court, opening, compromise_terms, main_request, additional_requests }: PDFLegalCompromiseProps) => {
  return (
    <PDFDocument subject="Avenimiento" title="Avenimiento">      
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { opening && <PDFParagraphText style={styles.opening} text={opening}/>}
      { compromise_terms && <PDFParagraphText text={compromise_terms} />}
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
      { additional_requests && <PDFRequestText text={additional_requests}/> }
    </PDFDocument>
  );
};

export default PDFLegalCompromise;
