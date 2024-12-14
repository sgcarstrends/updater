import fs from "fs";
import Papa from "papaparse";

export const processCSV = async (
  filePath: string,
): Promise<Record<string, any>> => {
  const fileContent = fs.readFileSync(filePath, "utf-8");

  return new Promise((resolve, reject) => {
    Papa.parse(fileContent, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      transform: (value) => {
        if (/\d+,\d+/.test(value)) {
          if (value === "") {
            return 0;
          }
          const cleanValue = value.replace(/,/g, "");
          return cleanValue.includes(".")
            ? parseFloat(cleanValue)
            : parseInt(cleanValue, 10);
        }
        return value;
      },
      complete: ({ data }: { data: Record<string, any>[] }) => {
        resolve(data);
      },
      error: (error: any) => {
        console.error(error);
        reject(error);
      },
    });
  });
};
