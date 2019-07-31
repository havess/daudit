create table if not exists monitored_tables ( \
    table_id integer not null auto_increment, \
    table_name varchar(100) not null, \
    database_name varchar(32) not null, \
    created_date datetime not null, \
    is_activated boolean not null, \
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
    useful_count integer not null, \
    not_useful_count integer not null, \
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
    is_acknowledged boolean not null, \
    is_acknowledged_by_user boolean not null, \
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (notification_id) references notification_type(notification_id));

-- Populate notification_type with preset anomaly types
insert into notification_type (notification_id, notification_type_description)
    values
        (1, "NULL_PROPORTION_ANOMALY"),
        (2, "BINARY_RELATIONS_ANOMALY");
