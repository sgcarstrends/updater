import { coeTable } from "@/schema";
import { updater } from "./updater";

export const updateCOE = async () => {
  const zipFileName = "COE Bidding Results.zip";
  const zipUrl = `https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/${zipFileName}`;
  const keyFields = ["month", "bidding_no"];

  const response = await updater({
    table: coeTable,
    zipFileName,
    zipUrl,
    keyFields,
  });
  console.log("response", response);

  return response;
};

export const handler = async () => {
  const response = await updateCOE();
  return { statusCode: 200, body: response };
};
