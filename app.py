#!/usr/bin/env python3
import os
import json
import logging
import re
from flask import Flask, Response
import requests
import xml.etree.ElementTree as ET
import urllib.parse

# Set up logging based on LOG_LEVEL env variable
log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
numeric_log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(level=numeric_log_level)
logger = logging.getLogger(__name__)

# Read required configuration from environment variables
FEED_URL = os.environ.get('FEED_URL')
if not FEED_URL:
    logger.error("Environment variable FEED_URL is not set.")
    raise RuntimeError("FEED_URL environment variable not set")

# Optional: specify the source feed's encoding (e.g., "windows-1251")
FEED_ENCODING = os.environ.get('FEED_ENCODING')

# Transformation rules: a JSON string representing a list of rules.
# Each rule is an object with keys: "field", "regex", "replacement".
transform_rules_str = os.environ.get('TRANSFORM_RULES')
if transform_rules_str:
    try:
        TRANSFORM_RULES = json.loads(transform_rules_str)
        logger.info("Loaded %d transformation rules.", len(TRANSFORM_RULES))
    except json.JSONDecodeError as e:
        logger.error("Error decoding TRANSFORM_RULES: %s", e)
        TRANSFORM_RULES = []
else:
    TRANSFORM_RULES = []
    logger.info("No transformation rules provided.")

app = Flask(__name__)

@app.route('/feed')
def proxy_feed():
    try:
        # Fetch the original feed
        response = requests.get(FEED_URL)
        response.raise_for_status()
    except Exception as e:
        logger.error("Error fetching feed: %s", e)
        return Response("Error fetching feed", status=500)
    
    # If an explicit feed encoding is provided, use it.
    if FEED_ENCODING:
        response.encoding = FEED_ENCODING
        logger.info("Overriding response encoding with: %s", FEED_ENCODING)
    elif not response.encoding:
        # Fallback: assume UTF-8 if none detected
        response.encoding = 'utf-8'
    
    # Get the feed as a Unicode string
    feed_text = response.text

    # Parse the feed XML
    try:
        tree = ET.ElementTree(ET.fromstring(feed_text))
    except ET.ParseError as e:
        logger.error("Error parsing feed XML: %s", e)
        return Response("Error parsing feed XML", status=500)
    
    # Apply transformation rules to each item in the feed
    # Assumes standard RSS structure: <rss><channel><item>...
    channel = tree.find('channel')
    if channel is None:
        logger.warning("No <channel> element found in feed; transformation rules not applied.")
    else:
        for item in channel.findall('item'):
            for rule in TRANSFORM_RULES:
                field = rule.get('field')
                regex = rule.get('regex')
                replacement = rule.get('replacement')
                if not field or not regex or replacement is None:
                    logger.warning("Incomplete transformation rule skipped: %s", rule)
                    continue
                element = item.find(field)
                if element is not None and element.text:
                    original_text = element.text
                    try:
                        # If the rule is for the "link" field, use a custom replacement function
                        if field.lower() == "link":
                            def repl(match):
                                # Replace "$1" with the HTML-escaped original text.
                                return replacement.replace("$1", urllib.parse.quote(original_text, safe=''))
                            new_text = re.sub(regex, repl, original_text)
                        else:
                            new_text = re.sub(regex, replacement, original_text)
                        logger.debug("Transformed '%s' to '%s' using rule: %s", original_text, new_text, rule)
                        element.text = new_text
                    except re.error as e:
                        logger.error("Regex error in rule %s: %s", rule, e)
    
    # Produce the modified feed as UTF-8 with an XML declaration
    try:
        output_xml = ET.tostring(tree.getroot(), encoding='utf-8', xml_declaration=True)
    except Exception as e:
        logger.error("Error generating output XML: %s", e)
        return Response("Error generating XML", status=500)
    
    return Response(output_xml, mimetype='application/rss+xml')

if __name__ == '__main__':
    # Listen on all interfaces on port 5000 (or adjust as needed)
    app.run(host='0.0.0.0', port=5000)
