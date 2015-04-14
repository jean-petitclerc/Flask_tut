--drop table if exists tuser;
--create table tuser (
--    user_name text primary key,
--    user_pass text not null
--);
create table tphoto (
    id integer primary key autoincrement,
    photo_name text not null,
    location text not null,
    photo_date date not null
);
create index photo_x1 on tphoto(photo_date, photo_name);
