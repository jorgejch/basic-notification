# Basic Notification

A lightweight and modular notification system designed for ease of use and flexibility. This project is ideal for scenarios where you need a simple way to trigger and manage notifications without additional complexity. It integrates with **Google Cloud Platform (GCP)** and uses **Pub/Sub** for event-driven execution.

## Features

- **Serverless Architecture**: Fully serverless, leveraging GCP Cloud Functions for execution.
- **Event-Driven**: Automatically triggered by Google Cloud Pub/Sub messages.
- **Lightweight**: Minimal dependencies for fast and easy integration.
- **Easy Deployment**: Simplified setup with the **Serverless Framework**.
- **Configurable**: Easily modify behavior via the `serverless.yml` configuration file.

## Architecture Overview

This system uses **Google Cloud Pub/Sub** and **Cloud Functions** for event-driven notification processing:

1. **Pub/Sub Topic**: Messages are published to a designated Pub/Sub topic.
2. **Cloud Function**: A Cloud Function, deployed via the Serverless Framework, listens to the topic and processes incoming messages.

## Getting Started

Follow these steps to set up and deploy the system.

### Prerequisites

1. A **Google Cloud Platform** project with billing enabled.
2. **gcloud CLI** installed and configured.
3. **Serverless Framework** installed:
   ```bash
   npm install -g serverless
   ```
4. A **Pub/Sub topic** created in your GCP project.

### Deployment with Serverless Framework

1. Clone the repository:
   ```bash
   git clone https://github.com/jorgejch/basic-notification.git
   cd basic-notification
   ```

2. Install project dependencies:
   ```bash
   npm install
   ```

3. Configure the deployment in `serverless.yml`:
   - Update the `topicName` property to match your Pub/Sub topic.
   - Set other configurations as needed (e.g., project ID and region).

4. Deploy the Cloud Function:
   ```bash
   serverless deploy
   ```

   The function will be deployed to GCP and automatically linked to the specified Pub/Sub topic.

### Pub/Sub Trigger

Once deployed, the Cloud Function is triggered whenever a message is published to the linked Pub/Sub topic. Messages are passed as event payloads for the function to process.

## Configuration in `serverless.yml`

The `serverless.yml` file is used to define the deployment setup for the Serverless Framework. Key configurations include:

- **Topic Name**: Specify the Pub/Sub topic that triggers the Cloud Function.
- **Environment Variables**: Add custom environment variables to tailor the function's behavior.
- **Runtime and Region**: Set the runtime (e.g., Python 3.10) and GCP region.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
