"""Module for interacting with edge-ai"""

import json

from js import console, FormData
from pyodide.http import pyfetch
from pyscript import document, fetch


def _clear_fields():
    record_div = document.querySelector("#folio-inventory-records")
    record_div.classList.add("d-none")
    ai_agent_result = document.querySelector("#ai-agent-result")
    ai_agent_result.classList.add("d-none")
    instance_json_h2 = document.querySelector("#instance-json-h2")

    model_name_subtitle = document.querySelector("#model-name")
    model_name_subtitle.value = ""

    usage_list = document.querySelector("#ai-usage")
    usage_list.innerHTML = ""

    instance_record = document.querySelector("#instance-json")
    instance_record.innerHTML = ""
    folio_instance_json_heading = document.querySelector("#folio-instance-h2")
    folio_instance_json = document.querySelector("#folio-instance-json")
    folio_instance_json.innerHTML = ""

    folio_status = document.querySelector("#folio-result")
    folio_status.innerHTML = ""

    ai_messages_tbody = document.querySelector("#ai-messages")
    ai_messages_tbody.innerHTML = ""


def _generate_parts(parts: list):
    parts_table = document.createElement("table")
    for class_ in ["table", "table-sm"]:
        parts_table.classList.add(class_)
    parts_header = document.createElement("thead")
    parts_table.appendChild(parts_header)
    for class_ in ["bg-dark-subtle", "text-white"]:
        parts_header.classList.add(class_)
    parts_header_tr = document.createElement("tr")
    parts_header.appendChild(parts_header_tr)
    for header in ["Part Kind", "Time", "Content"]:
        parts_header_td = document.createElement("td")
        parts_header_td.innerHTML = header
        parts_header_tr.appendChild(parts_header_td)
    parts_tbody = document.createElement("tbody")
    parts_table.appendChild(parts_tbody)
    for part in parts:
        part_tr = document.createElement("tr")
        parts_tbody.appendChild(part_tr)
        part_kind_td = document.createElement("td")
        part_tr.appendChild(part_kind_td)
        part_kind_value = part.get("part_kind")
        if "tool_name" in part:
            part_kind_value = f"{part_kind_value}: <strong>{part['tool_name']}</strong>"
        part_kind_td.innerHTML = part_kind_value
        part_time_td = document.createElement("td")
        part_tr.appendChild(part_time_td)
        part_time_td.innerHTML = part.get("timestamp", "")
        part_content_td = document.createElement("td")
        part_tr.appendChild(part_content_td)
        part_content_value = part.get("content", "")
        if "args" in part:
            part_content_value = f"{part_content_value} {part['args']}"
        part_content_td.innerHTML = part_content_value
    return parts_table


def _messages(messages: list):
    ai_messages_table = document.querySelector("#ai-messages-table")
    ai_messages_tbody = document.querySelector("#ai-messages")

    for message in messages:
        tr = document.createElement("tr")
        kind_td = document.createElement("td")
        kind_td.innerHTML = message["kind"].title()
        tr.appendChild(kind_td)
        parts_td = document.createElement("td")
        parts_td.appendChild(_generate_parts(message.get("parts", [])))
        tr.appendChild(parts_td)
        usage_td = document.createElement("td")
        if "usage" in message:
            usage_ul = document.createElement("ul")
            input_li = document.createElement("li")
            input_li.innerHTML = (
                f"<strong>Input Tokens</strong>: {message['usage']['input_tokens']}"
            )
            usage_ul.appendChild(input_li)
            output_li = document.createElement("li")
            output_li.innerHTML = (
                f"<strong>Output Tokens</strong>: {message['usage']['output_tokens']}"
            )
            usage_ul.appendChild(output_li)
            usage_td.appendChild(usage_ul)
        tr.appendChild(usage_td)
        ai_messages_tbody.appendChild(tr)


