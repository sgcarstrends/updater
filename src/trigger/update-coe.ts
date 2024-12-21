import { updateCOE } from "@/lib/updateCOE";
import { logger, task } from "@trigger.dev/sdk/v3";

export const updateCOETask = task({
  id: "update-coe",
  run: async (payload: any, { ctx }) => {
    try {
      logger.log("Starting COE Update Task", { payload, ctx });

      const response = await updateCOE();

      logger.log("COE Update Completed", {
        recordsProcessed: response.recordsProcessed,
        message: response.message,
        timestamp: response.timestamp,
      });

      return response;
    } catch (error) {
      logger.error("COE Update Task Failed", { error });
      throw error;
    }
  },
});
