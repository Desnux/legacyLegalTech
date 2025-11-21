import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFAlignedText, PDFDocument, PDFParagraphText, PDFRequestText, PDFSummaryText } from "@/components/pdf";

const styles = StyleSheet.create({
  header: {
    marginBottom: 24,
  },
  court: {
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: 24,
  },
  opening: {
    marginBottom: 12,
    textAlign: "justify",
  },
  summary: {
    marginBottom: 24,
  },
  exceptions: {
    marginBottom: 8,
  },
  main_request: {
    marginBottom: 8,
  },
});

interface PDFDemandExceptionProps {
  header: string | null;
  court: string | null;
  opening: string | null;
  summary: string | null;
  exceptions: string | null;
  main_request: string | null;
  additional_requests: string | null;
}

const PDFDemandException= ({
  header,
  court,
  opening,
  summary,
  exceptions,
  main_request,
  additional_requests,
}: PDFDemandExceptionProps) => {
  return (
    <PDFDocument subject="Texto de excepciones" title="Texto de excepciones">
      { header && <PDFAlignedText style={styles.header} text={header}/> }
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { opening && <PDFParagraphText style={styles.opening} text={opening}/>}
      { exceptions && <PDFParagraphText style={styles.exceptions} text={exceptions}/> }
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
      { additional_requests && <PDFRequestText text={additional_requests}/> }
    </PDFDocument>
  );
};

export default PDFDemandException;
