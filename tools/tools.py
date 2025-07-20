import os
import time
import re
from firecrawl import FirecrawlApp

def get_laravel_docs(urls=None, delay=2):
    """Extract content from Laravel docs using Firecrawl with rate limiting."""
    if urls is None:
        base_url = "https://laravel.com"
        sidebar_paths = [
            "/docs/12.x/releases",
            "/docs/12.x/upgrade",
            "/docs/12.x/contributions",
            "/docs/12.x/installation",
            "/docs/12.x/configuration",
            "/docs/12.x/structure",
            "/docs/12.x/frontend",
            "/docs/12.x/starter-kits",
            "/docs/12.x/deployment",
            "/docs/12.x/lifecycle",
            "/docs/12.x/container",
            "/docs/12.x/providers",
            "/docs/12.x/facades",
            "/docs/12.x/routing",
            "/docs/12.x/middleware",
            "/docs/12.x/csrf",
            "/docs/12.x/controllers",
            "/docs/12.x/requests",
            "/docs/12.x/responses",
            "/docs/12.x/views",
            "/docs/12.x/blade",
            "/docs/12.x/vite",
            "/docs/12.x/urls",
            "/docs/12.x/session",
            "/docs/12.x/validation",
            "/docs/12.x/errors",
            "/docs/12.x/logging",
            "/docs/12.x/artisan",
            "/docs/12.x/broadcasting",
            "/docs/12.x/cache",
            "/docs/12.x/collections",
            "/docs/12.x/concurrency",
            "/docs/12.x/context",
            "/docs/12.x/contracts",
            "/docs/12.x/events",
            "/docs/12.x/filesystem",
            "/docs/12.x/helpers",
            "/docs/12.x/http-client",
            "/docs/12.x/localization",
            "/docs/12.x/mail",
            "/docs/12.x/notifications",
            "/docs/12.x/packages",
            "/docs/12.x/processes",
            "/docs/12.x/queues",
            "/docs/12.x/rate-limiting",
            "/docs/12.x/strings",
            "/docs/12.x/scheduling",
            "/docs/12.x/authentication",
            "/docs/12.x/authorization",
            "/docs/12.x/verification",
            "/docs/12.x/encryption",
            "/docs/12.x/hashing",
            "/docs/12.x/passwords",
            "/docs/12.x/database",
            "/docs/12.x/queries",
            "/docs/12.x/pagination",
            "/docs/12.x/migrations",
            "/docs/12.x/seeding",
            "/docs/12.x/redis",
            "/docs/12.x/mongodb",
            "/docs/12.x/eloquent",
            "/docs/12.x/eloquent-relationships",
            "/docs/12.x/eloquent-collections",
            "/docs/12.x/eloquent-mutators",
            "/docs/12.x/eloquent-resources",
            "/docs/12.x/eloquent-serialization",
            "/docs/12.x/eloquent-factories",
            "/docs/12.x/testing",
            "/docs/12.x/http-tests",
            "/docs/12.x/console-tests",
            "/docs/12.x/dusk",
            "/docs/12.x/database-testing",
            "/docs/12.x/mocking",
            "/docs/12.x/billing",
            "/docs/12.x/cashier-paddle",
            "/docs/12.x/dusk",
            "/docs/12.x/envoy",
            "/docs/12.x/fortify",
            "/docs/12.x/folio",
            "/docs/12.x/homestead",
            "/docs/12.x/horizon",
            "/docs/12.x/mix",
            "/docs/12.x/octane",
            "/docs/12.x/passport",
            "/docs/12.x/pennant",
            "/docs/12.x/pint",
            "/docs/12.x/precognition",
            "/docs/12.x/prompts",
            "/docs/12.x/pulse",
            "/docs/12.x/reverb",
            "/docs/12.x/sail",
            "/docs/12.x/sanctum",
            "/docs/12.x/scout",
            "/docs/12.x/socialite",
            "/docs/12.x/telescope",
            "/docs/12.x/valet",
        ]
        urls = [f"{base_url}{path}" for path in sidebar_paths]
    
    api_key = os.getenv('FIRECRAWL_API_KEY')
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
    
    app = FirecrawlApp(api_key=api_key)
    contents = []
    
    for i, url in enumerate(urls):
        # Add delay between requests to avoid rate limiting
        if i > 0:
            print(f"  ⏳ Waiting {delay} seconds to avoid rate limits...")
            time.sleep(delay)
        
        try:
            print(f"Scraping {url} with Firecrawl...")
            result = app.scrape_url(
                url,
                formats=['markdown'],
                only_main_content=True
            )
            
            if hasattr(result, 'success') and result.success:
                if hasattr(result, 'markdown') and result.markdown:
                    content = result.markdown
                    contents.append(content)
                    print(f"  ✅ Extracted {len(content)} characters (markdown)")
                elif hasattr(result, 'html') and result.html:
                    # Fallback to HTML if markdown not available
                    content = result.html
                    contents.append(content)
                    print(f"  ✅ Extracted {len(content)} characters (html)")
                else:
                    print(f"  ⚠️ No markdown or html content found")
            else:
                if hasattr(result, 'error'):
                    print(f"  ❌ Scraping failed: {result.error}")
                else:
                    print(f"  ❌ Scraping failed: success={getattr(result, 'success', 'unknown')}")
                
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and "Rate limit exceeded" in error_str:
                # Extract retry delay from error message
                retry_delay = extract_retry_delay(error_str)
                print(f"  ⏳ Rate limit hit! Waiting {retry_delay} seconds before retrying...")
                time.sleep(retry_delay + 1)  # Add 1 second buffer
                
                # Retry the request
                try:
                    print(f"  🔄 Retrying {url}...")
                    result = app.scrape_url(
                        url,
                        formats=['markdown'],
                        only_main_content=True
                    )
                    
                    if hasattr(result, 'success') and result.success:
                        if hasattr(result, 'markdown') and result.markdown:
                            content = result.markdown
                            contents.append(content)
                            print(f"  ✅ Retry successful! Extracted {len(content)} characters")
                        elif hasattr(result, 'html') and result.html:
                            content = result.html
                            contents.append(content)
                            print(f"  ✅ Retry successful! Extracted {len(content)} characters")
                    else:
                        print(f"  ❌ Retry failed")
                except Exception as retry_error:
                    print(f"  ❌ Retry failed: {retry_error}")
            else:
                print(f"  ❌ Error scraping {url}: {e}")
                continue
    
    return contents


