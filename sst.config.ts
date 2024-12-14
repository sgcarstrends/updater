/// <reference path="./.sst/platform/config.d.ts" />

import { CronArgs } from "./.sst/platform/src/components/aws/cron";

export default $config({
  app(input) {
    return {
      name: "sgcarstrends-updater",
      removal: input?.stage === "prod" ? "retain" : "remove",
      home: "aws",
      providers: {
        aws: {
          region: "ap-southeast-1",
        },
      },
    };
  },
  async run() {
    const updateCars = new sst.aws.Function("UpdateCars", {
      handler: "src/lib/updateCars.handler",
      environment: {
        DATABASE_URL: process.env.DATABASE_URL!,
        UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL!,
        UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN!,
      },
    });

    const updateCOE = new sst.aws.Function("UpdateCOE", {
      handler: "src/lib/updateCOE.handler",
      environment: {
        DATABASE_URL: process.env.DATABASE_URL!,
        UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL!,
        UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN!,
      },
    });

    const CRON_SCHEDULERS: Record<string, CronArgs> = {
      cars: {
        schedule: "cron(0/60 0-10 ? * MON-FRI *)",
        job: updateCars.arn,
      },
      coe: {
        schedule: "cron(0/60 0-10 ? * MON-FRI *)",
        job: updateCOE.arn,
      },
      "coe-1st-bidding": {
        schedule: "cron(0/10 8-10 ? * 4#1 *)",
        job: updateCOE.arn,
      },
      "coe-2nd-bidding": {
        schedule: "cron(0/10 8-10 ? * 4#3 *)",
        job: updateCOE.arn,
      },
    };

    Object.entries(CRON_SCHEDULERS).forEach(([key, { schedule, job }]) => {
      new sst.aws.Cron(key, { job, schedule });
    });

    // TODO: Might create an API in the future
    // new sst.aws.Function("Updater", {
    //   handler: "src/index.handler",
    //   environment: {
    //     DATABASE_URL: process.env.DATABASE_URL!,
    //     UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL!,
    //     UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN!,
    //   },
    //   url: true,
    // });
  },
});
