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

    # Cleaner console: just the message for INFO/WARNING; full format for DEBUG+
    fmt = (
        "%(message)s"
        if args.log_level in {"INFO", "WARNING"}
        else "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Run; automation logs a single summary line at the end
    run_rpa_challenge(file_path=args.file, headless=args.headless, perf_mode=args.perf)



if __name__ == "__main__":
    main()
