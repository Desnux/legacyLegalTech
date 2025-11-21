export let backendUrl = "";

if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
} else if (globalThis.document?.body?.getAttribute("backend-url")) {
    backendUrl = globalThis.document.body.getAttribute("backend-url") as string;
} else {
    backendUrl = "http://localhost:8100/v1";
}

export const BACKEND_URL: string = backendUrl;

export let pdfUrl = "";

if (process.env.NEXT_PUBLIC_PDF_URL) {
    pdfUrl = process.env.NEXT_PUBLIC_PDF_URL;
} else if (globalThis.document?.body?.getAttribute("pdf-url")) {
    pdfUrl = globalThis.document.body.getAttribute("pdf-url") as string;
} else {
    pdfUrl = "https://gpt-strategist.s3.us-east-1.amazonaws.com";
}

export const PDF_URL: string = pdfUrl;