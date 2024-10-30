/** @format */

import { serve, serveDir } from "std/http/mod.ts";

serve((req) => {
  return serveDir(req, { fsRoot: "./public/" });
});
