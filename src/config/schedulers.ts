type SchedulerName = "cars" | "coe";

type ScheduleOptions =
  | string
  | {
      pattern: string;
      timezone?: string;
    };

export const schedulers: Record<SchedulerName, ScheduleOptions> = {
  cars: "*/60 0-10 * * 1-5",
  coe: "*/60 0-10 * * 1-5",
};
