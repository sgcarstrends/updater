import redis from "@/config/redis";
import type { ScheduleOptions, SchedulerName } from "@/config/schedulers";
import type { UpdaterResult } from "@/lib/updater";
import { logger, schedules } from "@trigger.dev/sdk/v3";

type UpdaterFunction = () => Promise<UpdaterResult>;

export const createUpdateTask = (
  id: SchedulerName,
  cron: ScheduleOptions,
  updaterFn: UpdaterFunction,
) => {
  return schedules.task({
    id,
    cron,
    run: async (payload: any, { ctx }) => {
      logger.log(`Starting ${id} Update Task`, { payload, ctx });

      try {
        const response = await updaterFn();

        logger.log(`${id} Update Completed`, {
          recordsProcessed: response.recordsProcessed,
          message: response.message,
          timestamp: response.timestamp,
        });

        return response;
      } catch (error) {
        logger.error(`${id} Update Task Failed`, { error });
        throw error;
      }
    },
    onSuccess: async () => {
      const now = Date.now();
      await redis.set(`lastUpdated:${id.toLowerCase()}`, now);
      logger.log(`Last updated (${id})`, { timestamp: now });
    },
  });
};