def extract_retry_delay(error_message):
    """Extract retry delay from Firecrawl error message."""
    # Look for patterns like "retry after 32s" or "32s"
    match = re.search(r'retry after (\d+)s', error_message)
    if match:
        return int(match.group(1))
    
    match = re.search(r'(\d+)s,', error_message)
    if match:
        return int(match.group(1))
    
    # Default fallback
    return 35


def get_laravel_documentation_pages():
    """Extract content from multiple Laravel documentation pages with rate limiting."""
    urls = [
        # Core documentation pages with actual content
        "https://laravel.com/docs/12.x/installation",
        "https://laravel.com/docs/12.x/configuration",
        "https://laravel.com/docs/12.x/routing",
        "https://laravel.com/docs/12.x/middleware",
        "https://laravel.com/docs/12.x/controllers",
        "https://laravel.com/docs/12.x/requests",
        "https://laravel.com/docs/12.x/responses",
        "https://laravel.com/docs/12.x/views",
        "https://laravel.com/docs/12.x/blade",
        "https://laravel.com/docs/12.x/eloquent",
        "https://laravel.com/docs/12.x/eloquent-relationships",
        "https://laravel.com/docs/12.x/eloquent-collections",
        "https://laravel.com/docs/12.x/eloquent-mutators",
        "https://laravel.com/docs/12.x/migrations",
        "https://laravel.com/docs/12.x/seeding",
        "https://laravel.com/docs/12.x/queries",
        "https://laravel.com/docs/12.x/validation",
        "https://laravel.com/docs/12.x/authentication",
        "https://laravel.com/docs/12.x/authorization",
        "https://laravel.com/docs/12.x/artisan",
        "https://laravel.com/docs/12.x/testing",
        "https://laravel.com/docs/12.x/filesystem",
        "https://laravel.com/docs/12.x/mail",
        "https://laravel.com/docs/12.x/notifications",
        "https://laravel.com/docs/12.x/queues",
        "https://laravel.com/docs/12.x/scheduling",
    ]
    
    print(f"📥 Extracting from {len(urls)} Laravel documentation pages...")
    print("⏳ Using 3-second delays between requests to respect rate limits...")
    
    # Use the rate-limited extraction with 3-second delays
    all_contents = get_laravel_docs(urls, delay=3)
    
    print(f"\n📊 Extraction Summary:")
    print(f"  • Total pages attempted: {len(urls)}")
    print(f"  • Successfully extracted: {len(all_contents)} documents")
    print(f"  • Total content size: {sum(len(content) for content in all_contents):,} characters")
    
    return all_contents


