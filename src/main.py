import argparse
import logging
import sys

from src.automation import run_rpa_challenge


def main():
    parser = argparse.ArgumentParser(description="Run the RPA Challenge automation.")
    parser.add_argument("--file", type=str, default="data/input_data.xlsx")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--perf", action="store_true", help="Minimize overhead/logging")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    if args.perf:
        logging.getLogger().setLevel(logging.WARNING)

    run_rpa_challenge(file_path=args.file, headless=args.headless, perf_mode=args.perf)


if __name__ == "__main__":
    main()
