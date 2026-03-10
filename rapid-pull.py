import requests
import json

print("="*70)
print("INSTAGRAM SCRAPER - RapidAPI (As Per Documentation)")
print("="*70)

# RapidAPI Credentials
RAPIDAPI_KEY = "bd5904a96cmsh3edcc696733215fp1eeb5ajsne133bf560c27"
RAPIDAPI_HOST = "instagram-scraper-stable-api.p.rapidapi.com"

# Base URL
BASE_URL = "https://instagram-scraper-stable-api.p.rapidapi.com"

# ============================================================
# GET USER POSTS (with form data)
# ============================================================

def get_user_posts(username, amount=20, pagination_token=""):
    """
    Get Instagram user posts using the RapidAPI endpoint
    
    Parameters:
    - username_or_url: Instagram username or profile URL
    - amount: Number of posts to fetch (optional, default 12)
    - pagination_token: Token from previous request for pagination (optional)
    """
    
    print(f"\n{'='*70}")
    print("GET USER POSTS")
    print(f"{'='*70}")
    
    # Endpoint
    url = f"{BASE_URL}/get_ig_user_posts.php"
    
    # Form data (FORM_DATA as shown in documentation)
    payload = {
        "username_or_url": username,
        "amount": str(amount),
    }
    
    # Add pagination token if provided
    if pagination_token:
        payload["pagination_token"] = pagination_token
    
    # Headers
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"\n🔍 Target: {username}")
    print(f"📊 Posts to fetch: {amount}")
    print(f"📡 Endpoint: {url}\n")
    
    print("📋 Form Data:")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        print("📥 Making request...\n")
        
        response = requests.post(url, data=payload, headers=headers)
        
        print(f"✅ Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            print("="*70)
            print("✅ RESPONSE DATA")
            print("="*70 + "\n")
            
            # Check for errors
            if 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return None
            
            # Display posts
            if 'posts' in data:
                posts = data['posts']
                print(f"✅ Found {len(posts)} posts!\n")
                
                for i, post in enumerate(posts[:5], 1):
                    print(f"📸 Post {i}:")
                    print(f"   ID: {post.get('id', 'N/A')}")
                    print(f"   Caption: {post.get('caption', 'N/A')[:60]}...")
                    print(f"   Likes: {post.get('likes', 'N/A')}")
                    print(f"   Comments: {post.get('comments', 'N/A')}")
                    print(f"   Date: {post.get('timestamp', 'N/A')}")
                    print(f"   Media: {post.get('media_url', 'N/A')[:50]}...")
                    print()
                
                # Check for pagination
                if 'pagination_token' in data:
                    print(f"📄 Pagination Token: {data['pagination_token']}")
                    print(f"   Use this to fetch more posts\n")
                
                # Save to file
                filename = f"{username}_posts.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✅ Saved to: {filename}")
                return data
            
            # Display user info
            elif 'user' in data:
                user = data['user']
                
                print("✅ USER INFORMATION")
                print(f"  Username: {user.get('username', 'N/A')}")
                print(f"  Followers: {user.get('followers', 'N/A')}")
                print(f"  Posts: {user.get('posts', 'N/A')}")
                
                return data
            
            else:
                print("📋 Full Response:")
                print(json.dumps(data, indent=2)[:1000])
                return data
        
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Could not parse JSON response")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================
# GET USER INFO
# ============================================================

def get_user_info(username):
    """Get user profile information"""
    
    print(f"\n{'='*70}")
    print("GET USER INFO")
    print(f"{'='*70}")
    
    url = f"{BASE_URL}/get_ig_user_info.php"
    
    payload = {
        "username_or_url": username,
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"\n🔍 Target: {username}")
    print(f"📡 Endpoint: {url}\n")
    
    try:
        print("📥 Making request...\n")
        
        response = requests.post(url, data=payload, headers=headers)
        
        print(f"✅ Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return None
            
            if 'user' in data:
                user = data['user']
                
                print("="*70)
                print("✅ USER PROFILE INFORMATION")
                print("="*70)
                print(f"\n📱 Username:      {user.get('username', 'N/A')}")
                print(f"👤 Full Name:     {user.get('full_name', 'N/A')}")
                print(f"📝 Bio:           {user.get('biography', 'N/A')}")
                print(f"📊 FOLLOWERS:     {user.get('followers', 'N/A')}")
                print(f"👥 Following:     {user.get('following', 'N/A')}")
                print(f"📸 Posts:         {user.get('posts', 'N/A')}")
                print(f"🌐 Website:       {user.get('website', 'N/A')}")
                print(f"✓ Verified:       {'Yes ✔️' if user.get('is_verified') else 'No'}")
                print(f"🔒 Private:       {'Yes' if user.get('is_private') else 'No (Public)'}")
                print(f"🖼️  Profile Pic:   {user.get('profile_pic_url', 'N/A')[:50]}...")
                print(f"📍 Location:      {user.get('location', 'N/A')}")
                
                print("\n" + "="*70)
                
                # Save
                filename = f"{username}_info.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"\n✅ Saved to: {filename}")
                return data
            
            else:
                print("Response:")
                print(json.dumps(data, indent=2))
                return data
        
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    
    import time
    
    print(f"\n🎯 Instagram Scraper using RapidAPI")
    print(f"🔑 Using your API key\n")
    
    # Target profile
    target_username = "festivebreadke"
    target_url = f"https://www.instagram.com/{target_username}/"
    
    # ============================================================
    # REQUEST 1: Get user info
    # ============================================================
    
    print("\n" + "#"*70)
    print("# REQUEST 1: GET USER PROFILE INFO")
    print("#"*70)
    
    user_info = get_user_info(target_username)
    
    time.sleep(2)
    
    # ============================================================
    # REQUEST 2: Get user posts
    # ============================================================
    
    print("\n" + "#"*70)
    print("# REQUEST 2: GET USER POSTS")
    print("#"*70)
    
    posts = get_user_posts(target_username, amount=20)
    
    # ============================================================
    # Summary
    # ============================================================
    
    print("\n" + "="*70)
    print("✅ REQUESTS COMPLETE!")
    print("="*70)
    
    if user_info and 'user' in user_info:
        user = user_info['user']
        print(f"\n📊 Summary:")
        print(f"   Username: {user.get('username')}")
        print(f"   Followers: {user.get('followers'):,}")
        print(f"   Posts: {user.get('posts'):,}")
    
    if posts and 'posts' in posts:
        print(f"   Posts Retrieved: {len(posts['posts'])}")
    
    print("\n" + "="*70)