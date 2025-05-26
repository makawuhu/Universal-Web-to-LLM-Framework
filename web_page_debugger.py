#!/usr/bin/env python3
"""
Web Page Debugger - See what's actually on a page
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

def debug_webpage(url):
    """Debug what's actually on a webpage"""
    print(f"🔍 Debugging webpage: {url}")
    print("=" * 80)
    
    # Browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        time.sleep(2)
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"✅ Successfully loaded page (Status: {response.status_code})")
        print(f"📄 Content length: {len(response.text)} characters")
        
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Check for PDF links
    print(f"\n📎 SEARCHING FOR PDF LINKS")
    print("-" * 40)
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.endswith('.pdf'):
            full_url = urljoin(url, href)
            pdf_links.append((full_url, a.get_text(strip=True)))
    
    if pdf_links:
        print(f"✅ Found {len(pdf_links)} PDF links:")
        for i, (link, text) in enumerate(pdf_links[:10], 1):
            print(f"   {i}. {text[:60]}...")
            print(f"      {link}")
        if len(pdf_links) > 10:
            print(f"   ... and {len(pdf_links) - 10} more")
    else:
        print("❌ No direct PDF links found")
    
    # Check for other document links
    print(f"\n📄 SEARCHING FOR OTHER DOCUMENT LINKS")
    print("-" * 40)
    doc_extensions = ['.doc', '.docx', '.txt', '.html', '.htm']
    other_docs = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if any(href.endswith(ext) for ext in doc_extensions):
            full_url = urljoin(url, href)
            other_docs.append((full_url, a.get_text(strip=True)))
    
    if other_docs:
        print(f"✅ Found {len(other_docs)} other document links:")
        for i, (link, text) in enumerate(other_docs[:5], 1):
            print(f"   {i}. {text[:60]}...")
            print(f"      {link}")
    else:
        print("❌ No other document links found")
    
    # Look for common patterns that might indicate documents
    print(f"\n🔍 SEARCHING FOR DOCUMENT PATTERNS")
    print("-" * 40)
    
    # Look for links with "guidance", "document", "download" etc.
    guidance_links = []
    keywords = ['guidance', 'document', 'download', 'file', 'report', 'publication']
    
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a['href'].lower()
        
        if any(keyword in text or keyword in href for keyword in keywords):
            full_url = urljoin(url, a['href'])
            guidance_links.append((full_url, a.get_text(strip=True)))
    
    if guidance_links:
        print(f"✅ Found {len(guidance_links)} potential document links:")
        for i, (link, text) in enumerate(guidance_links[:10], 1):
            print(f"   {i}. {text[:60]}...")
            print(f"      {link}")
    else:
        print("❌ No document-related links found")
    
    # Show page title and structure
    print(f"\n📋 PAGE INFORMATION")
    print("-" * 40)
    title = soup.find('title')
    if title:
        print(f"📝 Title: {title.get_text(strip=True)}")
    
    # Count different types of links
    all_links = soup.find_all("a", href=True)
    print(f"🔗 Total links: {len(all_links)}")
    
    # Look for common content patterns
    tables = soup.find_all("table")
    lists = soup.find_all(["ul", "ol"])
    divs = soup.find_all("div")
    
    print(f"📊 Page structure:")
    print(f"   • Tables: {len(tables)}")
    print(f"   • Lists: {len(lists)}")
    print(f"   • Divs: {len(divs)}")
    
    # Show a sample of the page content
    print(f"\n📝 SAMPLE PAGE CONTENT")
    print("-" * 40)
    page_text = soup.get_text()
    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
    
    print("First 10 non-empty lines:")
    for i, line in enumerate(lines[:10], 1):
        print(f"   {i}. {line[:80]}...")
    
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 40)
    if pdf_links:
        print("✅ Direct PDF scraping should work!")
    elif other_docs:
        print("⚠️ Try including other file extensions (.doc, .docx, etc.)")
    elif guidance_links:
        print("🔍 Documents might be behind additional clicks - need custom scraping logic")
    else:
        print("❌ This page might not have direct document links")
        print("   • Documents could be loaded with JavaScript")
        print("   • Might need to navigate to specific sections")
        print("   • Could require form submissions or searches")

if __name__ == "__main__":
    url = input("🌐 Enter URL to debug: ").strip()
    if url:
        debug_webpage(url)
    else:
        print("❌ No URL provided")