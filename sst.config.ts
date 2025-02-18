/// <reference path="./.sst/platform/config.d.ts" />

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
    const environment = {
      DATABASE_URL: process.env.DATABASE_URL,
      UPSTASH_REDIS_REST_URL: process.env.UPSTASH_REDIS_REST_URL,
      UPSTASH_REDIS_REST_TOKEN: process.env.UPSTASH_REDIS_REST_TOKEN,
    };

    // TODO: Temporary remove Secrets
    // const DATABASE_URL = new sst.Secret(
    //   "DATABASE_URL",
    //   environment.DATABASE_URL,
    // );
    // const UPSTASH_REDIS_REST_URL = new sst.Secret(
    //   "UPSTASH_REDIS_REST_URL",
    //   environment.UPSTASH_REDIS_REST_URL,
    // );
    // const UPSTASH_REDIS_REST_TOKEN = new sst.Secret(
    //   "UPSTASH_REDIS_REST_TOKEN",
    //   environment.UPSTASH_REDIS_REST_TOKEN,
    // );

    // TODO: Might create an API in the future
    new sst.aws.Function("Updater", {
      handler: "src/index.handler",
      environment,
      url: true,
    });
  },
});
