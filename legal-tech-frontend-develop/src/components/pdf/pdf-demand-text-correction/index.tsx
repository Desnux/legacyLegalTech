import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFDocument, PDFParagraphText, PDFRequestText, PDFSummaryText } from "@/components/pdf";
import { DemandTextCorrectionStructure } from "@/types/demand-text-correction-structure";

const styles = StyleSheet.create({
  summary: {
    marginBottom: 24,
  },
  court: {
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 24,
  },
  corrections: {
    marginBottom: 8,
  },
  opening: {
    marginBottom: 8,
  },
  main_request: {
    marginBottom: 8,
  }
});

interface PDFDemandTextCorrectionProps extends DemandTextCorrectionStructure { }

const PDFDemandTextCorrection = ({ summary, court, opening, corrections, main_request, additional_requests }: PDFDemandTextCorrectionProps) => {
  return (
    <PDFDocument subject="Rectifica demanda" title="Rectifica demanda">      
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { opening && <PDFParagraphText style={styles.opening} text={opening}/>}
      { corrections && <PDFParagraphText style={styles.corrections} text={corrections} />}
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
      { additional_requests && <PDFRequestText text={additional_requests}/> }
    </PDFDocument>
  );
};

export default PDFDemandTextCorrection;
