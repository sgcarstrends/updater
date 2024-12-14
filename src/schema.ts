import { index, integer, pgTable, text, uuid } from "drizzle-orm/pg-core";

export const carsTable = pgTable(
  "cars",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    month: text("month"),
    make: text("make"),
    importer_type: text("importer_type"),
    fuel_type: text("fuel_type"),
    vehicle_type: text("vehicle_type"),
    number: integer("number"),
  },
  (table) => ({
    monthMakeIdx: index("month_make_idx").on(table.month, table.make),
    monthIdx: index("month_idx").on(table.month),
    makeIdx: index("make_idx").on(table.make),
    fuelTypeIdx: index("fuel_type_idx").on(table.fuel_type),
    makeFuelTypeIdx: index("make_fuel_type_idx").on(
      table.make,
      table.fuel_type,
    ),
    numberIdx: index("number_idx").on(table.number),
  }),
);

export const coeTable = pgTable(
  "coe",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    month: text("month"),
    bidding_no: integer("bidding_no"),
    vehicle_class: text("vehicle_class"),
    quota: integer("quota"),
    bids_success: integer("bids_success"),
    bids_received: integer("bids_received"),
    premium: integer("premium"),
  },
  (table) => ({
    monthVehicleIdx: index("month_vehicle_idx").on(
      table.month,
      table.vehicle_class,
    ),
    vehicleClassIdx: index("vehicle_class_idx").on(table.vehicle_class),
    monthBiddingNoIdx: index("month_bidding_no_idx").on(
      table.month,
      table.bidding_no,
    ),
    premiumIdx: index("premium_idx").on(table.premium),
    bidsIdx: index("bids_idx").on(table.bids_success, table.bids_received),
    monthBiddingNoVehicleClassIdx: index(
      "month_bidding_no_vehicle_class_idx",
    ).on(table.month.desc(), table.bidding_no.desc(), table.vehicle_class),
  }),
);

export type InsertCar = typeof carsTable.$inferInsert;
export type SelectCar = typeof carsTable.$inferSelect;

export type InsertCOE = typeof coeTable.$inferInsert;
export type SelectCOE = typeof coeTable.$inferSelect;