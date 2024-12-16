import fs from "node:fs";
import Papa from "papaparse";

export const processCSV = async (filePath: string) => {
	const fileContent = fs.readFileSync(filePath, "utf-8");

	const { data } = Papa.parse(fileContent, {
		header: true,
		dynamicTyping: true,
		skipEmptyLines: true,
		transform: (value, field) => {
			// Handle empty number field
			if (field === "number" && value === "") {
				return 0;
			}

			// Clean up make field
			if (field === "make") {
				return value.trim().replace(/\./g, "");
			}

			// Handle numeric values with commas
			if (/\d+,\d+/.test(value)) {
				return Number.parseInt(value.replace(/,/g, ""), 10);
			}

			return value;
		},
	});

	return data;
};
