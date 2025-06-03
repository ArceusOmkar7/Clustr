#!/usr/bin/env python3
"""
Test script for batch captioning functionality in Clustr backend.

This script demonstrates how to use the new batch captioning features:
1. Upload multiple images
2. Process them using batch captioning
3. Check the results

Usage:
    python test_batch_captioning.py
"""

import asyncio
import httpx
import os
import sys
import json
from pathlib import Path

# Add the parent directory to sys.path so we can import from app
sys.path.append(str(Path(__file__).parent))

CLUSTR_BASE_URL = "http://localhost:5000"
BLIP_BASE_URL = "http://localhost:8000"


async def test_blip_service_health():
    """Test if BLIP service is available."""
    print("🔍 Checking BLIP service health...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BLIP_BASE_URL}/health", timeout=10.0)
            if response.status_code == 200:
                print("✅ BLIP service is healthy")
                return True
            else:
                print(f"❌ BLIP service returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ BLIP service is not available: {e}")
        return False


async def test_clustr_service_health():
    """Test if Clustr backend is available."""
    print("🔍 Checking Clustr backend health...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CLUSTR_BASE_URL}/", timeout=10.0)
            if response.status_code == 200:
                print("✅ Clustr backend is healthy")
                return True
            else:
                print(
                    f"❌ Clustr backend returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Clustr backend is not available: {e}")
        return False


async def test_blip_service_integration():
    """Test Clustr's integration with BLIP service."""
    print("🔍 Testing BLIP service integration...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CLUSTR_BASE_URL}/api/ml/service-health", timeout=10.0)
            data = response.json()

            if data.get("blip_service_available"):
                print("✅ BLIP service integration is working")
                print(f"   BLIP URL: {data.get('blip_service_url')}")
                return True
            else:
                print("❌ BLIP service integration failed")
                print(f"   Error: {data.get('error', 'Unknown error')}")
                return False
    except Exception as e:
        print(f"❌ Failed to test BLIP integration: {e}")
        return False


async def get_caption_statistics():
    """Get current caption statistics."""
    print("📊 Getting caption statistics...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CLUSTR_BASE_URL}/api/ml/caption-stats", timeout=10.0)
            data = response.json()

            print(f"   Total images: {data.get('total_images', 0)}")
            print(f"   Captioned: {data.get('captioned', 0)}")
            print(f"   Uncaptioned: {data.get('uncaptioned', 0)}")
            print(f"   Processing: {data.get('processing', 0)}")
            print(f"   Failed: {data.get('failed', 0)}")
            print(
                f"   Caption percentage: {data.get('caption_percentage', 0)}%")

            status_breakdown = data.get('status_breakdown', {})
            if status_breakdown:
                print("   Status breakdown:")
                for status, count in status_breakdown.items():
                    print(f"     {status}: {count}")

            return data
    except Exception as e:
        print(f"❌ Failed to get caption statistics: {e}")
        return None


async def test_batch_processing():
    """Test batch processing of uncaptioned images."""
    print("🔄 Testing batch processing of uncaptioned images...")

    try:
        async with httpx.AsyncClient() as client:
            # Trigger batch processing
            response = await client.post(
                f"{CLUSTR_BASE_URL}/api/ml/batch-process-uncaptioned",
                # Use sync for testing
                params={"limit": 10, "use_async": False},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Batch processing started")
                print(f"   Processing {data.get('count', 0)} images")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(
                    f"❌ Batch processing failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Failed to start batch processing: {e}")
        return False


async def upload_test_images():
    """Upload some test images if available."""
    print("📤 Looking for test images to upload...")

    # Look for images in the uploads directory
    uploads_dir = Path(__file__).parent / "uploads"
    if not uploads_dir.exists():
        print("   No uploads directory found, skipping image upload test")
        return False

    image_files = list(uploads_dir.glob("*.jpg")) + \
        list(uploads_dir.glob("*.png"))
    if not image_files:
        print("   No image files found in uploads directory")
        return False

    # Take up to 3 images for testing
    test_images = image_files[:3]
    print(f"   Found {len(test_images)} test images")

    try:
        async with httpx.AsyncClient() as client:
            files = []
            for img_path in test_images:
                files.append(
                    ("files", (img_path.name, open(img_path, "rb"), "image/jpeg")))

            response = await client.post(
                f"{CLUSTR_BASE_URL}/api/upload",
                files=files,
                timeout=60.0
            )

            # Close all opened files
            for _, (_, file_obj, _) in files:
                file_obj.close()

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Uploaded {len(data.get('data', []))} images")
                return True
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Failed to upload test images: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Clustr Batch Captioning Tests")
    print("=" * 50)

    # Test service health
    blip_healthy = await test_blip_service_health()
    clustr_healthy = await test_clustr_service_health()

    if not (blip_healthy and clustr_healthy):
        print("\n❌ Prerequisites not met. Please ensure both services are running:")
        print("   - BLIP Captioner: python run.py (port 8000)")
        print("   - Clustr Backend: python run.py (port 5000)")
        return

    print()

    # Test BLIP integration
    integration_working = await test_blip_service_integration()
    if not integration_working:
        print("\n❌ BLIP integration not working. Check configuration.")
        return

    print()

    # Get initial statistics
    print("📊 Initial Statistics:")
    initial_stats = await get_caption_statistics()

    print()

    # Upload test images (if available)
    uploaded = await upload_test_images()

    print()

    # Test batch processing
    batch_success = await test_batch_processing()

    if batch_success:
        print("\n⏳ Waiting a moment for processing to complete...")
        await asyncio.sleep(5)

        print("\n📊 Final Statistics:")
        final_stats = await get_caption_statistics()

        if initial_stats and final_stats:
            captioned_diff = final_stats.get(
                'captioned', 0) - initial_stats.get('captioned', 0)
            if captioned_diff > 0:
                print(
                    f"✅ Successfully captioned {captioned_diff} additional images!")
            else:
                print("ℹ️  No new images were captioned (may already be processed)")

    print("\n🎉 Batch captioning tests completed!")
    print("\nYou can now:")
    print("   - Check the gallery at http://localhost:5173 (if frontend is running)")
    print("   - View API docs at http://localhost:5000/docs")
    print("   - Call /api/ml/caption-stats for current statistics")
    print("   - Use /api/ml/batch-process-uncaptioned to process more images")


if __name__ == "__main__":
    asyncio.run(main())
