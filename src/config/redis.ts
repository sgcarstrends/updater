import { Redis } from "@upstash/redis";
import { Resource } from "sst";

export const redis = new Redis({
  url: Resource.UPSTASH_REDIS_REST_URL.value,
  token: Resource.UPSTASH_REDIS_REST_TOKEN.value,
});
