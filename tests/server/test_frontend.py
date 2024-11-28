import asyncio
import multiprocessing
import time
import uvicorn
import pytest

from playwright.async_api import async_playwright
from starlette.testclient import WebSocketTestSession

from fastapi import FastAPI
from fastapi.testclient import TestClient


def start_server():
    from mock_server import app  # import your FastAPI application here
    uvicorn.run(app, host="localhost", port=8000)


@pytest.fixture(scope="session", autouse=True)
def server():
    # Start the FastAPI application in a separate process
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()

    # Give the frontend some time to start
    time.sleep(.3)

    yield

    # Terminate the frontend process after the tests have completed
    server_process.terminate()


@pytest.fixture
def test_client() -> TestClient:
    from semantic_pdf.server.app import app  # import your FastAPI application here
    test_client = TestClient(app)
    test_client.base_url = "http://localhost:8000"
    return test_client


@pytest.fixture
def test_websocket(test_client: TestClient) -> WebSocketTestSession:
    return test_client.websocket_connect("/ws")


# @pytest.mark.asyncio
# async def test_websocket_changes_page_content(
#         test_websocket: WebSocketTestSession,
#         frontend: FastAPI,
#         # test_client: TestClient,
# ):
#     async with async_playwright() as p:
#         # Start a new browser instance
#         browser = await p.chromium.launch()
#         page = await browser.new_page()
#
#         # Navigate to your web application
#         await page.goto("http://localhost:8000")
#
#         # Send a message over the WebSocket connection
#         message = {"type": "log", "payload": "Test message"}  # replace with your actual message
#         test_websocket.send_json(message)
#
#         # Wait for the page to update
#         await asyncio.sleep(1)
#         print(await page.content())
#
#         # Check the contents of the element that should be updated
#         updated_element = await page.query_selector("#logs")  # replace with your actual selector
#         assert updated_element is not None
#         print("updated element: ", updated_element)
#         updated_content = await page.evaluate("element => element.textContent", updated_element)
#         print("updated content: ", updated_content)
#         assert "Test message" in updated_content
#
#         # Close the browser instance
#         await browser.close()