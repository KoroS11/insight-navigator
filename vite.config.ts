import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

function normalizeBasePath(basePath: string): string {
  const trimmed = basePath.trim();
  if (!trimmed) return "/";
  const withLeadingSlash = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
  return withLeadingSlash.endsWith("/") ? withLeadingSlash : `${withLeadingSlash}/`;
}

function resolveBasePath(): string {
  if (process.env.VITE_BASE_PATH) {
    return normalizeBasePath(process.env.VITE_BASE_PATH);
  }

  if (process.env.GITHUB_ACTIONS === "true") {
    const repoName = process.env.GITHUB_REPOSITORY?.split("/")[1] ?? "";
    return normalizeBasePath(repoName ? `/${repoName}/` : "/");
  }

  return "/";
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  base: resolveBasePath(),
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
