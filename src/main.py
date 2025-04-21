"""Module for interacting with edge-ai"""

import json

from js import console, FormData
from pyscript import document, fetch


def display_instance_result(result):
    instance_record = document.querySelector("#instance-json")
    instance_record_heading = document.querySelector("#instance-json-h2")
    instance_record.innerHTML = json.dumps(result.get("record"), indent=2)
    instance_record_heading.classList.remove("d-none")
    if result["folio_response"] is None:
        folio_status.innerHTML = (
            """<h2 class="text-success align-middle">Success!</h2>"""
        )
    elif "error" in result["folio_response"]:
        folio_status.innerHTML = (
            f"<h3>ERROR!</h3><p>{{ result['folio_response']['error'] }}</p>"
        )


async def submit_prompt(event):
    """Submits textual prompt to edge-ai to generate Inventory Instance"""
    text_prompt = document.querySelector("#text-prompt")
    edge_ai = document.querySelector("#edge-ai-url")
    folio_status = document.querySelector("#folio-result")
    payload = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"text": text_prompt.value, "model": "openai"}),
    }
    response = await fetch(f"{edge_ai.value}/inventory/instance/generate", **payload)
    result = await response.json()
    display_instance_result(result)
    text_prompt.innerHTML = ""


async def upload_image(event):
    """Submits book cover image to edge_ai to generate Inventory Instance"""
    upload_image = document.querySelector("#cover-image")

    edge_ai = document.querySelector("#edge-ai-url")

    form_data = FormData.new()
    raw_image = upload_image.files.item(0)

    form_data.append("image", raw_image)

    response = await fetch(
        f"{edge_ai.value}/inventory/instance/generate_from_image",
        method="POST",
        body=form_data,
    )
    result = await response.json()
    display_instance_result(result)
    console.log(f"Image upload raw image {raw_image.size}")