def _model_usage(usage: dict):
    card = document.querySelector("#ai-usage-card")
    model_name_subtitle = document.querySelector("#model-name")
    usage_list = document.querySelector("#ai-usage")
    usage_stats = usage["usage"]
    model_name_subtitle.innerHTML = f"<em>Model:</em> {usage['model_name']}"
    request_li = document.createElement("li")
    request_tokens_li = document.createElement("li")
    response_tokens_li = document.createElement("li")
    total_tokens_li = document.createElement("li")

    request_li.innerHTML = (
        f"<strong>Requests:</strong> {usage_stats.get('requests', -1) }"
    )
    request_li.classList.add("list-group-item")
    usage_list.appendChild(request_li)
    request_tokens_li.innerHTML = (
        f"<strong>Request tokens:</strong> {usage_stats.get('request_tokens', -1):,}"
    )
    request_tokens_li.classList.add("list-group-item")
    usage_list.appendChild(request_tokens_li)
    response_tokens_li.innerHTML = (
        f"<strong>Response tokens:</strong> {usage_stats.get('response_tokens', -1):,}"
    )
    response_tokens_li.classList.add("list-group-item")
    usage_list.appendChild(response_tokens_li)
    total_tokens_li.innerHTML = (
        f"<strong>Total tokens:</strong> {usage_stats.get('total_tokens', -1):,}"
    )
    total_tokens_li.classList.add("list-group-item")
    usage_list.appendChild(total_tokens_li)


def display_instance_result(result):
    folio_inventory_div = document.querySelector("#folio-inventory-records")
    folio_inventory_div.classList.remove("d-none")
    agent_result = document.querySelector("#ai-agent-result")
    agent_result.classList.remove("d-none")

    instance_record = document.querySelector("#instance-json")
    instance_record.innerHTML = json.dumps(result.get("record"), indent=2)
    folio_status = document.querySelector("#folio-result")

    if "error" in result:
        folio_status.innerHTML = f"""<div class="alert alert-danger" role="alert">
<h2 class="alert-heading">ERROR!</h2><p>{result['error']}</p>
</div>"""
        folio_inventory_div.classList.add("d-none")
        agent_result.classList.add("d-none")
    else:
        folio_url_elem = document.querySelector("#folio-url")
        folio_instance_json_heading = document.querySelector("#folio-instance-h2")
        folio_instance_json = document.querySelector("#folio-instance-json")
        folio_instance_json.innerHTML = json.dumps(
            result.get("folio_response"), indent=2
        )

        instance_url = (
            f"{folio_url_elem.value}/inventory/view/{result['folio_response']['id']}"
        )
        folio_status.innerHTML = f"""<h2 class="text-success align-middle fs-1">Success!</h2>
            <a href="{instance_url}" class="fs-2">{instance_url}</a>"""
        if result["usage"] is None and result["ai_messages"] is None:
            console.log(f"Usage and AI Messages missing from response")
            return
        #_model_usage(result["usage"])
        _messages(result["usage"]["messages"])


async def submit_prompt(event):
    """Submits textual prompt to edge-ai to generate Inventory Instance"""
    loading_spinner = document.querySelector("#load-spinner")
    loading_spinner.classList.remove("d-none")
    _clear_fields()
    text_prompt = document.querySelector("#text-prompt")
    edge_ai = document.querySelector("#edge-ai-url")

    payload = {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"text": text_prompt.value, "model": "openai"}),
    }
    response = await fetch(f"{edge_ai.value}/inventory/instance/generate", **payload)
    result = await response.json()
    display_instance_result(result)
    loading_spinner.classList.add("d-none")
    text_prompt.innerHTML = ""


async def upload_image(event):
    """Submits book cover image to edge_ai to generate Inventory Instance"""
    loading_spinner = document.querySelector("#load-spinner")
    loading_spinner.classList.remove("d-none")
    _clear_fields()
    upload_image = document.querySelector("#cover-image")

    edge_ai = document.querySelector("#edge-ai-url")

    form_data = FormData.new()
    raw_image = upload_image.files.item(0)

    form_data.append("image", raw_image)

    response = await pyfetch(
        f"{edge_ai.value}/inventory/instance/generate_from_image",
        method="POST",
        body=form_data,
    )
    result = await response.json()
    display_instance_result(result)
    loading_spinner.classList.add("d-none")


async def toggle_messages(event):
    message_div = document.querySelector("#ai-messages-table")
    if "d-none" in message_div.classList:
        event.target.innerHTML = "Hide Agent Messages"
        message_div.classList.remove("d-none")
    else:
        event.target.innerHTML = "Show Agent Messages"
        message_div.classList.add("d-none")
