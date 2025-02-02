import requests

def api_call(url, method, endpoint, auth=None, headers=None, payload=None):
    """Generic function to make API calls."""
    full_url = f"{url}{endpoint}"
    
    if method == "GET":
        response = requests.get(full_url, auth=auth, headers=headers)
    elif method == "POST":
        response = requests.post(full_url, json=payload, auth=auth, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method")
    
    return response