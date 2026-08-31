#!/bin/sh
set -e

export POSTGRES_BACKEND_URL="postgresql://${POSTGRES_BACKEND_USER}:${POSTGRES_BACKEND_PASSWORD}@postgresql-backend:5432/${POSTGRES_BACKEND_DB}"

npx prisma generate
npx prisma db push --accept-data-loss
exec npm run start:prod
