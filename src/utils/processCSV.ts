import fs from "node:fs";
import Papa from "papaparse";

export const processCSV = async (filePath: string) => {
	const fileContent = fs.readFileSync(filePath, "utf-8");

	const { data } = Papa.parse(fileContent, {
		header: true,
		dynamicTyping: true,
		skipEmptyLines: true,
		transform: (value, field) => {
			const trimmedValue = value.trim();

			// Handle empty number field
			if (field === "number" && trimmedValue === "") {
				return 0;
			}

			// Clean up make field
			if (field === "make") {
				return trimmedValue.replace(/\./g, "");
			}

			// Clean up vehicle_type field
			if (field === "vehicle_type") {
				return trimmedValue.replace(/\s*\/\s*/g, "/");
			}

			// Handle numeric values with commas
			if (/\d+,\d+/.test(trimmedValue)) {
				return Number.parseInt(trimmedValue.replace(/,/g, ""), 10);
			}

			return trimmedValue;
		},
	});

	return data;
};
