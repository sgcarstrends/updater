import { cars } from "@/schema";
import type { Car } from "@/types";
import { cleanSpecialChars } from "@/utils/cleanSpecialChars";
import { updater } from "./updater";

export const updateCars = async () => {
  const filename = "Monthly New Registration of Cars by Make.zip";
  const url = `https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/${filename}`;
  const keyFields: Array<keyof Car> = [
    "month",
    "make",
    "fuel_type",
    "vehicle_type",
  ];

  const response = await updater<Car>({
    table: cars,
    url,
    keyFields,
    csvTransformOptions: {
      fields: {
        make: (value: string) =>
          cleanSpecialChars(value, { separator: "." }).toUpperCase(),
        vehicle_type: (value: string) =>
          cleanSpecialChars(value, { separator: "/", joinSeparator: "/" }),
        number: (value: string | number) => (value === "" ? 0 : Number(value)),
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
