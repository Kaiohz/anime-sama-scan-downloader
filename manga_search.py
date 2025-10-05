import httpx
import re
from typing import List
from scan_downloader import scan_downloader


def search_anime_manga(query: str) -> List[str]:
    """
    Search for anime/manga on anime-sama.fr and extract the names from the results.
    
    Args:
        query (str): The search term to look for
        
    Returns:
        List[str]: A list of manga/anime names found in the search results
    """
    reset_cookie_url = "https://anime-sama.fr/"
    url = "https://anime-sama.fr/template-php/defaut/fetch.php"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://anime-sama.fr',
        'priority': 'u=1, i',
        'referer': 'https://anime-sama.fr/catalogue/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        'query': query
    }
    
    try:
        with httpx.Client() as client:
            # Initial request to reset cookies
            client.get(reset_cookie_url, headers=headers)
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            # Extract manga names from the HTML response
            return extract_manga_names(response.text)
            
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
        return []


def search_anime_manga_normalized(query: str) -> List[str]:
    """
    Search for anime/manga on anime-sama.fr and extract the normalized names from URLs.
    
    Args:
        query (str): The search term to look for
        
    Returns:
        List[str]: A list of normalized manga/anime names from URLs (e.g., 'hajime-no-ippo')
    """
    url = "https://anime-sama.fr/template-php/defaut/fetch.php"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://anime-sama.fr',
        'priority': 'u=1, i',
        'referer': 'https://anime-sama.fr/catalogue/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        'query': query
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            # Extract normalized names from the HTML response
            return extract_normalized_names(response.text)
            
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
        return []


def extract_manga_names(html_content: str) -> List[str]:
    """
    Extract manga names from the HTML response.
    
    Args:
        html_content (str): The HTML content from the search response
        
    Returns:
        List[str]: A list of extracted manga names
    """
    # Pattern to match the italic text within <p class="text-xs truncate opacity-70 italic mt-1">
    pattern = r'<p class="text-xs truncate opacity-70 italic mt-1">(.*?)</p>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    # Clean up the extracted names (remove extra whitespace and HTML entities)
    manga_names = []
    for match in matches:
        # Remove any remaining HTML tags and clean whitespace
        clean_name = re.sub(r'<[^>]+>', '', match).strip()
        if clean_name:
            manga_names.append(clean_name)
    
    return manga_names


def extract_normalized_names(html_content: str) -> List[str]:
    """
    Extract normalized manga names from the URLs in the HTML response.
    
    Args:
        html_content (str): The HTML content from the search response
        
    Returns:
        List[str]: A list of normalized manga names from URLs (e.g., 'hajime-no-ippo')
    """
    # Pattern to match href attributes in the <a> tags
    pattern = r'href="https://anime-sama\.fr/catalogue/([^"]+)"'
    matches = re.findall(pattern, html_content)
    
    # Return unique normalized names
    return list(set(matches))


def search_all_anime_manga() -> List[str]:
    """
    Search for all anime/manga in the catalog by using various search strategies.
    
    Returns:
        List[str]: A list of all manga/anime names in the catalog
    """
    # Try different approaches to get all results
    all_names = set()
    
    # Common letters, numbers, and terms that might return broad results
    search_terms = [
        '', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'the', 'no', 'de', 'la', 'le', 'ni', 'ga', 'wa', 'wo', 'to',
        'anime', 'manga', 'san', 'kun', 'chan', 'sama'
    ]
    
    print(f"Searching with {len(search_terms)} different terms...")
    
    for i, term in enumerate(search_terms, 1):
        print(f"Progress: {i}/{len(search_terms)} - Searching '{term}'...")
        names = search_anime_manga(term)
        if names:
            all_names.update(names)
            print(f"  Found {len(names)} new results")
    
    return sorted(list(all_names))


def search_all_anime_manga_normalized() -> List[str]:
    """
    Search for all anime/manga normalized names in the catalog by using various search strategies.
    
    Returns:
        List[str]: A list of all normalized manga/anime names (URL slugs) in the catalog
    """
    # Try different approaches to get all results
    all_names = set()
    
    # Common letters, numbers, and terms that might return broad results
    search_terms = [
        '', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'the', 'no', 'de', 'la', 'le', 'ni', 'ga', 'wa', 'wo', 'to',
        'anime', 'manga', 'san', 'kun', 'chan', 'sama'
    ]
    
    print(f"Searching normalized names with {len(search_terms)} different terms...")
    
    for i, term in enumerate(search_terms, 1):
        print(f"Progress: {i}/{len(search_terms)} - Searching '{term}'...")
        names = search_anime_manga_normalized(term)
        if names:
            all_names.update(names)
            print(f"  Found {len(names)} new normalized results")
    
    return sorted(list(all_names))


