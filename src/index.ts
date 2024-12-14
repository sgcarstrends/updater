import { Hono } from "hono";
import { handle } from "hono/aws-lambda";
import { showRoutes } from "hono/dev";
import { updateCOE } from "./lib/updateCOE";
import { updateCars } from "./lib/updateCars";

const app = new Hono();

// app.get("/updater/coe", async (c) => {
//   const response = await updateCOE();
//
//   return c.json({ message: "Hello World!" });
// });

app.post("/process-cars-data", async (c) => {
	const response = await updateCars();
	return c.json(response);
});

app.post("/process-coe-data", async (c) => {
	const response = await updateCOE();
	return c.json(response);
});

showRoutes(app);

export const handler = handle(app);
