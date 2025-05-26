# Universal Web-to-LLM Framework

🌐 **Automatically scrape websites and create searchable AI knowledge bases with AnythingLLM**

Transform any document collection on the web into an intelligent, conversational knowledge base in minutes!

## ✨ Features

- 🤖 **Interactive Setup** - Guided configuration for any website
- 📥 **Smart Scraping** - Handles PDF, DOC, TXT, and other document formats  
- 🧠 **Auto-Embedding** - Seamlessly integrates with AnythingLLM
- 💾 **Config Management** - Save and reuse configurations
- 🔍 **Debug Tools** - Analyze any webpage to understand its structure
- 🛡️ **Anti-Bot Protection** - Browser-like headers to avoid detection
- ✅ **Verification** - Tests knowledge base with custom questions

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install requests beautifulsoup4
```

### 2. Run the Interactive Setup
```bash
python universal_web_to_llm_framework.py
```

### 3. Follow the Prompts
- Enter website URL to scrape
- Configure AnythingLLM connection
- Set workspace name and preferences
- Add test questions

### 4. Watch the Magic Happen! ✨
The framework will:
1. Scrape documents from your target website
2. Download them locally
3. Upload to AnythingLLM
4. Embed them for AI search
5. Test with your custom questions

## 📖 Example Use Cases

### Government & Regulatory
- **OPM Memos** - Federal employment guidance
- **FDA Guidance** - Drug and medical device regulations
- **SEC Filings** - Financial regulations and rules
- **EPA Standards** - Environmental guidelines

### Academic & Research  
- **ArXiv Papers** - Latest research publications
- **PubMed Studies** - Medical research
- **University Docs** - Course materials and policies

### Corporate & Legal
- **Company Policies** - Internal documentation
- **Industry Standards** - ISO, NIST specifications
- **Legal Databases** - Case law and regulations

## 🛠️ Tools Included

### `universal_web_to_llm_framework.py`
Main interactive framework with full workflow automation

### `web_page_debugger.py`  
Debug tool to analyze website structure and find document links

### `ultimate_opm_processor.py`
Specialized processor for OPM government memos (example implementation)

## ⚙️ Configuration

Configurations are saved as JSON files for easy reuse:

```json
{
  "SOURCE_NAME": "FDA Guidance",
  "SOURCE_URL": "https://www.fda.gov/guidance-documents",
  "ANYTHINGLLM_BASE_URL": "http://localhost:3001",
  "WORKSPACE_SLUG": "fda-guidance",
  "FILE_EXTENSIONS": [".pdf", ".doc"],
  "LIMIT": 50,
  "TEST_QUESTIONS": [
    "What are recent FDA guidance changes?",
    "What regulations affect medical devices?"
  ]
}
```

## 🔧 Requirements

- **Python 3.7+**
- **AnythingLLM instance** with API access
- **Internet connection** for web scraping

## 📋 Supported File Types

- PDF (`.pdf`)
- Microsoft Word (`.doc`, `.docx`) 
- Text files (`.txt`)
- HTML pages (`.html`, `.htm`)
- Custom extensions via configuration

## 🎯 How It Works

1. **Web Scraping** - Uses BeautifulSoup to find document links
2. **Smart Downloads** - Respects rate limits and avoids duplicates
3. **AnythingLLM Integration** - Uploads via API with proper folder structure
4. **Embedding Process** - Moves documents to workspace for AI processing
5. **Verification** - Tests knowledge base with domain-specific questions

## 🔍 Debugging Websites

Use the debugger to understand any website structure:

```bash
python web_page_debugger.py
```

This will show you:
- Available document links
- Page structure and content
- Recommendations for scraping approach

## 🤝 Contributing

This framework is designed to be extensible! Contributions welcome for:

- New website-specific scrapers
- Additional file format support
- Enhanced anti-detection features
- GUI interface
- Scheduled automation

## 📜 License

MIT License - Use freely for personal and commercial projects

## 🙏 Acknowledgments

- Built for integration with [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm)
- Inspired by the need for accessible AI knowledge bases
- Special thanks to the open-source community

## 📞 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Share use cases and get help in GitHub Discussions
- **Wiki**: Check the Wiki for detailed guides and troubleshooting

---

**Made with ❤️ for the AI and knowledge management community**

⭐ **Star this repo** if you find it useful!
