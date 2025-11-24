import React from "react";
import { Document, Font, Page, StyleSheet, View } from "@react-pdf/renderer";

Font.register({
  family: "Arial",
  fonts: [
    {
      src: "/fonts/ARIAL.ttf",
    },
    {
      src: "/fonts/ARIALBD.ttf",
      fontWeight: 'bold',
    },
  ],
});

const styles = StyleSheet.create({
  page: {
    width: "8.5in",
    padding: "1in",
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    fontSize: 10,
    fontFamily: "Arial",
    textAlign: "justify",
  },
  section: {
    flexGrow: 1,
  },
});

interface PDFDocumentProps {
  children: React.ReactNode,
  title?: string,
  subject?: string,
}

const PDFDocument = ({ title, subject, children }: PDFDocumentProps) => {
  return (
    <Document language="es" creator="Neural Team" producer="Neural Team" title={title} subject={subject}>
      <Page size="LEGAL" style={styles.page}>
        <View style={styles.section}>
          {children}
        </View>
      </Page>
    </Document>
  );
};

export default PDFDocument;
