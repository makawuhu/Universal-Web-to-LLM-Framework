#!/usr/bin/env python3
"""
Universal Web-to-LLM Framework
Interactive processor for any website with document collections
"""

import requests
import json
import time
import os
import glob
from datetime import datetime
from pathlib import Path
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class UniversalWebToLLMProcessor:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config['ANYTHINGLLM_API_KEY']}",
            "User-Agent": config.get('USER_AGENT', 'Universal-Web-LLM-Processor/1.0')
        })
        self.base_url = config['ANYTHINGLLM_BASE_URL']
        self.workspace_slug = config['WORKSPACE_SLUG']
        
        # Create download directory (with parents)
        Path(config['DOWNLOAD_DIR']).mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print(f"🌐 Universal Web-to-LLM Processor - {config['SOURCE_NAME']}")
        print("=" * 80)
        print(f"🎯 Target: {self.base_url}")
        print(f"📂 Workspace: {self.workspace_slug}")
        print(f"🔗 Source: {config['SOURCE_URL']}")
    
    def scrape_document_links(self, limit=None):
        """Generic document scraper with browser-like headers"""
        print(f"📥 Scraping {self.config['SOURCE_NAME']} for documents...")
        
        # More browser-like headers to avoid detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            # Add delay to be respectful
            time.sleep(2)
            response = requests.get(self.config['SOURCE_URL'], headers=headers, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch source page: {e}")
            print("💡 This might be due to:")
            print("   • Anti-bot protection on the website")
            print("   • Rate limiting")
            print("   • Invalid URL")
            print("   • Network connectivity issues")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Generic approach - find all links matching file extensions
        file_extensions = self.config.get('FILE_EXTENSIONS', ['.pdf'])
        document_links = []
        
        for a in soup.find_all("a", href=True):
            href = a['href']
            if any(href.endswith(ext) for ext in file_extensions):
                full_url = urljoin(self.config['SOURCE_URL'], href)
                document_links.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in document_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        if limit:
            unique_links = unique_links[:limit]
        
        print(f"📋 Found {len(unique_links)} document links")
        return unique_links
    
    def download_documents(self, links):
        """Download documents from links"""
        print(f"📥 Downloading {len(links)} documents...")
        
        downloaded = []
        for i, link in enumerate(links, 1):
            filename = Path(urlparse(link).path).name
            if not filename:  # Handle cases where filename isn't clear
                filename = f"document_{i}.pdf"
                
            filepath = Path(self.config['DOWNLOAD_DIR']) / filename
            
            print(f"📄 [{i}/{len(links)}] {filename}")
            
            if filepath.exists():
                print(f"   ✓ Already exists ({filepath.stat().st_size} bytes)")
                downloaded.append(filepath)
                continue
                
            try:
                print(f"   ⬇️ Downloading...")
                with requests.get(link, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                print(f"   ✅ Downloaded ({filepath.stat().st_size} bytes)")
                downloaded.append(filepath)
                
            except Exception as e:
                print(f"   ❌ Download failed: {e}")
        
        return downloaded
    
    def upload_to_anythingllm(self, file_paths):
        """Upload files to AnythingLLM"""
        print(f"\n📤 Uploading {len(file_paths)} files to AnythingLLM...")
        
        uploaded_docs = []
        folder_name = self.config.get('FOLDER_NAME', self.workspace_slug)
        
        for i, file_path in enumerate(file_paths, 1):
            filename = Path(file_path).name
            print(f"\n📄 [{i}/{len(file_paths)}] Processing: {filename}")
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, 'application/pdf')}
                    data = {'folder': folder_name}
                    
                    upload_headers = {'Authorization': f"Bearer {self.config['ANYTHINGLLM_API_KEY']}"}
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/document/upload",
                        files=files,
                        data=data,
                        headers=upload_headers,
                        timeout=30
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    if result.get('success'):
                        doc_info = result.get('document', {})
                        uploaded_docs.append(doc_info.get('location', filename))
                        print(f"   ✅ Upload successful!")
                    else:
                        print(f"   ❌ Upload failed: {result}")
                        
            except Exception as e:
                print(f"   ❌ Failed to upload {filename}: {e}")
        
        return uploaded_docs
    
    def embed_all_documents(self):
        """Move all documents to workspace for embedding"""
        print(f"\n🧠 Embedding all documents in workspace...")
        
        # Get all documents from all folders
        response = self.session.get(f"{self.base_url}/api/v1/documents")
        response.raise_for_status()
        data = response.json()
        
        all_docs = []
        if 'localFiles' in data and 'items' in data['localFiles']:
            for folder in data['localFiles']['items']:
                folder_name = folder.get('name', 'unknown')
                folder_docs = folder.get('items', [])
                
                if folder_docs:
                    for doc in folder_docs:
                        doc_identifier = f"{folder_name}/{doc['name']}"
                        all_docs.append(doc_identifier)
        
        if not all_docs:
            print("❌ No documents found")
            return False
        
        print(f"   📚 Found {len(all_docs)} total documents")
        
        # Add to workspace
        payload = {"adds": all_docs}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workspace/{self.workspace_slug}/update-embeddings",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"   ✅ All documents embedded in workspace!")
            return True
        except Exception as e:
            print(f"   ❌ Embedding failed: {e}")
            return False
    
    def test_knowledge_base(self):
        """Test the knowledge base with domain-specific questions"""
        test_questions = self.config.get('TEST_QUESTIONS', [
            "What documents do you have access to?",
            "What are the main topics covered in these documents?",
            "Summarize the key information from your knowledge base."
        ])
        
        print(f"\n🧪 Testing knowledge base...")
        
        for question in test_questions[:2]:  # Test first 2 questions
            print(f"   ❓ Question: {question}")
            
            payload = {"message": question, "mode": "chat"}
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/workspace/{self.workspace_slug}/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                answer = result.get('textResponse', '')
                sources = result.get('sources', [])
                
                print(f"   📝 Response: {len(answer)} characters")
                print(f"   📚 Sources: {len(sources)} documents")
                
                if sources:
                    print("   ✅ Knowledge base working!")
                else:
                    print("   ⚠️ No sources found")
                    
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        
        return True
    
    def run_complete_workflow(self, limit=None):
        """Run the complete workflow"""
        # Step 1: Scrape document links
        links = self.scrape_document_links(limit)
        if not links:
            return False
        
        # Step 2: Download documents
        downloaded = self.download_documents(links)
        if not downloaded:
            return False
        
        # Step 3: Upload to AnythingLLM
        uploaded = self.upload_to_anythingllm(downloaded)
        if not uploaded:
            return False
        
        # Step 4: Embed in workspace
        if not self.embed_all_documents():
            return False
        
        # Step 5: Test knowledge base
        self.test_knowledge_base()
        
        print("\n" + "=" * 80)
        print("🎉 SUCCESS! Knowledge base ready for queries")
        print(f"🌐 Access: {self.base_url}/workspace/{self.workspace_slug}")
        
        return True

