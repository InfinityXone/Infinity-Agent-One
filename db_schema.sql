create table if not exists directives (
    id bigserial primary key,
    directive jsonb not null,
    created_at timestamp default now()
);

create table if not exists results (
    id bigserial primary key,
    result jsonb not null,
    created_at timestamp default now()
);
