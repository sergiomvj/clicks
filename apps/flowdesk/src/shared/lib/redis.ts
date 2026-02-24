import Redis from "ioredis";

const redisUrl = process.env.REDIS_URL || "redis://localhost:6379";

const globalForRedis = global as unknown as {
    redis: Redis | undefined;
    pub: Redis | undefined;
    sub: Redis | undefined;
};

export const redis = globalForRedis.redis ?? new Redis(redisUrl, {
    maxRetriesPerRequest: null,
});

export const pub = globalForRedis.pub ?? new Redis(redisUrl, {
    maxRetriesPerRequest: null,
});

export const sub = globalForRedis.sub ?? new Redis(redisUrl, {
    maxRetriesPerRequest: null,
});

if (process.env.NODE_ENV !== "production") {
    globalForRedis.redis = redis;
    globalForRedis.pub = pub;
    globalForRedis.sub = sub;
}
