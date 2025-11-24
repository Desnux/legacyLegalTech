import React from "react";
import { StyleSheet, Text } from "@react-pdf/renderer";
import { PDFAlignedText, PDFDocument, PDFParagraphText } from "@/components/pdf";

const styles = StyleSheet.create({
  header: {
    marginBottom: 24,
  },
  dateLine: {
    marginBottom: 24,
    fontWeight: "bold",
  },
  resolution: {
    marginBottom: 8,
  },
  footer: {
    marginTop: 8,
    fontWeight: "bold",
  },
});

interface PDFDispatchResolutionProps {
  header: string | null;
  date_line: string | null;
  resolution: string | null;
  footer: string | null;
}

const PDFDispatchResolution = ({ header, date_line, resolution, footer }: PDFDispatchResolutionProps) => {
  return (
    <PDFDocument subject="Resolución despáchese" title="Resolución despáchese">
      { header && <PDFAlignedText style={styles.header} text={header}/> }
      { date_line && <Text style={styles.dateLine}>{date_line}</Text> }
      { resolution && <PDFParagraphText style={styles.resolution} text={resolution}/> }
      { footer && <Text style={styles.footer}>{footer}</Text> }
    </PDFDocument>
  );
};

export default PDFDispatchResolution;
