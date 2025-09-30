import logging
import os

from typing import List

from config.config import get_config


logger = logging.getLogger(__name__)


def log_core_version() -> None:
    """Log the installed FloTorch-core version if available. Never raises."""
    try:
        try:
            # Python 3.8+
            from importlib.metadata import version, PackageNotFoundError  # type: ignore
        except Exception:  # pragma: no cover
            from importlib_metadata import version, PackageNotFoundError  # type: ignore

        dist_names = ["FloTorch-core", "flotorch-core", "flotorch_core"]
        for name in dist_names:
            try:
                v = version(name)
                logger.info(f"FloTorch-core detected ({name}) version: {v}")
                return
            except PackageNotFoundError:
                continue
        logger.warning("FloTorch-core package not detected. Some features may rely on it.")
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Unable to determine FloTorch-core version: {exc}")


def validate_base_config() -> List[str]:
    """
    Perform lightweight configuration validation. Returns a list of warnings.
    This must never raise to avoid behavior changes in existing environments.
    """
    warnings: List[str] = []
    try:
        cfg = get_config()

        if not (cfg.aws_region and isinstance(cfg.aws_region, str)):
            warnings.append("aws_region is not set (config.aws_region).")

        if not (cfg.s3_bucket and isinstance(cfg.s3_bucket, str)):
            warnings.append("s3_bucket is not set (config.s3_bucket).")

        # OpenSearch basic presence check (endpoint env is used in util.open_search_config_utils)
        if not os.getenv("OPENSEARCH_ENDPOINT") and not cfg.opensearch_host:
            warnings.append("OpenSearch endpoint is not configured (OPENSEARCH_ENDPOINT/opensearch_host).")

        # Planned service adapters
        for key in ("INDEXER_URL", "RETRIEVER_URL", "EVAL_URL"):
            if not os.getenv(key):
                warnings.append(f"Optional external service URL not set: {key} (ok to ignore if unused).")

        # Database selection
        db_type = os.getenv("DB_TYPE")
        if not db_type:
            warnings.append("DB_TYPE is not set; default routing may not be explicit.")

    except Exception as exc:  # pragma: no cover
        warnings.append(f"Validation encountered an error: {exc}")

    return warnings


def log_validation_warnings(warnings: List[str]) -> None:
    if not warnings:
        logger.info("Configuration validation passed with no warnings.")
        return
    logger.warning("Configuration validation warnings:")
    for msg in warnings:
        logger.warning(f" - {msg}")



