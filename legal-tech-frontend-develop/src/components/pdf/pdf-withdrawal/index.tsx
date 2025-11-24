import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFAlignedText, PDFDocument, PDFParagraphText, PDFSummaryText } from "@/components/pdf";
import { WithdrawalStructure } from "@/types/withdrawal-structure";

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
  content: {
    marginBottom: 8,
  },
  main_request: {
    marginBottom: 8,
  }
});

interface PDFWithdrawalProps extends WithdrawalStructure { }

const PDFWithdrawal = ({ header, summary, court, content, main_request }: PDFWithdrawalProps) => {
  return (
    <PDFDocument subject="Desistimiento" title="Desistimiento">
      { header && <PDFAlignedText style={styles.header} text={header}/> }
      { summary && <PDFSummaryText style={styles.summary} text={summary}/> }
      { court && <Text style={styles.court}>{court}</Text> }
      { content && <PDFParagraphText style={styles.content} text={content}/>}
      { main_request && <PDFParagraphText style={styles.main_request} text={main_request} />}
    </PDFDocument>
  );
};

export default PDFWithdrawal;