def search_by_alphabet() -> List[str]:
    """
    Search systematically through the alphabet to find all anime/manga.
    
    Returns:
        List[str]: A comprehensive list of manga/anime names
    """
    import string
    import time
    
    all_names = set()
    
    # Search single letters
    for letter in string.ascii_lowercase:
        print(f"Searching for '{letter}'...")
        names = search_anime_manga(letter)
        all_names.update(names)
        time.sleep(0.1)  # Be respectful to the server
    
    # Search common two-letter combinations
    common_combinations = [
        'an', 'ar', 'at', 'er', 'he', 'in', 'it', 'on', 'or', 're', 'st', 'th',
        'no', 'ni', 'na', 'ne', 'ga', 'go', 'ka', 'ki', 'ku', 'ko', 'ma', 'mi',
        'mu', 'mo', 'sa', 'shi', 'su', 'so', 'ta', 'te', 'to', 'wa', 'wo', 'ya',
        'yu', 'yo', 'ra', 'ri', 'ru', 'ro'
    ]
    
    for combo in common_combinations:
        print(f"Searching for '{combo}'...")
        names = search_anime_manga(combo)
        all_names.update(names)
        time.sleep(0.1)  # Be respectful to the server
    
    return sorted(list(all_names))


def extract_full_info(html_content: str) -> List[dict]:
    """
    Extract full information from the HTML response including titles, descriptions, and URLs.
    
    Args:
        html_content (str): The HTML content from the search response
        
    Returns:
        List[dict]: A list of dictionaries with anime/manga information
    """
    import re
    
    results = []
    
    # Pattern to match the entire <a> tag with all information
    pattern = r'<a[^>]+href="([^"]+)"[^>]*>.*?<h3[^>]*>(.*?)</h3>.*?<p class="text-xs truncate opacity-70 italic mt-1">(.*?)</p>.*?</a>'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    for match in matches:
        url, title, description = match
        
        # Clean up the extracted data
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_description = re.sub(r'<[^>]+>', '', description).strip()
        
        results.append({
            'url': url.strip(),
            'title': clean_title,
            'description': clean_description
        })
    
    return results


def search_anime_manga_full(query: str) -> List[dict]:
    """
    Search for anime/manga and return full information including URLs.
    
    Args:
        query (str): The search term to look for
        
    Returns:
        List[dict]: A list of dictionaries with complete anime/manga information
    """
    url = "https://anime-sama.fr/template-php/defaut/fetch.php"
    
    headers = {
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://anime-sama.fr',
        'priority': 'u=1, i',
        'referer': 'https://anime-sama.fr/catalogue/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    data = {
        'query': query
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            return extract_full_info(response.text)
            
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return []
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
        return []


def interactive_search():
    """
    Interactive search function that allows user to search, see results, 
    select by index, and get the normalized name.
    """
    while True:
        # Get search query from user
        query = input("\nEnter your search term (or 'quit' to exit): ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not query:
            print("Please enter a search term.")
            continue
            
        # Perform search
        print(f"\nSearching for '{query}'...")
        full_results = search_anime_manga_full(query)
        
        if not full_results:
            print("No results found. Please try a different search term.")
            continue
            
        # Display results
        print(f"\nFound {len(full_results)} results:")
        print("=" * 60)
        for i, item in enumerate(full_results, 1):
            print(f"{i}. {item['title']}")
            print(f"   Description: {item['description']}")
            print(f"   Normalized: {item['url'].split('/')[-1]}")
            print()
        
        # Get index selection from user
        while True:
            try:
                index_input = input(f"Enter the index (1-{len(full_results)}) of your choice (or 'back' for new search): ").strip()
                
                if index_input.lower() in ['back', 'b']:
                    break
                    
                index = int(index_input)
                
                if 1 <= index <= len(full_results):
                    selected_item = full_results[index - 1]
                    normalized_name = selected_item['url'].split('/')[-1]
                    
                    print("\n" + "=" * 60)
                    print("SELECTED RESULT:")
                    print(f"Title: {selected_item['title']}")
                    print(f"Description: {selected_item['description']}")
                    print(f"Normalized Name: {normalized_name}")
                    print(f"Full URL: {selected_item['url']}")
                    print("=" * 60)

                    return selected_item['title']
                    
                else:
                    print(f"Please enter a number between 1 and {len(full_results)}")
                    
            except ValueError:
                print("Please enter a valid number or 'back'")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                return


if __name__ == "__main__":
    # Interactive search mode
    print("Welcome to Anime-Sama Interactive Search!")
    print("This tool helps you search for anime/manga and get normalized names.")
    print("-" * 60)

    max_retry = 5
    retry = 0
    manga_name = interactive_search()
    if manga_name:
        try:
            print(f"\nStarting download for '{manga_name}'...")
            scan_downloader(manga_name)
        except Exception as e:
            if retry < max_retry:
                retry += 1
                print(f"Retrying... ({retry}/{max_retry})")
                scan_downloader(manga_name)
            else:
                print("Max retries reached. Aborting.")
