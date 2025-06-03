import httpx
import logging
import os
import asyncio
from typing import List, Dict, Optional, Tuple
from app.config import settings
from app.services.mongodb_service import mongodb_service
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchCaptionRequest:
    """Data class for batch caption request information."""
    image_id: str
    image_path: str
    original_filename: str


class BatchCaptionService:
    """
    Enhanced service for batch and asynchronous image captioning using BLIP service.

    This service leverages the batch processing capabilities of the BLIP Captioner
    to process multiple images efficiently, reducing API calls and improving performance.
    """

    def __init__(self):
        self.batch_endpoint = "/batch-caption"
        self.async_batch_endpoint = "/async-batch-caption"
        self.async_status_endpoint = "/async-batch-caption/status"
        self.base_url = settings.BLIP_BASE_URL

    async def process_batch_sync(self, batch_requests: List[BatchCaptionRequest]) -> Dict[str, Dict]:
        """
        Process a batch of images synchronously using the BLIP batch endpoint.

        Args:
            batch_requests: List of BatchCaptionRequest objects

        Returns:
            Dict mapping image_id to result data (caption, tags, error)
        """
        if not batch_requests:
            return {}

        logger.info(
            f"Processing batch of {len(batch_requests)} images synchronously")

        # Prepare files for the batch request
        files_to_send = []
        id_to_filename_map = {}

        for req in batch_requests:
            if not os.path.exists(req.image_path):
                logger.error(
                    f"Image file not found: {req.image_path} for image_id: {req.image_id}")
                continue

            try:
                # Open file and prepare for multipart upload
                file_content = open(req.image_path, "rb")
                files_to_send.append(
                    ("images", (req.original_filename, file_content, "image/jpeg"))
                )
                id_to_filename_map[req.original_filename] = req.image_id
            except Exception as e:
                logger.error(f"Failed to prepare file {req.image_path}: {e}")
                continue

        if not files_to_send:
            logger.warning("No valid files to process in batch")
            return {}

        results = {}

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                full_url = f"{self.base_url}{self.batch_endpoint}"
                logger.info(
                    f"Sending batch request to {full_url} with {len(files_to_send)} files")

                response = await client.post(full_url, files=files_to_send)
                response.raise_for_status()

                data = response.json()
                batch_results = data.get("results", [])

                # Map results back to image IDs
                for result in batch_results:
                    image_path = result.get("image_path")
                    if image_path in id_to_filename_map:
                        image_id = id_to_filename_map[image_path]
                        if result.get("error"):
                            results[image_id] = {"error": result["error"]}
                        else:
                            results[image_id] = {
                                "caption": result.get("caption"),
                                "tags": result.get("tags", [])
                            }

                logger.info(
                    f"Batch processing completed. Processed {len(results)} images successfully")

        except httpx.RequestError as e:
            logger.error(f"HTTP request failed for batch processing: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during batch processing: {e}")
        finally:
            # Close all opened files
            for _, (_, file_obj, _) in files_to_send:
                try:
                    file_obj.close()
                except:
                    pass

        return results

    async def process_batch_async(self, batch_requests: List[BatchCaptionRequest]) -> Optional[str]:
        """
        Process a batch of images asynchronously using the BLIP async batch endpoint.

        Args:
            batch_requests: List of BatchCaptionRequest objects

        Returns:
            Task ID for polling status, or None if failed
        """
        if not batch_requests:
            return None

        logger.info(
            f"Starting async processing of {len(batch_requests)} images")

        # Prepare files for the async batch request
        files_to_send = []
        id_to_filename_map = {}

        for req in batch_requests:
            if not os.path.exists(req.image_path):
                logger.error(
                    f"Image file not found: {req.image_path} for image_id: {req.image_id}")
                continue

            try:
                file_content = open(req.image_path, "rb")
                files_to_send.append(
                    ("images", (req.original_filename, file_content, "image/jpeg"))
                )
                id_to_filename_map[req.original_filename] = req.image_id
            except Exception as e:
                logger.error(f"Failed to prepare file {req.image_path}: {e}")
                continue

        if not files_to_send:
            logger.warning("No valid files to process in async batch")
            return None

        task_id = None

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                full_url = f"{self.base_url}{self.async_batch_endpoint}"
                logger.info(
                    f"Sending async batch request to {full_url} with {len(files_to_send)} files")

                response = await client.post(full_url, files=files_to_send)
                response.raise_for_status()

                data = response.json()
                task_id = data.get("task_id")

                if task_id:
                    logger.info(f"Async batch task started with ID: {task_id}")
                    # Store the mapping for later result processing
                    await self._store_task_mapping(task_id, id_to_filename_map)
                else:
                    logger.error(
                        "No task_id received from async batch request")

        except httpx.RequestError as e:
            logger.error(
                f"HTTP request failed for async batch processing: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error during async batch processing: {e}")
        finally:
            # Close all opened files
            for _, (_, file_obj, _) in files_to_send:
                try:
                    file_obj.close()
                except:
                    pass

        return task_id

    async def check_async_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Check the status of an async batch task and process results if completed.

        Args:
            task_id: The task ID returned by process_batch_async

        Returns:
            Task status information
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                full_url = f"{self.base_url}{self.async_status_endpoint}/{task_id}"
                response = await client.get(full_url)
                response.raise_for_status()

                task_status = response.json()
                status = task_status.get("status")

                logger.info(f"Task {task_id} status: {status}")

                # If task is completed, process the results
                if status == "COMPLETED":
                    await self._process_async_results(task_id, task_status)

                return task_status

        except httpx.RequestError as e:
            logger.error(f"Failed to check task status for {task_id}: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error checking task status for {task_id}: {e}")

        return None

    async def _store_task_mapping(self, task_id: str, id_to_filename_map: Dict[str, str]):
        """Store the task ID to image ID mapping for later result processing."""
        # In a production environment, you might want to store this in Redis or database
        # For now, we'll store it in a simple file or memory structure
        # This is a simplified implementation
        mapping_data = {
            "task_id": task_id,
            "mapping": id_to_filename_map,
            "created_at": str(asyncio.get_event_loop().time())
        }
        # You could implement persistence here if needed
        logger.info(
            f"Stored mapping for task {task_id} with {len(id_to_filename_map)} entries")

    async def _process_async_results(self, task_id: str, task_status: Dict):
        """Process the results from a completed async task."""
        results = task_status.get("result", [])
        if not results:
            logger.warning(f"No results found for completed task {task_id}")
            return

        logger.info(f"Processing {len(results)} results from task {task_id}")

        updates_count = 0
        errors_count = 0

        for result in results:
            image_path = result.get("image_path")
            if result.get("error"):
                logger.error(
                    f"Error in async result for {image_path}: {result['error']}")
                errors_count += 1
                continue

            caption = result.get("caption")
            tags = result.get("tags", [])

            if caption:
                # In a production system, you would use the stored filename-to-ID mapping
                # For now, we'll try to find the image by matching the original filename
                try:
                    # This is a simplified approach - in production you'd use proper ID mapping
                    # stored when the async task was created
                    query = {"original_name": image_path}
                    image_doc = mongodb_service.uploads_collection.find_one(
                        query)

                    if image_doc:
                        image_id = image_doc["id"]
                        update_data = {
                            "caption": caption,
                            "tags": tags,
                            "status": "processed"
                        }
                        success = mongodb_service.update_upload_metadata(
                            image_id, update_data)
                        if success:
                            logger.info(
                                f"Updated image {image_id} ({image_path}) with caption: {caption[:50]}...")
                            updates_count += 1
                        else:
                            logger.error(
                                f"Failed to update database for {image_path}")
                            errors_count += 1
                    else:
                        logger.warning(
                            f"Could not find image in database with filename: {image_path}")
                        errors_count += 1

                except Exception as e:
                    logger.error(
                        f"Failed to update database for {image_path}: {e}")
                    errors_count += 1

        logger.info(
            f"Async task {task_id} processing complete: {updates_count} successful, {errors_count} errors")


