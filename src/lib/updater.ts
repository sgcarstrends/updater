import path from "node:path";
import { AWS_LAMBDA_TEMP_DIR } from "@/config";
import { db } from "@/db";
import { calculateChecksum } from "@/utils/calculateChecksum";
import { createUniqueKey } from "@/utils/createUniqueKey";
import { downloadFile } from "@/utils/downloadFile";
import { processCSV } from "@/utils/processCSV";
import { cacheChecksum, getCachedChecksum } from "@/utils/redisCache";
import type { PgTable } from "drizzle-orm/pg-core";

export interface UpdaterConfig<T extends PgTable> {
	table: T;
	zipFileName: string;
	zipUrl: string;
	keyFields: string[];
}

export interface UpdaterResult {
	recordsProcessed: number;
	message: string;
	timestamp: string;
}

const BATCH_SIZE = 5000;

export const updater = async <T extends PgTable>({
	table,
	zipFileName,
	zipUrl,
	keyFields,
}: UpdaterConfig<T>): Promise<UpdaterResult> => {
	// Download and extract file
	const extractedFileName = await downloadFile(zipUrl);
	const destinationPath = path.join(AWS_LAMBDA_TEMP_DIR, extractedFileName);
	console.log("Destination path:", destinationPath);

	// Calculate checksum of the downloaded file
	const checksum = await calculateChecksum(destinationPath);
	console.log("Checksum:", checksum);

	// Get previously stored checksum
	const cachedChecksum = await getCachedChecksum(extractedFileName);
	console.log("Cached checksum:", cachedChecksum);

	// TODO: Temporary disable caching while testing
	// if (!cachedChecksum) {
	//   console.log(`No cached checksum found. This might be the first run.`);
	//   await cacheChecksum(extractedFileName, checksum);
	//   console.log(`Checksum for ${zipFileName} cached. Checksum: ${checksum}`);
	//
	//   console.log(
	//     `No cached checksum found. This might be the first run. Checksum for ${zipFileName} cached. Checksum: ${checksum}`,
	//   );
	// } else if (cachedChecksum === checksum) {
	//   console.log(
	//     `File have not been changed since the last update. Checksum: ${checksum}`,
	//   );
	//   return {
	//     recordsProcessed: 0,
	//     message: `File have not been changed since the last update. Checksum: ${checksum}`,
	//     timestamp: new Date().toISOString(),
	//   };
	// }
	//
	// await cacheChecksum(extractedFileName, checksum);
	// console.log("Checksum has been changed.");

	// Process CSV
	const processedData = await processCSV(destinationPath);

	// Create a query to check for existing records
	const existingKeysQuery = await db
		.select(Object.fromEntries(keyFields.map((field) => [field, table[field]])))
		.from(table);

	// Create a Set of existing keys for faster lookup
	const existingKeys = new Set(
		existingKeysQuery.map((record) => createUniqueKey(record, keyFields)),
	);

	// Check against the existing records for new non-duplicated entries
	const newRecords = processedData.filter((record: Record<string, any>) => {
		const identifier = createUniqueKey(record, keyFields);
		return !existingKeys.has(identifier);
	});

	// Return early when there are no new records to be added to the database
	if (newRecords.length === 0) {
		return {
			// table: table.$name,
			recordsProcessed: 0,
			message:
				"No new data to insert. The provided data matches the existing records.",
			timestamp: new Date().toISOString(),
		};
	}

	// Process in batches only if we have new records
	let totalInserted = 0;

	const start = performance.now();
	for (let i = 0; i < newRecords.length; i += BATCH_SIZE) {
		const batch = newRecords.slice(i, i + BATCH_SIZE);
		const inserted = await db.insert(table).values(batch).returning();
		totalInserted += inserted.length;
		console.log(
			`Inserted batch of ${inserted.length} records. Total: ${totalInserted}`,
		);
	}
	const end = performance.now();

	// TODO: Temporary disable caching while testing
	// await cacheChecksum(extractedFileName, checksum);

	return {
		// table: table.$name,
		recordsProcessed: totalInserted,
		message: `${totalInserted} record(s) inserted in ${Math.round(end - start)}ms`,
		timestamp: new Date().toISOString(),
	};
};
