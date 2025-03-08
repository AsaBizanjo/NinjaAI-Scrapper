MyNinja.AI OpenAI-Compatible API
================================

This project provides an OpenAI-compatible API wrapper for MyNinja.AI, allowing you to use MyNinja.AI's capabilities through the familiar OpenAI API interface.

**Created by:** Asa Bizanjo

Features
--------

*   OpenAI-compatible API endpoints
*   Support for streaming responses
*   Automatic session management
*   Headless browser automation
*   Health check and reset endpoints

Installation
------------

### Prerequisites

*   Python 3.8+
*   Google Chrome browser
*   A MyNinja.AI account

### Setup

    
    # Clone the repository (if applicable)
    git clone https://github.com/yourusername/myninja-openai-api.git
    cd myninja-openai-api
    
    # Create a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install dependencies
    pip install flask selenium webdriver-manager
        

### Configuration

Edit the following line in the code to match your Chrome profile path:

    user_data_dir = os.path.expanduser(r"C:\Users\asa21\AppData\Local\Google\Chrome\User Data")

Make sure to replace this with your own Chrome user data directory path.

**Note:** The API uses your existing Chrome profile to access MyNinja.AI. Make sure you're already logged in to MyNinja.AI in this Chrome profile.

Usage
-----

### Starting the API Server

    python api_server.py

The server will start on `http://localhost:5000` by default.

### API Endpoints

#### Chat Completions

    POST /v1/chat/completions

This endpoint is compatible with OpenAI's chat completions API. Example request:

    
    {
      "model": "myninja-ai",
      "messages": [
        {"role": "user", "content": "Tell me a joke about programming"}
      ],
      "stream": false
    }
        

#### Health Check

    GET /health

Returns the current status of the API and browser.

#### Reset

    POST /reset

Resets the browser session. Useful if you encounter issues.

### Using with OpenAI Python Client

    
    import openai
    
    # Configure the client to use your local API
    client = openai.OpenAI(
        base_url="http://localhost:5000/v1",
        api_key="dummy-key"  # API key is required but not used
    )
    
    # Non-streaming request
    response = client.chat.completions.create(
        model="myninja-ai",  # Model name doesn't matter
        messages=[
            {"role": "user", "content": "Tell me a joke about programming"}
        ]
    )
    print(response.choices[0].message.content)
    
    # Streaming request
    stream = client.chat.completions.create(
        model="myninja-ai",
        messages=[
            {"role": "user", "content": "Tell me a joke about programming"}
        ],
        stream=True
    )
    
    # Process the streaming response
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)  # Print each chunk as it arrives
    
    print("\n\nFull response:", full_response)
        

Troubleshooting
---------------

**Common Issues:**

*   **Chrome crashes:** If Chrome keeps crashing, try using the `/reset` endpoint and restart the server. Make sure no other Chrome instances are using the same profile.
*   **Authentication issues:** Ensure you're logged into MyNinja.AI in the Chrome profile you're using.
*   **Selector errors:** If the website structure changes, the CSS selectors may need to be updated.

Limitations
-----------

*   Only one request can be processed at a time due to the single browser instance
*   The API depends on the MyNinja.AI web interface, so it may break if their interface changes
*   Token counting is not supported (returns -1 for token counts)
*   Some OpenAI API parameters are ignored

License
-------

This project is for educational purposes only. Use responsibly and in accordance with MyNinja.AI's terms of service.

Created by Asa Bizanjo © 2025