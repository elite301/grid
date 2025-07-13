# GridBeyond Energy Management System

A comprehensive energy management platform for handling grid data, regions, nodes, and time series measurements with evolution support.

## Features

- **Grid Management**: Store and manage TSO/ISO (Transmission System Operators/Independent System Operators)
- **Regional Organization**: Hierarchical structure with Grid → Regions → Nodes
- **Time Series Evolution**: Support for evolving measurements where values change over time for the same timestamp
- **RESTful API**: Complete API for querying and managing energy data
- **PostgreSQL Database**: Robust database design with proper indexing for performance
- **Admin Interface**: Django admin for easy data management

## Database Design

### Core Models

1. **Grid**: Represents TSO/ISOs (Grid1, Grid2, Grid3)
2. **GridRegion**: Has many-to-one relationship with Grid (Region1, Region2, Region3 for each Grid)
3. **GridNode**: Has many-to-one relationship with GridRegion (Node1, Node2, Node3 for each Region)
4. **Measures**: Stores hourly time series values with evolution support

### Time Series Evolution

The `Measures` table supports the evolution of time series data. For example:
- At 9 AM, a Grid Node can have a value of 100 kW for timestamp 11 PM of the following day
- At 10 AM, the same Grid Node can have a value of 99 kW for the same datetime 11 PM of the following day

This evolution is captured through the `collected_at` field, which tracks when each measurement was collected/updated.

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Grid
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL**
   - Create a database named `gridbeyond_db`
   - Update database credentials in `gridbeyond/settings.py` if needed

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Seed sample data**
   ```bash
   python manage.py seed_data --weeks 1
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Base URL: `http://localhost:8000/api/v1/`

### Core CRUD Endpoints

- `GET/POST/PUT/DELETE /grids/` - Grid management
- `GET/POST/PUT/DELETE /regions/` - Grid Region management
- `GET/POST/PUT/DELETE /nodes/` - Grid Node management
- `GET/POST/PUT/DELETE /measures/` - Measures management

### Time Series Query Endpoints

#### 1. Latest Values API
```
GET /measures/query/?start_datetime=2024-01-01T00:00:00Z&end_datetime=2024-01-02T00:00:00Z
```

Returns the latest value for each timestamp in the date range.

**Parameters:**
- `start_datetime` (required): Start of date range (ISO format)
- `end_datetime` (required): End of date range (ISO format)
- `node_id` (optional): Filter by specific node
- `grid_id` (optional): Filter by specific grid
- `region_id` (optional): Filter by specific region

#### 2. Evolution API
```
GET /measures/evolution/?start_datetime=2024-01-01T00:00:00Z&end_datetime=2024-01-02T00:00:00Z&collected_datetime=2024-01-01T09:00:00Z
```

Returns the value corresponding to the collected_datetime for each timestamp in the date range.

**Parameters:**
- `start_datetime` (required): Start of date range (ISO format)
- `end_datetime` (required): End of date range (ISO format)
- `collected_datetime` (required): Specific collection time
- `node_id` (optional): Filter by specific node
- `grid_id` (optional): Filter by specific grid
- `region_id` (optional): Filter by specific region

### Dashboard API
```
GET /dashboard/
```

Returns system statistics and overview information.

## Example API Usage

### Get latest values for a specific time range
```bash
curl "http://localhost:8000/api/v1/measures/query/?start_datetime=2024-01-01T00:00:00Z&end_datetime=2024-01-01T23:00:00Z"
```

### Get evolution data for a specific collection time
```bash
curl "http://localhost:8000/api/v1/measures/evolution/?start_datetime=2024-01-01T00:00:00Z&end_datetime=2024-01-01T23:00:00Z&collected_datetime=2024-01-01T09:00:00Z"
```

### Get all grids
```bash
curl "http://localhost:8000/api/v1/grids/"
```

## Data Model Benefits

### Time Series Evolution Benefits

1. **Forecasting Support**: Allows storing predicted values that evolve as we get closer to the actual time
2. **Historical Accuracy**: Tracks how predictions changed over time
3. **Quality Assessment**: Different quality levels based on prediction accuracy
4. **Real-time Updates**: Supports real-time measurement updates

### Scalability Considerations

When the table grows from 1 week to 1 year of data:

1. **Indexing Strategy**: Composite indexes on (node, timestamp, collected_at) for efficient querying
2. **Partitioning**: Can partition by date ranges for better performance
3. **Archiving**: Older data can be archived to separate tables
4. **Caching**: Implement Redis caching for frequently accessed data
5. **Database Optimization**: Regular VACUUM and ANALYZE operations

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to:
- View and manage Grids, Regions, Nodes, and Measures
- Browse time series data with filtering and search
- Monitor data quality and evolution patterns

## Data Seeding

The system includes a comprehensive data seeding script that generates:

- 3 Grids (Grid1, Grid2, Grid3)
- 3 Regions per Grid (Region1, Region2, Region3)
- 3 Nodes per Region (Node1, Node2, Node3)
- 1 week of hourly time series data with evolution

Run with custom parameters:
```bash
python manage.py seed_data --weeks 4  # Generate 4 weeks of data
```

## Performance Considerations

### Database Indexes
- Composite index on (node, timestamp, collected_at)
- Index on (timestamp, collected_at)
- Index on (node, timestamp)

### Query Optimization
- Uses `select_related()` for efficient joins
- Implements proper filtering and ordering
- Supports pagination for large datasets

### Future Enhancements
- Redis caching for frequently accessed data
- Database partitioning by date ranges
- Background tasks for data processing
- Real-time WebSocket updates

## Technology Stack

- **Backend**: Django 5.2.4
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 12+
- **Python**: 3.8+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is part of the GridBeyond coding challenge. 