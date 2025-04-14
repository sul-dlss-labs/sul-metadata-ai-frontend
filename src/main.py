"""Module for interacting with edge-ai"""
import json

from js import console, FormData
from pyscript import document


async def submit_prompt(event):
    """Submits textual prompt to edge-ai to generate Inventory Instance"""
    text_prompt = document.querySelector("#text-prompt")
    console.log(f"Would submit {text_prompt.value} to edge-ai")


async def upload_image(event):
    """Submits book cover image to edge_ai to generate Inventory Instance"""
    upload_image = document.querySelector("#cover-image")
    # form_data = FormData.new()

    console.log(f"Image upload {upload_image.files}")
