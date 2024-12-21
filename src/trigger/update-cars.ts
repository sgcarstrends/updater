import { updateCars } from "@/lib/updateCars";
import { logger, task } from "@trigger.dev/sdk/v3";

export const updateCarsTask = task({
  id: "update-cars",
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
