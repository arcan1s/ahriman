import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig, type Plugin } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

function rename(oldName: string, newName: string): Plugin {
    return {
        name: "rename",
        enforce: "post",
        generateBundle(_, bundle) {
            if (bundle[oldName]) {
                bundle[oldName].fileName = newName;
            }
        },
    };
}

export default defineConfig({
    plugins: [react(), tsconfigPaths(), rename("index.html", "build-status.jinja2")],
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