def get_user_configuration():
    """Interactive configuration setup"""
    print("=" * 80)
    print("🎯 Interactive Web-to-LLM Processor Setup")
    print("=" * 80)
    
    config = {}
    
    # Basic source information
    print("\n📁 SOURCE CONFIGURATION")
    print("-" * 40)
    config['SOURCE_NAME'] = input("📝 Enter a name for this source (e.g., 'FDA Guidance', 'Company Docs'): ").strip()
    config['SOURCE_URL'] = input("🌐 Enter the URL to scrape documents from: ").strip()
    
    # AnythingLLM configuration
    print("\n🤖 ANYTHINGLLM CONFIGURATION")
    print("-" * 40)
    config['ANYTHINGLLM_BASE_URL'] = input("🔗 Enter AnythingLLM server URL (e.g., http://192.168.4.7:3001): ").strip()
    config['ANYTHINGLLM_API_KEY'] = input("🔑 Enter AnythingLLM API key: ").strip()
    
    # Workspace configuration
    print("\n📂 WORKSPACE CONFIGURATION")
    print("-" * 40)
    default_slug = config['SOURCE_NAME'].lower().replace(' ', '-').replace('_', '-')
    workspace_input = input(f"📋 Enter workspace name (default: {default_slug}): ").strip()
    config['WORKSPACE_SLUG'] = workspace_input if workspace_input else default_slug
    config['FOLDER_NAME'] = config['WORKSPACE_SLUG']
    
    # File configuration
    print("\n📄 FILE CONFIGURATION")
    print("-" * 40)
    print("Common file types: pdf, doc, docx, txt, html")
    extensions_input = input("📎 Enter file extensions to download (comma-separated, default: pdf): ").strip()
    if extensions_input:
        extensions = [f".{ext.strip().lstrip('.')}" for ext in extensions_input.split(',')]
    else:
        extensions = ['.pdf']
    config['FILE_EXTENSIONS'] = extensions
    
    # Limits and options
    print("\n⚙️  PROCESSING OPTIONS")
    print("-" * 40)
    limit_input = input("🔢 Maximum documents to process (default: 20, 0 for no limit): ").strip()
    try:
        limit = int(limit_input) if limit_input else 20
        limit = None if limit == 0 else limit
    except ValueError:
        limit = 20
    config['LIMIT'] = limit
    
    # Download directory
    safe_name = config['SOURCE_NAME'].lower().replace(' ', '_').replace('-', '_')
    config['DOWNLOAD_DIR'] = f"./downloads/{safe_name}"
    
    # Test questions
    print("\n🧪 TEST QUESTIONS (Optional)")
    print("-" * 40)
    print("Enter 2-3 test questions to verify the knowledge base works.")
    print("Press Enter to skip a question.")
    
    test_questions = []
    for i in range(3):
        question = input(f"❓ Test question {i+1}: ").strip()
        if question:
            test_questions.append(question)
    
    if not test_questions:
        test_questions = [
            "What documents do you have access to?",
            "What are the main topics covered in these documents?",
            "Summarize the key information available."
        ]
    
    config['TEST_QUESTIONS'] = test_questions
    config['USER_AGENT'] = 'Interactive-Web-LLM-Processor/1.0'
    
    # Display configuration summary
    print("\n" + "=" * 80)
    print("📋 CONFIGURATION SUMMARY")
    print("=" * 80)
    print(f"📝 Source Name: {config['SOURCE_NAME']}")
    print(f"🌐 Source URL: {config['SOURCE_URL']}")
    print(f"🤖 AnythingLLM Server: {config['ANYTHINGLLM_BASE_URL']}")
    print(f"📂 Workspace: {config['WORKSPACE_SLUG']}")
    print(f"📎 File Types: {', '.join(config['FILE_EXTENSIONS'])}")
    print(f"🔢 Document Limit: {config['LIMIT'] if config['LIMIT'] else 'No limit'}")
    print(f"📁 Download Directory: {config['DOWNLOAD_DIR']}")
    print(f"🧪 Test Questions: {len(config['TEST_QUESTIONS'])} configured")
    
    # Confirmation
    print("\n" + "-" * 80)
    confirm = input("✅ Proceed with this configuration? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Setup cancelled.")
        return None
    
    return config

