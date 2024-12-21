import { AWS_LAMBDA_TEMP_DIR } from "@/config";
import AdmZip from "adm-zip";

export const downloadFile = async (url: string) => {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Get the ArrayBuffer from the response
    const arrayBuffer = await response.arrayBuffer();

    // Create a new zip instance from the downloaded data
    const zip = new AdmZip(Buffer.from(arrayBuffer));

    // Get the first non-directory entry
    const entry = zip.getEntries().find((entry) => !entry.isDirectory);
    if (!entry) {
      throw new Error("No file found in ZIP archive");
    }

    // Log the found filename
    console.log("Found file in ZIP:", entry.entryName);

    // Extract the ZIP contents to temp directory
    zip.extractEntryTo(entry.entryName, AWS_LAMBDA_TEMP_DIR, true, true);

    // Return the path to the extracted CSV file
    return entry.entryName;
  } catch (error) {
    console.error("Error downloading or extracting file:", error);
    throw error;
  }
};
