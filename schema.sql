drop table if exists monitored_tables;
drop table if exists column_null_profiles;
drop table if exists notification_type;
drop table if exists notification_threshold;
drop table if exists alert_table;

create table if not exists monitored_tables ( \
    table_id integer not null, \
    table_name varchar(32) not null, \
    database_name varchar(32) not null, \
    created_date datetime not null, \
    is_activated boolean not null, \
    primary key(table_id));

create table if not exists column_null_profiles ( \
    column_id integer not null, \
    column_name varchar(100) not null, \
    table_id integer not null, \
    num_rows integer not null, \
    expected_nulls_per_num_rows integer not null, \
    primary key (column_id), \
    foreign key (table_id) references monitored_tables(table_id));

create table if not exists notification_type ( \
    notification_id integer not null, \
    notification_type_description varchar(500) not null, \
    primary key(notification_id));

create table if not exists notification_threshold ( \
    id integer not null, \
    table_id integer not null, \
    notification_id integer not null, \
    useful_count integer not null, \
    not_useful_count integer not null, \
    null_proportion_threshold integer not null,
    primary key (id), \
    foreign key (table_id) references monitored_tables(table_id), \
    foreign key (notification_id) references notification_type(notification_id));

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
    foreign key (notification_id) references notification_type(notification_id));

-- Populate tables for NYC data table
insert into monitored_tables (table_id, table_name, database_name, is_activated)
    values (1, 'NYC311Data', 'daudit', TRUE);

insert into column_null_profiles (column_id, column_name, table_id, num_rows, expected_nulls_per_num_rows)
    values
        (1, 'AddressType', 1, 5000-, 1120),
        (2, 'Agency', 1, 50000, 0),
        (3, 'AgencyName', 1, 50000, 0),
        (4, 'BBL', 1, 50000, 10529),
        (5, 'Borough', 1, 50000, 0),
        (6, 'BridgeHighwayDirection', 1, 50000, 49923),
        (7, 'BridgeHighwayName', 1, 50000, 49923),
        (8, 'BridgeHighwaySegment', 1, 50000, 49895),
        (9, 'City', 1, 50000, 1260),
        (10, 'ClosedDate', 1, 50000, 6222),
        (11, 'CommunityBoard', 1, 50000, 0),
        (12, 'ComplaintType', 1, 50000, 0),
        (13, 'CrossStreet1', 1, 50000, 15450),
        (14, 'CrossStreet2', 1, 50000, 15581),
        (15, 'Descriptor', 1, 50000, 406),
        (16, 'DueDate', 1, 50000, 21624),
        (17, 'FacilityType', 1, 50000, 28),
        (18, 'id', , 1, 50000, 0),
        (19, 'IncidentAddress', 1, 50000, 7860),
        (20, 'IncidentZip', 1, 50000, 1273),
        (21, 'IntersectionStreet1', 1, 50000, 43620),
        (22, 'IntersectionStreet2', 1, 50000, 43662),
        (23, 'Landmark', 1, 50000, 49969),
        (24, 'Latitude', 1, 50000, 2590),
        (25, 'Location', 1, 50000, 2590),
        (26, 'LocationType', 1, 50000, 9505),
        (27, 'Longitude', 1, 50000, 2590),
        (28, 'OpenDataChannelType', 1, 50000, 0),
        (30, 'ParkBorough', 1, 50000, 0),
        (31, 'ParkFacilityName', 1, 50000, 0),
        (32, 'ResolutionActionUpdatedDate', 1, 50000, 3587),
        (33, 'ResolutionDescription', 1, 50000, 5452),
        (34, 'RoadRamp', 1, 50000, 49923),
        (35, 'Status', 1, 50000, 0),
        (36, 'StreetName', 1, 50000, 7861),
        (37, 'TaxiCompanyBorough', 1, 50000, 49954),
        (38, 'TaxiPickUpLocation', 1, 50000, 49815),
        (39, 'VehicleType', 1, 50000, 49999),
        (40, 'XCoordinate', 1, 50000, 2590),
        (41, 'YCoordinate', 1, 50000, 2590);
