import { pgTable, serial, text, integer, uuid } from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

export const cars = pgTable("cars", {
  id: uuid("uuid1").default(sql`gen_random_uuid()`),
  month: text(),
  make: text(),
  importerType: text("importer_type"),
  fuelType: text("fuel_type"),
  vehicleType: text("vehicle_type"),
  number: integer(),
});

export const coe = pgTable("coe", {
  id: uuid("uuid1").default(sql`gen_random_uuid()`),
  month: text(),
  biddingNo: integer("bidding_no"),
  vehicleClass: text("vehicle_class"),
  quota: integer(),
  bidsSuccess: integer("bids_success"),
  bidsReceived: integer("bids_received"),
  premium: integer(),
});
