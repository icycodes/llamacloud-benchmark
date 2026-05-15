# Parse a PDF Document to Markdown with LlamaParse (TypeScript)

## Background
You are working in `/home/user/myproject`, which is a pre-initialized Node.js project. It already contains:

- A sample one-page PDF at `/home/user/myproject/sample.pdf` (it embeds the literal text `Hello LlamaParse - Harbor Test Document`).
- A `package.json` with `"type": "module"`.
- Pre-installed npm dependencies in `node_modules/`: the [`@llamaindex/llama-cloud`](https://www.npmjs.com/package/@llamaindex/llama-cloud) TypeScript SDK and [`tsx`](https://www.npmjs.com/package/tsx) (for running TypeScript files directly).

Your job is to build a small TypeScript command-line utility that uses the LlamaCloud TypeScript SDK to parse a PDF document via the managed LlamaParse service and persist the parsed markdown content to disk.

The SDK is already installed in the environment and the `LLAMA_CLOUD_API_KEY` environment variable is configured. You do NOT need to handle authentication explicitly — the SDK reads the API key from the environment automatically when you call `new LlamaCloud()`.

## Requirements
- Implement a TypeScript CLI named `parse.ts` at `/home/user/myproject/parse.ts`.
- The script must accept exactly two command-line arguments:
  - `--input <path>`: the path to the local PDF file to parse.
  - `--output <path>`: the path where the parsed markdown should be written.
- The script must use the **`@llamaindex/llama-cloud`** TypeScript SDK (`import LlamaCloud from "@llamaindex/llama-cloud"`).
- Upload the input file with `purpose: "parse"` and then run a parsing job using **tier `cost_effective`** and **version `latest`**. Request markdown output via the `expand` parameter (i.e., `expand: ["markdown"]`).
- After the job completes, write the **per-page markdown joined into a single document** to the `--output` file. Pages must be joined with two consecutive newline characters (`\n\n`) between adjacent pages, in their original page order.
- Print a single line to stdout in the exact format: `Parsed <N> pages` where `<N>` is the number of pages returned by the parse job (i.e., `result.markdown.pages.length`).
- The script must exit with status code `0` on success and a **non-zero** status code if the `--input` path does not exist (i.e., it MUST fail fast instead of silently uploading nothing).

## Implementation Guide
1. The project is already initialized at `/home/user/myproject` with `"type": "module"` in `package.json` and the `@llamaindex/llama-cloud` and `tsx` packages in `node_modules/`. Do NOT run `npm install` — work directly with the existing dependencies.
2. Create `/home/user/myproject/parse.ts`.
3. Parse `--input` and `--output` from `process.argv` (you can use Node's built-in `node:util` `parseArgs`, or any other approach — no extra npm packages are required).
4. Validate that the `--input` file exists before uploading (e.g., with `fs.existsSync`). If it does not, print an error message and exit with a non-zero status code.
5. Import `LlamaCloud` from `@llamaindex/llama-cloud` and instantiate a client (no arguments — it reads `LLAMA_CLOUD_API_KEY` from the environment).
6. Upload the file via `client.files.create({ file: fs.createReadStream(inputPath), purpose: "parse" })`.
7. Trigger a parse job via `client.parsing.parse({ file_id: ..., tier: "cost_effective", version: "latest", expand: ["markdown"] })`. The SDK blocks until the job completes.
8. Iterate over `result.markdown.pages` (each page exposes a `markdown` field), join the per-page markdown strings with `\n\n`, and write the joined string to `--output` (e.g., with `fs.writeFileSync`).
9. Print `Parsed <N> pages` to stdout where `<N>` equals `result.markdown.pages.length`.
10. Run the script with `npx tsx parse.ts --input <pdf_path> --output <output_md_path>` from `/home/user/myproject`.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Script path: `/home/user/myproject/parse.ts`
- Command: `npx tsx parse.ts --input <pdf_path> --output <output_md_path>` (run from `/home/user/myproject`)
- Input argument format: `--input <path_to_pdf>` and `--output <path_to_output_markdown_file>`
- Expected command output: stdout must include exactly one line `Parsed <N> pages` where `<N>` is the page count returned by LlamaParse.
- The output markdown file must be created at the path specified by `--output` and must contain the per-page markdown joined with `\n\n` between pages.
- The script must use the `@llamaindex/llama-cloud` TypeScript SDK with `tier: "cost_effective"`, `version: "latest"`, and `expand` including `"markdown"`.
- The script must succeed (exit code 0) when given a valid PDF and a valid `LLAMA_CLOUD_API_KEY`.
- The script must exit with a non-zero status code when `--input` refers to a non-existent file.

