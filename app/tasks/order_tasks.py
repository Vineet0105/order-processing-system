
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="orders.process_notification",
    max_retries=3,
    default_retry_delay=5,
)
def process_order_notification(self, order_id: int):
    try:
        logger.info(
            "Processing order notification",
            extra={"order_id": order_id},
        )

        # Placeholder for notification logic.
        # For example, send an order-confirmation email.

        logger.info(
            "Order notification processed",
            extra={"order_id": order_id},
        )

        return {
            "order_id": order_id,
            "status": "processed",
        }

    except Exception as exc:
        logger.exception(
            "Order notification failed",
            extra={"order_id": order_id},
        )
        raise self.retry(exc=exc)
