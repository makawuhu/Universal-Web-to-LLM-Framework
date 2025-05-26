#!/usr/bin/env python3
"""
Ultimate OPM Memo Processor - Combines download + upload + TRUE embedding
"""

import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Configuration
CONFIG = {
    "ANYTHINGLLM_API_KEY": "PHK1CK9-QVGMXPC-PK2PQBK-G4CM8V1",
    "ANYTHINGLLM_BASE_URL": "http://192.168.4.7:3001",
    "WORKSPACE_SLUG": "opm-memos",
    "WORKSPACE_NAME": "OPM Memos",
    "MEMO_INDEX_URL": "https://www.opm.gov/policy-data-oversight/latest-and-other-highlighted-memos/",
    "DOWNLOAD_DIR": "./opm_downloads",
    "MAX_RETRIES": 3,
    "RETRY_DELAY": 5,
    "TIMEOUT": 30
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultimate_opm_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltimateOPMProcessor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {CONFIG['ANYTHINGLLM_API_KEY']}",
            "User-Agent": "Ultimate-OPM-Processor/1.0"
        })
        self.base_url = CONFIG['ANYTHINGLLM_BASE_URL']
        self.workspace_slug = CONFIG['WORKSPACE_SLUG']
        
        # Create download directory
        Path(CONFIG['DOWNLOAD_DIR']).mkdir(exist_ok=True)
        
        print("=" * 80)
        print("🏛️  Ultimate OPM Memo Processor - Download + Upload + TRUE Embedding!")
        print("=" * 80)
        print(f"🎯 Target: {self.base_url}")
        print(f"📂 Workspace: {self.workspace_slug}")
        print(f"✨ Method: Download → Upload → Move to Workspace → Embed")
    
    def test_connection(self):
        """Test connection to AnythingLLM"""
        print(f"🔗 Testing connection to {self.base_url}...")
        try:
            response = requests.get(f"{self.base_url}/api/v1/workspaces", 
                                  headers={"Authorization": f"Bearer {CONFIG['ANYTHINGLLM_API_KEY']}"}, 
                                  timeout=10)
            response.raise_for_status()
            print("✅ Connection successful!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def download_opm_memos(self, limit=10):
        """Download OPM memo PDFs using proven BeautifulSoup method"""
        print("📥 Fetching OPM memo links...")
        
        try:
            response = requests.get(CONFIG['MEMO_INDEX_URL'], timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Failed to fetch memo index: {e}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        memo_links = [urljoin(CONFIG['MEMO_INDEX_URL'], a['href']) 
                      for a in soup.find_all("a", href=True) 
                      if a['href'].endswith(".pdf")]
        
        print(f"📋 Found {len(memo_links)} memo links")
        
        if limit:
            memo_links = memo_links[:limit]
            print(f"⚡ Limited to {limit} memos for processing")
        
        downloaded = []
        for i, link in enumerate(memo_links, 1):
            filename = Path(link).name
            filepath = Path(CONFIG['DOWNLOAD_DIR']) / filename
            
            print(f"📄 [{i}/{len(memo_links)}] {filename}")
            
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
    
    def ensure_workspace_exists(self):
        """Create workspace if it doesn't exist"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workspace/{self.workspace_slug}")
            print(f"✅ Workspace '{self.workspace_slug}' already exists")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"🔧 Creating workspace '{self.workspace_slug}'...")
                payload = {
                    "name": CONFIG['WORKSPACE_NAME'],
                    "slug": self.workspace_slug
                }
                response = self.session.post(
                    f"{self.base_url}/api/v1/workspace/new",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                print("✅ Workspace created successfully")
                return True
            else:
                raise
    
    def upload_to_anythingllm(self, file_paths):
        """Upload files to AnythingLLM folder"""
        print(f"\n📤 Uploading {len(file_paths)} files to AnythingLLM...")
        
        uploaded_docs = []
        
        for i, file_path in enumerate(file_paths, 1):
            filename = Path(file_path).name
            print(f"\n📄 [{i}/{len(file_paths)}] Processing: {filename}")
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, 'application/pdf')}
                    data = {'folder': 'opm-memos'}
                    
                    # Use separate headers for file upload
                    upload_headers = {'Authorization': f"Bearer {CONFIG['ANYTHINGLLM_API_KEY']}"}
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/document/upload",
                        files=files,
                        data=data,
                        headers=upload_headers,
                        timeout=CONFIG['TIMEOUT']
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    if result.get('success'):
                        doc_info = result.get('document', {})
                        uploaded_docs.append(doc_info.get('location', filename))
                        
                        print(f"   ✅ Upload successful!")
                        if 'metadata' in doc_info:
                            metadata = json.loads(doc_info['metadata'])
                            print(f"   📋 Title: {metadata.get('title', 'Unknown')}")
                            print(f"   📊 Word Count: {metadata.get('wordCount', 'Unknown')}")
                        print(f"   📍 Location: {doc_info.get('location', 'Unknown')}")
                    else:
                        print(f"   ❌ Upload failed: {result}")
                        
            except Exception as e:
                print(f"   ❌ Failed to upload {filename}: {e}")
        
        print(f"\n✅ Successfully uploaded {len(uploaded_docs)} documents to omp-memos folder")
        return uploaded_docs
    
    def move_to_workspace_and_embed(self):
        """Move ALL documents from ALL folders to workspace for TRUE embedding"""
        print(f"\n🧠 Moving ALL documents to workspace for TRUE embedding...")
        
        # Get documents from ALL folders
        response = self.session.get(f"{self.base_url}/api/v1/documents")
        response.raise_for_status()
        data = response.json()
        
        # Find documents in ALL folders
        all_docs = []
        folder_names = []
        
        if 'localFiles' in data and 'items' in data['localFiles']:
            for folder in data['localFiles']['items']:
                folder_name = folder.get('name', 'unknown')
                folder_docs = folder.get('items', [])
                
                if folder_docs:  # Only process folders with documents
                    folder_names.append(folder_name)
                    print(f"   📁 {folder_name}: {len(folder_docs)} documents")
                    
                    # Add all documents from this folder
                    for doc in folder_docs:
                        doc_identifier = f"{folder_name}/{doc['name']}"
                        all_docs.append(doc_identifier)
        
        print(f"   📊 Total: {len(all_docs)} documents across {len(folder_names)} folders")
        
        if not all_docs:
            print("❌ No documents found in any folders")
            return False
        
        # Add ALL documents to workspace (THIS is what triggers real embedding)
        payload = {"adds": all_docs}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workspace/{self.workspace_slug}/update-embeddings",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            print(f"   ✅ ALL {len(all_docs)} documents moved to workspace - TRUE embedding initiated!")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to move to workspace: {e}")
            return False
    
    def verify_embedding(self):
        """Verify that documents are truly embedded and searchable"""
        print(f"\n🔍 Verifying TRUE embedding...")
        
        # Check workspace has documents
        response = self.session.get(f"{self.base_url}/api/v1/workspace/{self.workspace_slug}")
        response.raise_for_status()
        data = response.json()
        
        doc_count = 0
        if 'workspace' in data:
            workspace_info = data['workspace']
            if isinstance(workspace_info, list) and workspace_info:
                docs = workspace_info[0].get('documents', [])
                doc_count = len(docs)
        
        print(f"   📊 Documents in workspace: {doc_count}")
        
        if doc_count == 0:
            print("   ❌ No documents in workspace - embedding failed")
            return False
        
        # Test actual embedding with a comprehensive question
        print("   🧪 Testing embedding with comprehensive question...")
        
        payload = {
            "message": "How many different OPM memos do you have access to? List the main policy areas covered.",
            "mode": "chat"
        }
        
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
            
            print(f"   📝 Answer length: {len(answer)} characters")
            print(f"   📚 Sources cited: {len(sources)}")
            
            if sources and len(answer) > 100:
                print("   ✅ TRUE EMBEDDING CONFIRMED!")
                print("   📄 Source documents being accessed:")
                for i, source in enumerate(sources[:5], 1):
                    title = source.get('title', 'Unknown')
                    clean_title = title.replace('.pdf', '').replace('-', ' ').title()
                    print(f"      {i}. {clean_title}")
                
                if len(sources) > 5:
                    print(f"      ... and {len(sources) - 5} more sources")
                
                print(f"   💬 Answer preview: {answer[:150]}...")
                return True
            else:
                print("   ⚠️ Embedding may not be working - no sources or short answer")
                return False
                
        except Exception as e:
            print(f"   ❌ Embedding test failed: {e}")
            return False
    
    def run_complete_workflow(self, limit=10):
        """Run the complete workflow with TRUE embedding"""
        if not self.test_connection():
            return False
        
        # Step 1: Download memos
        downloaded_files = self.download_opm_memos(limit)
        if not downloaded_files:
            print("❌ No files downloaded")
            return False
        
        # Step 2: Ensure workspace exists
        self.ensure_workspace_exists()
        
        # Step 3: Upload to folder
        uploaded_docs = self.upload_to_anythingllm(downloaded_files)
        if not uploaded_docs:
            print("❌ No files uploaded")
            return False
        
        # Step 4: Move to workspace for TRUE embedding
        if not self.move_to_workspace_and_embed():
            print("❌ Failed to embed documents")
            return False
        
        # Step 5: Verify embedding works
        embedding_success = self.verify_embedding()
        
        # Final summary
        print("\n" + "=" * 80)
        if embedding_success:
            print("🎉 ULTIMATE SUCCESS!")
            print("   ✅ Downloaded memos")
            print("   ✅ Uploaded to AnythingLLM") 
            print("   ✅ Moved to workspace")
            print("   ✅ TRUE EMBEDDING CONFIRMED!")
            print(f"\n🌐 Access: {self.base_url}/workspace/{self.workspace_slug}")
            print("\n💬 Try asking:")
            print("   • 'Summarize all recent federal employment policy changes'")
            print("   • 'What are all the executive orders mentioned in the memos?'")
            print("   • 'List all guidance related to collective bargaining and RIFs'")
            print("   • 'How many different policy areas do these memos cover?'")
        else:
            print("⚠️ PARTIAL SUCCESS - Documents uploaded but embedding unclear")
            print("   Try testing manually in the web interface")
        
        return embedding_success

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Ultimate OPM Memo Processor')
    parser.add_argument('--limit', type=int, default=10, help='Max memos to process (default: 10)')
    parser.add_argument('--test-only', action='store_true', help='Only test embedding')
    
    args = parser.parse_args()
    
    processor = UltimateOPMProcessor()
    
    if args.test_only:
        success = processor.verify_embedding()
    else:
        success = processor.run_complete_workflow(args.limit)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())