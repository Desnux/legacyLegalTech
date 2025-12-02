export let backendUrl = "";

if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
} else if (globalThis.document?.body?.getAttribute("backend-url")) {
    backendUrl = globalThis.document.body.getAttribute("backend-url") as string;
} else {
    backendUrl = "http://localhost:8100/v1";
}

export const BACKEND_URL: string = backendUrl;

let recepthorUrl = "";
let recepthorCaptchaToken = "";
let recepthorEmail = "";
let recepthorPassword = "";
let recepthorSkipCaptchaToken = "";

if (process.env.NEXT_PUBLIC_RECEPTHOR_URL && process.env.NEXT_PUBLIC_RECEPTHOR_CAPTCHA_TOKEN && process.env.NEXT_PUBLIC_RECEPTHOR_EMAIL && process.env.NEXT_PUBLIC_RECEPTHOR_PASSWORD && process.env.NEXT_PUBLIC_RECEPTHOR_SKIP_CAPTCHA_TOKEN) {
    recepthorUrl = process.env.NEXT_PUBLIC_RECEPTHOR_URL;
    recepthorCaptchaToken = process.env.NEXT_PUBLIC_RECEPTHOR_CAPTCHA_TOKEN;
    recepthorEmail = process.env.NEXT_PUBLIC_RECEPTHOR_EMAIL;
    recepthorPassword = process.env.NEXT_PUBLIC_RECEPTHOR_PASSWORD;
    recepthorSkipCaptchaToken = process.env.NEXT_PUBLIC_RECEPTHOR_SKIP_CAPTCHA_TOKEN;
} else {
    recepthorUrl = "";
    recepthorCaptchaToken = "";
    recepthorEmail = "";
    recepthorPassword = "";
    recepthorSkipCaptchaToken = "";
}

export const RECEPTHOR_URL: string = recepthorUrl;
export const RECEPTHOR_CAPTCHA_TOKEN: string = recepthorCaptchaToken;
export const RECEPTHOR_EMAIL: string = recepthorEmail;
export const RECEPTHOR_PASSWORD: string = recepthorPassword;
export const RECEPTHOR_SKIP_CAPTCHA_TOKEN: string = recepthorSkipCaptchaToken;

export let pdfUrl = "";

if (process.env.NEXT_PUBLIC_PDF_URL) {
    pdfUrl = process.env.NEXT_PUBLIC_PDF_URL;
} else if (globalThis.document?.body?.getAttribute("pdf-url")) {
    pdfUrl = globalThis.document.body.getAttribute("pdf-url") as string;
} else {
    pdfUrl = "https://legal-tech-documents.s3.us-east-2.amazonaws.com";
}

export const PDF_URL: string = pdfUrl;