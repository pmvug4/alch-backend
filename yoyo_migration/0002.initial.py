"""
Add old DBMATE form migration
"""

from yoyo import step

__depends__ = {'0000.extension'}

steps = [
    step("""
create table users
(
    id              serial
        constraint users_pk
            primary key,
    username        varchar not null,
    password_hash varchar,
    refresh_token varchar,
    group_id int not null
);
create unique index users_id_uindex
    on users (id);
create unique index users_username_uindex
    on users (username);
create table groups
(
    id  int
        constraint groups_pk
            primary key,
    name        varchar not null
);
create unique index groups_id_uindex
    on groups (id);
alter table users
    add constraint users_groups_id_fk
        foreign key (group_id) references groups;
create table otp_passwords
(
    id           serial
        constraint otp_password_pk
            primary key,
    username     varchar(50) not null,
    user_id      int
        constraint otp_password_users_id_fk
            references users
            on delete cascade,
    otp_password varchar(100),
    check_count  int         not null,
    valid_until  TIMESTAMP,
    invalid int default 0,
    created_at   TIMESTAMP default NOW()
);
create unique index otp_password_id_uindex
    on otp_passwords (id);
create index otp_password_username_index
    on otp_passwords (username);
INSERT INTO groups (id, name) VALUES (1::integer, 'customer'::varchar)
""",
         """
DROP TABLE otp_passwords;
DROP TABLE groups;
DROP TABLE users;
"""),  # rollback command
]