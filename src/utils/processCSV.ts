import fs from "node:fs";
import Papa from "papaparse";

export interface CSVTransformOptions {
  fields?: Record<string, (value: any) => any>;
}

export const processCSV = async (
  filePath: string,
  options: CSVTransformOptions = {},
) => {
  const fileContent = fs.readFileSync(filePath, "utf-8");

  const { fields = {} } = options;
  console.log("fields", fields);

  const { data } = Papa.parse(fileContent, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
    transform: (value, field) => {
      // Check for specific field transformations
      if (fields[field]) {
        return fields[field](value);
      }

      // Default trim
      return typeof value === "string" ? value.trim() : value;
    },
  });

  return data;
};
