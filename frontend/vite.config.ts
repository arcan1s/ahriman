import react from "@vitejs/plugin-react";
import path from "path";
import { defineConfig, type Plugin } from "vite";

function rename(oldName: string, newName: string): Plugin {
    return {
        enforce: "post",
        generateBundle(_, bundle) {
            if (bundle[oldName]) {
                bundle[oldName].fileName = newName;
            }
        },
        name: "rename",
    };
}

export default defineConfig({
    base: "/",
    build: {
        chunkSizeWarningLimit: 10000,
        emptyOutDir: false,
        outDir: path.resolve(__dirname, "../package/share/ahriman/templates"),
        rolldownOptions: {
            output: {
                assetFileNames: "static/[name].[ext]",
                chunkFileNames: "static/[name].js",
                entryFileNames: "static/[name].js",
            },
        },
    },
    plugins: [react(), rename("index.html", "build-status.jinja2")],
    resolve: {
        tsconfigPaths: true,
    },
    server: {
        proxy: {
            "/api": "http://localhost:8080",
        },
    },
});
