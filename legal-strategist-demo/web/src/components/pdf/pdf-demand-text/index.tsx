import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFAlignedText, PDFDocument, PDFParagraphText, PDFRequestText, PDFSummaryText } from "@/components/pdf";
import { DemandTextStructure } from "@/types/demand-text";

const styles = StyleSheet.create({
  header: {
    marginBottom: 24,
  },
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
  },
});

interface PDFDemandTextProps extends DemandTextStructure { }

const PDFDemandText = ({ header, summary, court, opening, missing_payment_arguments, main_request, additional_requests }: PDFDemandTextProps) => {
  console.log('PDFDemandText', { header, summary, court, opening, missing_payment_arguments, main_request, additional_requests });
  return (
    <PDFDocument subject="Texto de demanda legal" title="Texto de demanda">
      { header && <PDFAlignedText style={styles.header} text={header}/> }
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { opening && <PDFParagraphText style={styles.opening} text={opening}/>}
      { missing_payment_arguments && missing_payment_arguments.map((segment, index) => <PDFParagraphText key={index} style={styles.missing_payment_arguments} text={segment.argument}/>)}
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
      { additional_requests && <PDFRequestText text={additional_requests}/> }
    </PDFDocument>
  );
};

export default PDFDemandText;
