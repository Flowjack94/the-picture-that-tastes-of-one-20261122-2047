// The picture that tastes of one ingredient — entry program (Node 22, built-ins only).
//
// Writes one image to $MAKEFUN_OUTPUT_DIR/entry.png: a single ripe strawberry,
// drawn entirely in code for this entry, held in this repository as entry.png.
// Deterministic: the same bytes are written on every run.
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir: string = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const here: string = dirname(fileURLToPath(import.meta.url));
const source: string = join(here, "entry.png");

if (!existsSync(source)) {
  throw new Error("entry.png is missing next to main.ts");
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, join(outDir, "entry.png"));
console.log("wrote entry.png to " + outDir);
