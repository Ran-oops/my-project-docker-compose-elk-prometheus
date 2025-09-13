import redis
import psycopg2
import os

def get_redis():
    return redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, db=0)

def get_db():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST", "postgres")
    )