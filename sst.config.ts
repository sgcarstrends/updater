/// <reference path="./.sst/platform/config.d.ts" />

import type { CronArgs } from "./.sst/platform/src/components/aws/cron";

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
    const DATABASE_URL = new sst.Secret(
      "DATABASE_URL",
      process.env.DATABASE_URL,
    );
    const UPSTASH_REDIS_REST_URL = new sst.Secret(
      "UPSTASH_REDIS_REST_URL",
      process.env.UPSTASH_REDIS_REST_URL,
    );
    const UPSTASH_REDIS_REST_TOKEN = new sst.Secret(
      "UPSTASH_REDIS_REST_TOKEN",
      process.env.UPSTASH_REDIS_REST_TOKEN,
    );

    const updateCars = new sst.aws.Function("UpdateCars", {
      link: [DATABASE_URL, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN],
      handler: "src/lib/updateCars.handler",
    });

    const updateCOE = new sst.aws.Function("UpdateCOE", {
      link: [DATABASE_URL, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN],
      handler: "src/lib/updateCOE.handler",
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

    for (const [key, { schedule, job }] of Object.entries(CRON_SCHEDULERS)) {
      new sst.aws.Cron(key, { job, schedule });
    }

    // TODO: Might create an API in the future
    new sst.aws.Function("Updater", {
      link: [DATABASE_URL, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN],
      handler: "src/index.handler",
      url: true,
    });
  },
});
