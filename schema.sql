create table if not exists monitored_tables ( \
    table_id integer not null,
    table_name varchar(32) not null, \
    database_name varchar(32) not null, \
    created_date datetime not null, \
    is_activated boolean not null, \
    primary key(table_id))

create table if not exists notification_type ( \
    notification_id integer not null, \
    notification_type_description varchar(500) not null, \
    primary key(notification_id))

create table if not exists notification_threshold ( \
    id integer not null, \
    table_id integer not null, \
    notification_id integer not null, \
    useful_count integer not null, \
    not_useful_count integer not null, \
    null_proportion_threshold integer not null,
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (notification_id) references notification_type(notification_id))

create table if not exists alert_table ( \
    id integer not null, \
    table_id integer not null, \
    notification_id integer not null, \
    start_date datetime not null, \
    end_date datetime, \
    is_acknowledged boolean not null, \
    is_acknowledged_by_user boolean not null, \
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (notification_id) references notification_type(notification_id))
