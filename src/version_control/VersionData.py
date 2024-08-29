import asyncio
import streamlit as st
from  database.prompts import fetch_saved_prompts, fetch_all_versions_prompt

async def fetch_versions(i):
    loop = asyncio.get_event_loop()
    versions = await loop.run_in_executor(None, fetch_all_versions_prompt, i['id'])
    return i['prompt_title'], i['prompt'], i['id'], [{"Version":j['version'], "Prompt":j['prompt']} for j in versions.data]

async def main(a):
    data = {}
    tasks = [fetch_versions(i) for i in a]
    for future in asyncio.as_completed(tasks):
        prompt_title, prompt, prompt_id,  versions = await future
        data[prompt_title] = {"prompt": prompt, "prompt_id": prompt_id, "versions": versions}
    return data

def fetch_all_prompt_versions(userid):
    a = fetch_saved_prompts(userid).data

    # Create a new event loop and set it as the default
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the main function until it completes and return the result
    return loop.run_until_complete(main(a))