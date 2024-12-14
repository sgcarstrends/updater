import { downloadFile } from "../utils/downloadFile";
import { AWS_LAMBDA_TEMP_DIR } from "../config";
import path from "node:path";
import { calculateChecksum } from "../utils/calculateChecksum";
import { cacheChecksum, getCachedChecksum } from "../utils/redisCache";
import { processCSV } from "../utils/processCSV";
import { db } from "../db";
import { PgTable } from "drizzle-orm/pg-core";
import { createUniqueKey } from "../utils/createUniqueKey";

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

const downloadAndPrepareFile = async (zipUrl: string): Promise<string> => {
  const extractedFileName = await downloadFile(zipUrl);
  const destinationPath = path.join(AWS_LAMBDA_TEMP_DIR, extractedFileName);
  console.log("Destination path:", destinationPath);
  return destinationPath;
};

const validateFileChecksum = async (
  extractedFileName: string,
  destinationPath: string,
): Promise<{ checksum: string; isNewOrChanged: boolean }> => {
  const checksum = await calculateChecksum(destinationPath);
  console.log("Checksum:", checksum);

  const cachedChecksum = await getCachedChecksum(extractedFileName);
  console.log("Cached checksum:", cachedChecksum);

  if (!cachedChecksum) {
    console.log(`No cached checksum found. This might be the first run.`);
    await cacheChecksum(extractedFileName, checksum);
    return { checksum, isNewOrChanged: true };
  }

  const isNewOrChanged = cachedChecksum !== checksum;
  if (!isNewOrChanged) {
    console.log(
      `File has not been changed since the last update. Checksum: ${checksum}`,
    );
  }

  return { checksum, isNewOrChanged };
};

const findNewRecords = async <T extends PgTable>(
  table: T,
  processedData: Record<string, any>[],
  keyFields: string[],
): Promise<Record<string, any>[]> => {
  const existingKeysQuery = await db
    .select(Object.fromEntries(keyFields.map((field) => [field, table[field]])))
    .from(table);

  const existingKeys = new Set(
    existingKeysQuery.map((record) => createUniqueKey(record, keyFields)),
  );

  return processedData.filter((record) => {
    const identifier = createUniqueKey(record, keyFields);
    return !existingKeys.has(identifier);
  });
};

const insertRecordBatches = async <T extends PgTable>(
  table: T,
  newRecords: Record<string, any>[],
): Promise<{ totalInserted: number; duration: number }> => {
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
  const duration = Math.round(end - start);

  return { totalInserted, duration };
};

export const updater = async <T extends PgTable>({
  table,
  zipFileName,
  zipUrl,
  keyFields,
}: UpdaterConfig<T>): Promise<UpdaterResult> => {
  try {
    // Download and prepare file
    const destinationPath = await downloadAndPrepareFile(zipUrl);

    // Validate file checksum
    const { checksum, isNewOrChanged } = await validateFileChecksum(
      zipFileName,
      destinationPath,
    );

    // If file is not changed, return early
    if (!isNewOrChanged) {
      return {
        recordsProcessed: 0,
        message: `File has not been changed since the last update. Checksum: ${checksum}`,
        timestamp: new Date().toISOString(),
      };
    }

    // Process CSV
    const processedData = await processCSV(destinationPath);

    // Find new records
    const newRecords = await findNewRecords(table, processedData, keyFields);

    // Return early if no new records
    if (newRecords.length === 0) {
      return {
        recordsProcessed: 0,
        message:
          "No new data to insert. The provided data matches existing records.",
        timestamp: new Date().toISOString(),
      };
    }

    // Insert records in batches
    const { totalInserted, duration } = await insertRecordBatches(
      table,
      newRecords,
    );

    // Cache the new checksum
    await cacheChecksum(zipFileName, checksum);

    return {
      recordsProcessed: totalInserted,
      message: `${totalInserted} record(s) inserted in ${duration}ms`,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.error("Error in updater:", error);
    return {
      recordsProcessed: 0,
      message: `Error during update: ${error instanceof Error ? error.message : "Unknown error"}`,
      timestamp: new Date().toISOString(),
    };
  }
};
