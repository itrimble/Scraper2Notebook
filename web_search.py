#!/usr/bin/env python3
"""
Web Search Function for Scraper2Notebook

This script implements a simple web search function using DuckDuckGo's
command-line tool 'ddgr'. It can be integrated with the RAG system
to provide up-to-date information beyond the local knowledge base.
"""

import subprocess
import json
import os
import re
import sys

def web_search(query, num_results=3):
    """
    Perform a web search using DuckDuckGo via the ddgr command-line tool.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (default: 3)
        
    Returns:
        list: A list of dictionaries containing search results
    """
    try:
        # Check if ddgr is installed
        subprocess.run(["which", "ddgr"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Error: ddgr is not installed. Please install it first:")
        print("  macOS: brew install ddgr")
        print("  Linux: sudo apt install ddgr (or equivalent)")
        return []
    
    try:
        # Run the ddgr command
        cmd = ["ddgr", "--json", "--num", str(num_results), query]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the JSON output
        if result.stdout:
            try:
                search_results = json.loads(result.stdout)
                return search_results
            except json.JSONDecodeError:
                print(f"Error parsing search results: {result.stdout[:100]}...")
                return []
        else:
            return []
    except subprocess.CalledProcessError as e:
        print(f"Search error: {e}")
        return []

def format_search_results(results):
    """Format search results into a readable string."""
    if not results:
        return "No search results found."
    
    formatted = []
    for i, result in enumerate(results):
        formatted.append(f"{i+1}. {result.get('title', 'No title')}")
        formatted.append(f"   URL: {result.get('url', 'No URL')}")
        formatted.append(f"   {result.get('abstract', 'No description')}")
        formatted.append("")
    
    return "\n".join(formatted)

def main():
    """Run a web search from the command line."""
    if len(sys.argv) < 2:
        print("Usage: python web_search.py <search query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    results = web_search(query)
    print(format_search_results(results))

if __name__ == "__main__":
    main()