def get_laravel_documentation_pages_batch(batch_size=5):
    """Extract Laravel docs in smaller batches to avoid rate limits."""
    all_urls = [
        "https://laravel.com/docs/12.x/installation",
        "https://laravel.com/docs/12.x/configuration", 
        "https://laravel.com/docs/12.x/routing",
        "https://laravel.com/docs/12.x/middleware",
        "https://laravel.com/docs/12.x/controllers",
        "https://laravel.com/docs/12.x/requests",
        "https://laravel.com/docs/12.x/responses",
        "https://laravel.com/docs/12.x/views",
        "https://laravel.com/docs/12.x/blade",
        "https://laravel.com/docs/12.x/eloquent",
        "https://laravel.com/docs/12.x/eloquent-relationships",
        "https://laravel.com/docs/12.x/eloquent-collections",
        "https://laravel.com/docs/12.x/eloquent-mutators",
        "https://laravel.com/docs/12.x/migrations",
        "https://laravel.com/docs/12.x/seeding",
        "https://laravel.com/docs/12.x/queries",
        "https://laravel.com/docs/12.x/validation",
        "https://laravel.com/docs/12.x/authentication",
        "https://laravel.com/docs/12.x/authorization",
        "https://laravel.com/docs/12.x/artisan",
        "https://laravel.com/docs/12.x/testing",
        "https://laravel.com/docs/12.x/filesystem",
        "https://laravel.com/docs/12.x/mail",
        "https://laravel.com/docs/12.x/notifications",
        "https://laravel.com/docs/12.x/queues",
        "https://laravel.com/docs/12.x/scheduling",
    ]
    
    all_contents = []
    total_batches = (len(all_urls) + batch_size - 1) // batch_size
    
    print(f"📥 Extracting {len(all_urls)} pages in {total_batches} batches of {batch_size}")
    
    for i in range(0, len(all_urls), batch_size):
        batch_urls = all_urls[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch_urls)} pages)")
        
        batch_contents = get_laravel_docs(batch_urls, delay=4)
        all_contents.extend(batch_contents)
        
        # Wait longer between batches
        if i + batch_size < len(all_urls):
            print(f"⏳ Waiting 10 seconds before next batch...")
            time.sleep(10)
    
    print(f"\n📊 Final Summary:")
    print(f"  • Total pages processed: {len(all_urls)}")
    print(f"  • Successfully extracted: {len(all_contents)} documents")
    print(f"  • Total content size: {sum(len(content) for content in all_contents):,} characters")
    
    return all_contents


def clean_and_filter_content(contents):
    """Clean and filter extracted content to remove navigation and improve quality."""
    cleaned_contents = []
    
    for content in contents:
        # Skip short content (likely navigation)
        if len(content.strip()) < 200:
            continue
            
        # Skip content that's mostly navigation links
        lines = content.split('\n')
        link_count = sum(1 for line in lines if 'https://' in line or '[' in line and '](' in line)
        total_lines = len([line for line in lines if line.strip()])
        
        if total_lines > 0 and (link_count / total_lines) > 0.7:
            continue  # Skip if more than 70% of lines are links
            
        cleaned_contents.append(content)
    
    return cleaned_contents
