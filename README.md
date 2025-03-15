# RSS Proxy Transformer

RSS Proxy Transformer is a lightweight Python web service that fetches an RSS feed from a specified URL, applies customizable regex-based transformations on selected XML fields, and serves the modified feed in UTF‑8 encoding. It is especially useful for rewriting URLs (with proper URL‑encoding) and handling feeds in non‑UTF‑8 encodings (like windows-1251).

## Features

- **Customizable Transformations:** Apply multiple regex-based rules to designated XML fields (e.g. `<link>`).
- **Encoding Conversion:** Accept feeds in various encodings (e.g. `windows-1251`) and output a UTF‑8 encoded feed.
- **URL‑Encoding Support:** For example, for the `<link>` field, replace placeholders (like `$1`) with the URL‑encoded original value.
- **Environment‑Based Configuration:** All settings, including feed URL and transformation rules, are configured via environment variables.
- **Robust Error Handling:** Logs errors and provides informative HTTP responses when issues occur.
- **Lightweight & Deployable:** Built on Flask; ideal for cloud workers, containerized apps, or simple server deployment.

## Requirements

- Python 3.7+
- [Flask](https://flask.palletsprojects.com/)
- [Requests](https://docs.python-requests.org/)

All other dependencies are part of Python’s standard library.

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/Kenya-West/rss-proxy-transformer.git
cd rss-proxy-transformer
pip install -r requirements.txt
```

*(Ensure your `requirements.txt` includes Flask and requests.)*

## Configuration

The application is fully configured via environment variables:

- **FEED_URL** (required):  
  The URL of the original RSS feed to be proxied.

- **FEED_ENCODING** (optional):  
  If the source feed is in a non‑UTF‑8 encoding (e.g. `"windows-1251"`), set this variable to ensure proper conversion.

- **TRANSFORM_RULES** (optional):  
  A JSON‑encoded array of transformation rules. Each rule must be an object with the following keys:
  - `"field"`: The XML tag (e.g. `"link"`) to transform.
  - `"regex"`: A regex pattern to match against the element's text.
  - `"replacement"`: A replacement string which may include the placeholder `$1`. For the `"link"` field, `$1` will be replaced by the URL‑encoded original text.

  **Example:**

  ```json
  [
    {
      "field": "link",
      "regex": "^(https?://.*)$",
      "replacement": "https://proxy.example.com/?url=$1"
    }
  ]
  ```

- **LOG_LEVEL** (optional):  
  Set the logging level (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`). Defaults to `INFO`.

## Running the Application

To run the service locally, simply execute:

```bash
python app.py
```

By default, the service listens on all interfaces (`0.0.0.0`) at port `5000`. You can then subscribe to the proxied feed at:

```
http://<your-server>:5000/feed
```

## Deployment

RSS Proxy Transformer can be deployed on any platform that supports Python. Some common options include:

- **Cloud Providers:** Deploy on services like Heroku, AWS, or DigitalOcean.
- **Containers:** Package the application in a Docker container.
- **Serverless Platforms:** Adapt it for use with cloud workers if desired.

Adjust the host and port settings as needed for your deployment environment.

## Docker Compose Deployment
To run the application with Docker Compose:
1. Copy the example environment file:
   ```sh
   cp .env.example .env
   ```
2. Modify the `.env` file as needed.
3. Start the service:
   ```sh
   docker-compose up -d
   ```

## Contributing

Contributions are welcome! If you have ideas for improvements or encounter any bugs, please open an issue or submit a pull request on GitHub.

### How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write tests for your changes.
4. Submit a pull request with a clear description of your changes.

## Troubleshooting

- **Feed Fetch Errors:**  
  Ensure that the `FEED_URL` is correct and that your server has network access to it.

- **Encoding Issues:**  
  If you see garbled characters, try setting the `FEED_ENCODING` environment variable to the feed’s original encoding.

- **Transformation Rules Not Working:**  
  Double-check the JSON structure and regex patterns in your `TRANSFORM_RULES`. Use a tool like [regex101](https://regex101.com/) for testing.

- **Logging:**  
  Increase the `LOG_LEVEL` (e.g., set `LOG_LEVEL=DEBUG`) to see detailed logs for troubleshooting.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the maintainers of Flask and Requests for making it easy to build and deploy lightweight web services.
- Special thanks to the open-source community for their continuous support and contributions.

## Contact

For questions or feedback, please open an issue on [GitHub](https://github.com/Kenya-West/rss-proxy-transformer/issues) or contact the maintainer at [your.email@example.com](mailto:your.email@example.com).