#!/bin/sh
set -e

npx prisma generate
npx prisma db push --accept-data-loss
exec npm run start:prod
