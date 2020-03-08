drop table if exists alert_table;
drop table if exists notification_threshold;
drop table if exists notification_type;
drop table if exists binary_relations_profile_table;
drop table if exists null_profile_table;
drop table if exists profile_table;
drop table if exists column_table;
drop table if exists monitored_tables;

create table if not exists monitored_tables ( \
    table_id integer not null auto_increment, \
    table_name varchar(100) not null, \
    database_name varchar(32) not null, \
    database_host varchar(100) not null, \
    created_date datetime not null default current_timestamp, \
    is_activated boolean not null default 1, \
    primary key(table_id));

create table if not exists column_table ( \
    column_id integer not null auto_increment, \
    column_name varchar(32) not null, \
    table_id integer not null, \
    primary key (column_id), \
    foreign key (table_id) references monitored_tables(table_id));

create table if not exists profile_table ( \
    profile_id integer not null auto_increment, \
    table_id integer not null, \
    num_rows integer not null, \
    created_date datetime not null, \
    expiry_date datetime not null, \
    primary key (profile_id), \
    foreign key (table_id) references monitored_tables(table_id));

create table if not exists null_profile_table ( \
    id integer not null auto_increment, \
    profile_id integer not null, \
    table_id integer not null, \
    column_id integer not null, \
    num_null_rows integer not null, \
    primary key (id), \
    foreign key (profile_id) references profile_table(profile_id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (column_id) references column_table(column_id));

create table if not exists binary_relations_profile_table ( \
    id integer not null auto_increment, \
    profile_id integer not null, \
    table_id integer not null, \
    column_id_a integer not null, \
    column_id_b integer not null, \
    a_content varchar(100) not null, \
    b_content varchar(100) not null, \
    count integer not null, \
    primary key (id), \
    foreign key (profile_id) references profile_table(profile_id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (column_id_a) references column_table(column_id), \
    foreign key (column_id_b) references column_table(column_id));

create table if not exists notification_type ( \
    notification_id integer not null, \
    notification_type_description varchar(32) not null, \
    primary key(notification_id));

create table if not exists notification_threshold ( \
    id integer not null auto_increment, \
    table_id integer not null, \
    notification_id integer not null, \
    column_id integer not null, \
    useful_count integer not null default 0, \
    not_useful_count integer not null default 0, \
    confidence_interval decimal not null default 95.0, \
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (column_id) references column_table(column_id), \
    foreign key (notification_id) references notification_type(notification_id));

create table if not exists alert_table ( \
    id integer not null auto_increment, \
    table_id integer not null, \
    notification_id integer not null, \
    start_date datetime not null, \
    end_date datetime, \
    column_id_a integer not null, \
    column_id_b integer, \
    is_acknowledged boolean not null, \
    acknowledged_by_user varchar(32), \
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (notification_id) references notification_type(notification_id));

-- Populate notification_type with preset anomaly types
INSERT INTO notification_type (notification_id, notification_type_description)
    VALUES
        (1, "NULL_PROPORTION_ANOMALY"),
        (2, "BINARY_RELATIONS_ANOMALY");

INSERT INTO monitored_tables(table_name, database_name, database_host, created_date, is_activated)
    VALUES ("NYC311Data", "daudit", "ec2-34-236-66-104.compute-1.amazonaws.com", current_timestamp, 1);