# Global instance
batch_caption_service = BatchCaptionService()


async def process_images_in_batches(
    image_requests: List[BatchCaptionRequest],
    batch_size: int = 5,
    use_async: bool = True
) -> Dict[str, Dict]:
    """
    Process multiple images in batches using either sync or async batch processing.

    Args:
        image_requests: List of images to process
        batch_size: Number of images per batch
        use_async: Whether to use async processing (recommended for large batches)

    Returns:
        Dict mapping image_id to results
    """
    if not image_requests:
        return {}

    logger.info(
        f"Processing {len(image_requests)} images in batches of {batch_size}, async={use_async}")

    all_results = {}

    # Split into batches
    for i in range(0, len(image_requests), batch_size):
        batch = image_requests[i:i + batch_size]
        logger.info(
            f"Processing batch {i//batch_size + 1} with {len(batch)} images")

        if use_async:
            # For async processing, we just start the task
            task_id = await batch_caption_service.process_batch_async(batch)
            if task_id:
                logger.info(
                    f"Started async task {task_id} for batch {i//batch_size + 1}")
                # In a real implementation, you might want to store task_id for later polling
        else:
            # For sync processing, we get immediate results
            batch_results = await batch_caption_service.process_batch_sync(batch)
            all_results.update(batch_results)

            # Update database immediately for sync results
            for image_id, result in batch_results.items():
                if "error" not in result:
                    try:
                        update_data = {
                            "caption": result["caption"],
                            "tags": result["tags"],
                            "status": "processed"
                        }
                        mongodb_service.update_upload_metadata(
                            image_id, update_data)
                        logger.info(
                            f"Updated database for image_id: {image_id}")
                    except Exception as e:
                        logger.error(
                            f"Failed to update database for image_id {image_id}: {e}")
                else:
                    # Mark as failed
                    try:
                        mongodb_service.update_upload_metadata(
                            image_id, {"status": "caption_failed",
                                       "error": result["error"]}
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to update error status for image_id {image_id}: {e}")

        # Add a small delay between batches to avoid overwhelming the service
        if i + batch_size < len(image_requests):
            await asyncio.sleep(1)

    return all_results


async def queue_batch_caption_background_task(image_ids_and_paths: List[Tuple[str, str, str]]):
    """
    Background task to process multiple images using batch captioning.

    Args:
        image_ids_and_paths: List of tuples (image_id, image_path, original_filename)
    """
    if not image_ids_and_paths:
        return

    logger.info(
        f"Starting batch caption background task for {len(image_ids_and_paths)} images")

    # Convert to BatchCaptionRequest objects
    batch_requests = [
        BatchCaptionRequest(
            image_id=image_id,
            image_path=image_path,
            original_filename=filename
        )
        for image_id, image_path, filename in image_ids_and_paths
    ]

    # Process in batches
    # Use sync processing for smaller batches, async for larger ones
    use_async = len(batch_requests) > 10

    try:
        results = await process_images_in_batches(
            batch_requests,
            batch_size=5,
            use_async=use_async
        )

        logger.info(
            f"Batch caption background task completed. Processed {len(results)} images")

    except Exception as e:
        logger.error(f"Error in batch caption background task: {e}")
        # Mark all images as failed
        for image_id, _, _ in image_ids_and_paths:
            try:
                mongodb_service.update_upload_metadata(
                    image_id, {
                        "status": "caption_failed_batch_error", "error": str(e)}
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update error status for image_id {image_id}: {update_error}")
