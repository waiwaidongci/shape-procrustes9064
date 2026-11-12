import {defineConfig} from 'vite';export default defineConfig({esbuild:{jsx:'automatic'},server:{proxy:{'/api':{target:'http://localhost:19234',rewrite:path=>path.replace(/^\/api/,'')}}}});