def save_configuration(config):
    """Save configuration for reuse"""
    config_file = f"config_{config['WORKSPACE_SLUG']}.json"
    try:
        # Remove sensitive info for saving
        save_config = config.copy()
        save_config['ANYTHINGLLM_API_KEY'] = "[REDACTED]"
        
        with open(config_file, 'w') as f:
            json.dump(save_config, f, indent=2)
        print(f"💾 Configuration saved to {config_file}")
    except Exception as e:
        print(f"⚠️ Could not save configuration: {e}")

def load_configuration():
    """Load a saved configuration"""
    config_files = glob.glob("config_*.json")
    if not config_files:
        return None
    
    print("\n📁 SAVED CONFIGURATIONS")
    print("-" * 40)
    for i, file in enumerate(config_files, 1):
        workspace_name = file.replace('config_', '').replace('.json', '')
        print(f"{i}. {workspace_name}")
    
    print(f"{len(config_files) + 1}. Create new configuration")
    print(f"{len(config_files) + 2}. Delete a configuration")
    
    try:
        choice = int(input(f"\nSelect option (1-{len(config_files) + 2}): "))
        
        if choice == len(config_files) + 1:
            return None  # Create new
        elif choice == len(config_files) + 2:
            return delete_configuration(config_files)  # Delete
        
        config_file = config_files[choice - 1]
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Need to get API key again for security
        config['ANYTHINGLLM_API_KEY'] = input("🔑 Enter AnythingLLM API key: ").strip()
        
        print(f"✅ Loaded configuration: {config['SOURCE_NAME']}")
        return config
        
    except (ValueError, IndexError, FileNotFoundError):
        print("❌ Invalid selection")
        return None

def delete_configuration(config_files):
    """Delete a saved configuration"""
    print("\n🗑️  DELETE CONFIGURATION")
    print("-" * 40)
    
    for i, file in enumerate(config_files, 1):
        workspace_name = file.replace('config_', '').replace('.json', '')
        print(f"{i}. {workspace_name}")
    
    print(f"{len(config_files) + 1}. Cancel")
    
    try:
        choice = int(input(f"\nSelect configuration to delete (1-{len(config_files) + 1}): "))
        
        if choice == len(config_files) + 1:
            print("❌ Deletion cancelled")
            return load_configuration()  # Go back to main menu
        
        config_file = config_files[choice - 1]
        workspace_name = config_file.replace('config_', '').replace('.json', '')
        
        confirm = input(f"⚠️  Really delete '{workspace_name}' configuration? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            os.remove(config_file)
            print(f"✅ Deleted configuration: {workspace_name}")
        else:
            print("❌ Deletion cancelled")
        
        return load_configuration()  # Go back to main menu
        
    except (ValueError, IndexError, FileNotFoundError):
        print("❌ Invalid selection")
        return load_configuration()

def main():
    """Interactive main function"""
    print("🚀 Welcome to the Universal Web-to-LLM Processor!")
    
    # Try to load existing configuration or create new one
    config = load_configuration()
    if not config:
        config = get_user_configuration()
        if not config:
            return 1
        save_configuration(config)
    
    # Run the processor
    processor = UniversalWebToLLMProcessor(config)
    success = processor.run_complete_workflow(config.get('LIMIT'))
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())