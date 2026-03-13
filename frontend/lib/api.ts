export type GenerateResponse = {
  status: string;
  markdown: string;
  sources: string[];
};

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function generateGuide(docsUrl: string): Promise<GenerateResponse> {
  const response = await fetch(`${BACKEND_URL}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ docs_url: docsUrl }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Generation failed");
  }

  return response.json();
}
