import requests

# 1. Setup your credentials
handle = "matrixking1.bsky.social"
app_password = "flame86362"  # It is safer to use an App Password!
base_url = "https://bsky.social/xrpc"

# 2. Create a Session (Login)

class BleuSkyService:
    def get_access_token():
        print("Authenticating...")
        resp = requests.post(
            f"{base_url}/com.atproto.server.createSession",
            json={"identifier": handle, "password": app_password}
        )
        resp.raise_for_status()
        return resp.json()["accessJwt"]

    # 3. Search for Posts
    def search_posts(token, query):
        print(f"Searching for: {query}...")
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "q": query,
            "lang": "en",
            "limit": 10
        }
        
        # We use the public API endpoint for search as it's optimized for it
        search_url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
        
        resp = requests.get(search_url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json().get("posts", [])

    # --- Execute ---
    def get_posts(self):
        try:
            jwt = self.get_access_token()
            results = self.search_posts(jwt, "epstein")

            for post in results:
                author = post['author']['handle']
                text = post['record']['text']
                print(f"[@{author}]: {text}\n{'-'*40}")

        except Exception as e:
            print(f"Error occurred: {e}")