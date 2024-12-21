import { coe } from "@/schema";
import type { COE } from "@/types";
import { updater } from "./updater";

export const updateCOE = async () => {
  const filename = "COE Bidding Results.zip";
  const url = `https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/${filename}`;
  const keyFields: Array<keyof COE> = ["month", "bidding_no"];

  const parseNumericString = (value: string | number) => {
    if (typeof value === "string") {
      return Number.parseInt(value.replace(/,/g, ""), 10);
    }

    return value;
  };

  const parseNumericFields: Array<keyof COE> = [
    "quota",
    "bids_success",
    "bids_received",
  ];

  const response = await updater<COE>({
    table: coe,
    url: url,
    keyFields,
    csvTransformOptions: {
      fields: Object.fromEntries(
        parseNumericFields.map((field) => [field, parseNumericString]),
      ),
    },
  });
  console.log("response", response);

  return response;
};

export const handler = async () => {
  const response = await updateCOE();
  return { statusCode: 200, body: response };
};
