import { Resource } from "sst";
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";

const sql = neon(Resource.DATABASE_URL.value);
export const db = drizzle({ client: sql });
