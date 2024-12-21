import { carsTable } from "@/schema";
import type { Car } from "@/types";
import { updater } from "./updater";

export const updateCars = async () => {
  const zipFileName = "Monthly New Registration of Cars by Make.zip";
  const zipUrl = `https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/${zipFileName}`;
  const keyFields: Array<keyof Car> = ["month"];

  const response = await updater<Car>({
    table: carsTable,
    zipFileName,
    zipUrl,
    keyFields,
    csvTransformOptions: {
      fields: {
        make: (value: string) => value.trim().replace(/\./g, ""),
        vehicle_type: (value: string) => value.trim().replace(/\s*\/\s*/g, "/"),
        number: (value: string | number) => {
          if (value === "") {
            return 0;
          }

          if (typeof value === "string" && /\d+,\d+/.test(value)) {
            return Number.parseInt(value.replace(/,/g, ""), 10);
          }

          return Number(value);
        },
      },
    },
  });
  console.log("response", response);

  return response;
};

export const handler = async () => {
  const response = await updateCars();
  return { statusCode: 200, body: response };
};
