# Basic Notification

A lightweight and modular notification system designed for ease of use and flexibility. This project is ideal for scenarios where you need a simple way to trigger and manage notifications without additional complexity.

## Features

- **Lightweight**: Minimal dependencies for fast and easy integration.
- **Modular**: Extend and customize to fit your needs.
- **Cross-Platform**: Works on any environment that supports Python.

## Getting Started

Follow these steps to set up and use the Basic Notification system.

### Prerequisites

- Python 3.7 or higher installed.
- `pip` package manager available.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jorgejch/basic-notification.git
   cd basic-notification
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Import the notification module into your project:
   ```python
   from notification import Notification
   ```

2. Create and trigger a notification:
   ```python
   notifier = Notification()
   notifier.send("This is a basic notification message!")
   ```

### Configuration

You can customize the behavior of notifications by modifying the configuration in the `config.py` file.

### Example

Below is a simple example of using the system to send multiple notifications:
```python
from notification import Notification

notifier = Notification()
messages = ["Hello, world!", "Notification 2", "Final notification"]

for message in messages:
    notifier.send(message)
```

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, feel free to open an issue in this repository or contact the maintainer.
