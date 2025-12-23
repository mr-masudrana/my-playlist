import requests
import re
import time

# কনফিগারেশন
BASE_URL = "http://tv.roarzone.info/"
OUTPUT_FILE = "playlist.m3u"

# ব্রাউজারের মতো আচরণ করার জন্য হেডার
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": BASE_URL
}

def get_channel_links():
    """মেইন পেজ থেকে সব চ্যানেলের লিংক খুঁজে বের করবে"""
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            # এখানে আমরা ধরে নিচ্ছি চ্যানেলগুলোর লিংক নির্দিষ্ট প্যাটার্নে আছে
            # প্রয়োজনে সাইটের HTML স্ট্রাকচার অনুযায়ী regex বা logic বদলাতে হতে পারে
            # উদাহরণস্বরূপ আমরা সব href খুঁজছি যা চ্যানেলের পেজে যায়
            links = re.findall(r'href=["\'](.*?/edge\d+/.*?)["\']', response.text)
            # যদি সরাসরি লিংক না পাওয়া যায়, তবে ম্যানুয়ালি কিছু চ্যানেলের লিস্ট রাখা ভালো
            # অথবা সাইটের বর্তমান HTML দেখে এই লজিক আপডেট করতে হবে
            return list(set(links)) # ডুপ্লিকেট রিমুভ করা
    except Exception as e:
        print(f"Error fetching main page: {e}")
    return []

def extract_m3u8(channel_url):
    """চ্যানেল পেজ থেকে টোকেনসহ m3u8 লিংক বের করবে"""
    try:
        full_url = channel_url if channel_url.startswith("http") else BASE_URL + channel_url
        response = requests.get(full_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            # Regex দিয়ে m3u8 লিংক খোঁজা হচ্ছে
            match = re.search(r'(https?://[^\s"\'<>]+?\.m3u8\?token=[^\s"\']+)', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error extracting from {channel_url}: {e}")
    return None

def generate_playlist():
    print("Scanning for channels...")
    
    # নোট: যদি অটোমেটিক চ্যানেল ডিটেকশন কাজ না করে, আপনি এখানে ম্যানুয়ালি চ্যানেলের নামের লিস্ট দিতে পারেন
    # উদাহরণ হিসেবে আমরা কিছু কমন চ্যানেল ম্যানুয়ালি চেক করার কোড দিচ্ছি, 
    # কারণ Roarzone এর হোমপেজ স্ক্র্যাপ করা অনেক সময় জটিল হতে পারে।
    
    # আপাতত আমরা উদাহরণ হিসেবে একটি চ্যানেল চেক করি (আপনি লুপ চালাতে পারেন)
    # আপনি চাইলে এখানে চ্যানেলের স্লাগ (slug) গুলোর একটি লিস্ট তৈরি করে লুপ চালাতে পারেন
    channel_slugs = [
        "somoy-tv", "gtv", "jamuna-tv", "independent-tv", "star-sports-1", "ten-sports" 
        # এখানে আপনার পছন্দের চ্যানেলের URL-এর শেষ অংশ যোগ করুন
    ]
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        for slug in channel_slugs:
            # Roarzone এর লিংকের প্যাটার্ন অনুযায়ী ইউআরএল তৈরি
            # লক্ষ্য করুন: সাইটের লিংক স্ট্রাকচার চেক করে নেবেন
            # ধরে নিচ্ছি লিংক এমন: http://tv.roarzone.info/somoy-tv
            target_url = BASE_URL + slug 
            
            print(f"Processing: {slug}...")
            m3u8_link = extract_m3u8(target_url)
            
            if m3u8_link:
                # চ্যানেলের নাম সুন্দর করে লেখা
                channel_name = slug.replace("-", " ").upper()
                f.write(f'#EXTINF:-1 group-title="BD Live", {channel_name}\n')
                f.write(f'{m3u8_link}\n')
            else:
                print(f"Failed to get link for {slug}")
            
            time.sleep(1) # সার্ভারে চাপ না দেওয়ার জন্য ১ সেকেন্ড বিরতি

    print(f"Playlist generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_playlist()
  
