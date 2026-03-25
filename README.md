# Wake-on-LAN (Python)

This script sends a Wake-on-LAN "magic packet" to one or more devices by MAC address.

## Supported Python versions

- Python `2.7`
- Python `3.x`

## Run

You can pass one or more MAC addresses as command-line arguments. If you omit MACs, the script falls back to the defaults in `main.py`.

```sh
python main.py AA:BB:CC:DD:EE:FF
python main.py AA:BB:CC:DD:EE:FF 11:22:33:44:55:66
python main.py AA:BB:CC:DD:EE:FF --broadcast-ip 192.168.1.255 --port 9
```

## Help

To see the full CLI documentation, run (or `-h`):

```sh
python main.py --help
```

## Notes

- The script uses `255.255.255.255` as the default broadcast IP and port `9` (common WoL port).
- Some networks/VPNs block broadcast traffic; in that case you may need to modify firewall settings or use a directed broadcast address.

## Testing

Unit tests use Python's built-in `unittest` framework and mock out the UDP socket, so they do not send real Wake-on-LAN packets.

### Run tests (no coverage)

```sh
python -m unittest discover -s tests -p "test_*.py"
```

### Run tests with coverage (optional)

If you have `coverage` installed:

```sh
python tests/run_coverage.py
```

The coverage runner uses `tests/coveragerc.ini` and is compatible with both Python `2.7` and `3.x`.

## Continuous Integration (GitHub Actions)

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs on every push to `main`/`master` and on all pull requests.

In CI it will:

- Run a syntax check on `main.py`
- Execute unit tests via `python -m unittest discover -s tests -p "test_*.py"`
- Execute coverage via `python tests/run_coverage.py` (requires the `coverage` package)

The workflow tests Python versions `3.9` through `3.12`.
