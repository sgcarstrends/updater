# Updater

## Description

A serverless application for updating car trends data.

## Prerequisites

- Node.js (compatible with Node 22.x)
- pnpm

## Installation

```bash
pnpm install
```

## Scripts

- `pnpm dev`: Start development server using SST (Serverless Stack) in dev stage
- `pnpm test`: Run tests using Vitest
- `pnpm test:coverage`: Run tests with coverage report
- `pnpm migrate`: Run database migrations using Drizzle Kit

## Key Dependencies

- Hono (Web framework)
- Drizzle ORM
- Neon Database Serverless
- Upstash Redis

## Development Tools

- Vitest (Testing)
- Biome (Linting)

## Database Migrations

Migrations are managed using Drizzle Kit. Run `pnpm migrate` to apply database schema changes.

## License

MIT License

## Author

Ru Chern Chong <ruchern.chong@sgcarstrends.com>
