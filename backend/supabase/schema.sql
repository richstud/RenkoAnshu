-- Supabase schema for Renko Reversal Gold Bot

create table if not exists accounts (
  id serial primary key,
  login bigint unique not null,
  server text not null,
  status text,
  created_at timestamptz default now()
);

create table if not exists trades (
  id serial primary key,
  account_id bigint references accounts(login) on delete cascade,
  symbol text not null,
  type text not null,
  lot numeric,
  entry_price numeric,
  exit_price numeric,
  profit numeric,
  timestamp timestamptz default now()
);

create table if not exists logs (
  id serial primary key,
  account_id bigint references accounts(login) on delete cascade,
  event text not null,
  latency numeric,
  created_at timestamptz default now()
);

create table if not exists settings (
  id int primary key,
  brick_size numeric,
  bot_status text,
  updated_at timestamptz default now()
);
