import { carsTable } from "@/schema";
import { updater } from "./updater";

export const updateCars = async () => {
	const zipFileName = "Monthly New Registration of Cars by Make.zip";
	const zipUrl = `https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/${zipFileName}`;
	const keyFields = ["month"];

	const response = await updater({
		table: carsTable,
		zipFileName,
		zipUrl,
		keyFields,
	});
	console.log("response", response);

	return response;
};

export const handler = async () => {
	const response = await updateCars();
	return { statusCode: 200, body: response };
};
