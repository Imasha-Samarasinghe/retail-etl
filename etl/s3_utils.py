import gzip
import logging
import shutil
import tempfile
from pathlib import Path

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

from config.settings import S3_BUCKET

log = logging.getLogger(__name__)

_client_cfg = Config(retries={"max_attempts": 10, "mode": "standard"},
                     connect_timeout=30, read_timeout=120)
_transfer_cfg = TransferConfig(multipart_threshold=16 * 1024 * 1024,
                               multipart_chunksize=8 * 1024 * 1024,
                               max_concurrency=2)


def upload(local_path, prefix: str, run_id: int, compress: bool = False) -> str:
    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not set in .env")
    path = Path(local_path)
    tmp = None
    if compress:
        tmp = Path(tempfile.gettempdir()) / (path.name + ".gz")
        with open(path, "rb") as src, gzip.open(tmp, "wb") as dst:
            shutil.copyfileobj(src, dst)
        path = tmp
    key = f"{prefix}/run_id={run_id}/{path.name}"
    try:
        # credentials come from env vars loaded from .env by settings.py
        boto3.client("s3", config=_client_cfg).upload_file(
            str(path), S3_BUCKET, key, Config=_transfer_cfg)
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)
    log.info("S3 upload: %s -> s3://%s/%s", local_path, S3_BUCKET, key)
    return key
