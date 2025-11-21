"use client";

import BasePDFViewer from "@/components/pdf/base-pdf-viewer";
import { PDF_URL } from "@/config";

interface PDFURLViewerProps {
  url: string;
}

const PDFURLViewer = ({ url }: PDFURLViewerProps) => {
  const pdfUrl = `${PDF_URL}/${url}`;
  return (
    <BasePDFViewer url={pdfUrl}/>
  );  
};

export default PDFURLViewer;
