import { Resource } from "sst";
import { Redis } from "@upstash/redis";

export const redis = new Redis({
  url: Resource.UPSTASH_REDIS_REST_URL.value,
  token: Resource.UPSTASH_REDIS_REST_TOKEN.value,
});
