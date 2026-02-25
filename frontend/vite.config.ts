import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import path from "path";

function renameHtml(newName: string): Plugin {
    return {
        name: "rename-html",
        enforce: "post",
        generateBundle(_, bundle) {
            if (bundle["index.html"]) {
                bundle["index.html"].fileName = newName;
            }
        },
    };
}

export default defineConfig({
    plugins: [react(), tsconfigPaths(), renameHtml("build-status.jinja2")],
    base: "/",
    build: {
        chunkSizeWarningLimit: 10000,
        emptyOutDir: false,
        outDir: path.resolve(__dirname, "../package/share/ahriman/templates"),
        rollupOptions: {
            output: {
                entryFileNames: "static/[name].js",
                chunkFileNames: "static/[name].js",
                assetFileNames: "static/[name].[ext]",
            },
        },
    },
    server: {
        proxy: {
            "/api": "http://localhost:8080",
        },
    },
});
