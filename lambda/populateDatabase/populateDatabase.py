from json import loads

def handler(event,context):
    """This function will run nightly and will poll for updates to the wiki and update or add the embeddings"""
    # Send a GET request like this https://denhac.org/wp-json/wp/v2/epkb_post_type_1?modified_after=2024-04-01T05:19:07
    # Parse JSON
    # Update embeddings for each updated post

    return "Big Success"