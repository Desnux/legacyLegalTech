"use client";

import BasePDFViewer from "@/components/pdf/base-pdf-viewer";

interface PDFBlobViewerProps {
  className?: string;
  filename?: string;
  blob: Blob;
}

const PDFBlobViewer = ({ className, filename, blob }: PDFBlobViewerProps) => {
  const pdfUrl = URL.createObjectURL(blob);

  return (
    <BasePDFViewer className={className} filename={filename} url={pdfUrl}/>
  );  
};

export default PDFBlobViewer;
