# Monitoring System

A robust monitoring system designed to collect, process, and report various metrics from system resources and external services. The system features a modular architecture with support for different types of monitors and flexible metric queuing mechanisms.

## Features

### Monitors
- **System Monitors**
  - CPU Usage Monitor
  - Memory Usage Monitor
  - Process Count Monitor
- **Cryptocurrency Monitors**
  - Bitcoin Price Monitor
- **Queuing System**
  - Simple Queue Implementation
  - Priority Queue for Critical Metrics

## Architecture

The system is built with a modular architecture consisting of:
1. **Monitor Components**: Individual monitors that collect specific metrics
2. **Queue System**: Handles metric processing and delivery
3. **Logging System**: Comprehensive logging of metrics and system status

## Testing

The project includes both unit tests and integration tests:

### Unit Tests
Tests individual components in isolation using mocks:
- Monitor initialization
- Metric collection
- Error handling

To run unit tests:
```bash
python -m unittest discover -s src/tests/unit -p "test_*.py" -v
```

### Integration Tests
Tests component interactions and actual functionality:
- Queue operations
- Metric processing
- System integration

To run integration tests:
```bash
python -m unittest discover -s src/tests/integration -p "test_*.py" -v
```

## Project Structure
```
project_root/
├── src/                        # Source code
│   ├── client/                # Client implementations
│   │   ├── simple_queue.py    # Basic queue implementation
│   │   ├── priority_queue.py  # Priority-based queue
│   │   └── async_queue.py     # Asynchronous queue
│   ├── config/                # Configuration management
│   ├── logging/               # Logging setup
│   ├── utils/                 # Utility functions
│   ├── metrics_monitoring/
│   │   ├── handlers/          # Metric handling logic
│   │   ├── models/           # Data models
│   │   └── monitors/         # Monitor implementations
│   │       ├── system/       # System resource monitors
│   │       ├── crypto/       # Cryptocurrency monitors
│   │       ├── weather/      # Weather monitors
│   │       └── space/        # Space-related monitors
│   └── tests/
│       ├── unit/            # Unit tests
│       └── integration/     # Integration tests
├── main.py                 # Application entry point
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
└── .gitignore           # Git ignore rules
```

## Configuration

The system uses two main configuration files:
- `config.json`: Main configuration for monitors and system settings
- `.env`: Environment-specific variables and secrets

## Dependencies

Key dependencies are listed in `requirements.txt`. Main dependencies include:
- psutil: For system monitoring
- requests: For API calls

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` and `config.json`
4. Run the application: `python main.py`

