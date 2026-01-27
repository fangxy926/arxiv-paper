#!/usr/bin/env python3
"""LLM client utility"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_client():
    """Initialize OpenAI-compatible LLM client from environment variables"""
    api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return None
    return OpenAI(base_url=api_base, api_key=api_key)
