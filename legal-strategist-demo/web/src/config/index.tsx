export let backendUrl = "";

if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
} else if (globalThis.document?.body?.getAttribute("backend-url")) {
    backendUrl = globalThis.document.body.getAttribute("backend-url") as string;
} else {
    backendUrl = "http://localhost:8100/v1";
}

export const BACKEND_URL: string = backendUrl;
