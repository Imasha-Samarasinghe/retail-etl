import argparse
import logging
import time

from config.settings import CLEAN_DIR, REJECT_DIR, BASE
from etl.extract import extract
from etl.transform import standardize
from etl.validate import validate
from etl.load import load, start_run, finish_run

log = logging.getLogger("pipeline")


def setup_logging():
    (BASE / "logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(
            BASE / "logs" / "pipeline.log")],
    )


def main():
    ap = argparse.ArgumentParser(description="Online Retail II ETL pipeline")
    ap.add_argument("--sample", type=int, default=None,
                    help="only process the first N rows")
    args = ap.parse_args()
    setup_logging()

    run_id = start_run()
    n_read = n_rej = n_loaded = 0
    t0 = time.time()
    try:
        raw = extract(args.sample)
        n_read = len(raw)
        log.info("EXTRACT  rows read: %s (%.1fs)", n_read, time.time() - t0)

        df = standardize(raw)
        log.info("TRANSFORM standardized (%.1fs)", time.time() - t0)

        clean, rejects = validate(df)
        n_rej = len(rejects)
        log.info("VALIDATE clean: %s | rejected: %s", len(clean), n_rej)
        for reason, cnt in rejects["reject_reason"].value_counts().items():
            log.info("   reject reason %-20s %s", reason, cnt)

        REJECT_DIR.mkdir(parents=True, exist_ok=True)
        CLEAN_DIR.mkdir(parents=True, exist_ok=True)
        rejects.to_csv(REJECT_DIR / "rejects.csv", index=False)
        clean.to_parquet(CLEAN_DIR / "clean.parquet", index=False)

        n_loaded = load(clean)
        finish_run(run_id, n_read, n_rej, n_loaded, "success")
        log.info("DONE run %s | read %s = clean %s + rejected %s | loaded %s | %.1fs",
                 run_id, n_read, len(clean), n_rej, n_loaded, time.time() - t0)
    except Exception:
        log.exception("Pipeline failed")
        finish_run(run_id, n_read, n_rej, n_loaded, "failed")
        raise


if __name__ == "__main__":
    main()
