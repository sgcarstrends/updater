import redis from "@/config/redis";
import { schedulers } from "@/config/schedulers";
import { updateCars } from "@/lib/updateCars";
import { logger, schedules } from "@trigger.dev/sdk/v3";

export const updateCarsTask = schedules.task({
  id: "update-cars",
  cron: schedulers.cars,
  run: async (payload: any, { ctx }) => {
    try {
      logger.log("Starting Cars Update Task", { payload, ctx });

      const response = await updateCars();

      logger.log("Cars Update Completed", {
        recordsProcessed: response.recordsProcessed,
        message: response.message,
        timestamp: response.timestamp,
      });

      return response;
    } catch (error) {
      logger.error("Cars Update Task Failed", { error });
      throw error;
    }
  },
});
