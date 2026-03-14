-- Run this entire script in Supabase SQL Editor
-- Go to: supabase.com → your project → SQL Editor → New Query → paste this → Run

-- USERS TABLE
create table if not exists users (
    id bigint primary key generated always as identity,
    name text not null,
    email text unique not null,
    password_hash text not null,
    created_at timestamptz default now()
);

-- CATEGORIES TABLE
create table if not exists categories (
    id bigint primary key generated always as identity,
    user_id bigint references users(id) on delete cascade,
    name text not null,
    type text not null check (type in ('income', 'expense')),
    is_default boolean default false
);

-- TRANSACTIONS TABLE
create table if not exists transactions (
    id bigint primary key generated always as identity,
    user_id bigint references users(id) on delete cascade,
    category_id bigint references categories(id) on delete restrict,
    amount float not null check (amount > 0),
    description text not null,
    date date not null,
    payment_method text not null check (payment_method in ('cash', 'card')),
    created_at timestamptz default now()
);

-- BUDGETS TABLE
create table if not exists budgets (
    id bigint primary key generated always as identity,
    user_id bigint references users(id) on delete cascade,
    category_id bigint references categories(id) on delete cascade,
    amount_limit float not null check (amount_limit > 0),
    period text not null check (period in ('monthly', 'weekly')),
    unique (user_id, category_id, period)
);

-- DEFAULT CATEGORIES (shared, no user_id)
insert into categories (name, type, is_default) values
    ('Salary', 'income', true),
    ('Freelance', 'income', true),
    ('Other Income', 'income', true),
    ('Groceries', 'expense', true),
    ('Rent', 'expense', true),
    ('Transport', 'expense', true),
    ('Eating Out', 'expense', true),
    ('Entertainment', 'expense', true),
    ('Health', 'expense', true),
    ('Clothing', 'expense', true),
    ('Subscriptions', 'expense', true),
    ('Other Expense', 'expense', true)
on conflict do nothing;
