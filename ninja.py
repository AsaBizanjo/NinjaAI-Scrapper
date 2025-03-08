from flask import Flask, request, Response, jsonify, stream_with_context
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import threading
import queue
import json
import uuid
import os

app = Flask(__name__)


driver = None
driver_lock = threading.Lock()
is_initialized = False

def initialize_driver():
    global driver, is_initialized
    
    if is_initialized and driver:
        try:
            
            driver.title
            return
        except:
            
            try:
                driver.quit()
            except:
                pass
            driver = None
            is_initialized = False
    
    options = Options()
    
    
    user_data_dir = os.path.expanduser(r"C:\Users\asa21\AppData\Local\Google\Chrome\User Data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Profile 1")
    
    
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-extensions")  
    options.add_argument("--disable-software-rasterizer")
    
    
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    
    service = Service(ChromeDriverManager().install())
    
    print("Initializing Chrome in headless mode...")
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            
            
            driver.set_page_load_timeout(30)
            driver.get("https://myninja.ai")
            print("Waiting for page to load...")
            time.sleep(5)  
            
            print(f"Current URL: {driver.current_url}")
            is_initialized = True
            break
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_attempts} failed: {str(e)}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None
            
            if attempt == max_attempts - 1:
                raise Exception(f"Failed to initialize Chrome after {max_attempts} attempts")
            
            time.sleep(2)  

def start_new_chat():
    """Click the New Chat button to start a fresh conversation"""
    try:
        wait = WebDriverWait(driver, 10)
        new_chat_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '.nj-create-new-chat--button')))
        new_chat_button.click()
        print("Started a new chat")
        time.sleep(2)  
        return True
    except Exception as e:
        print(f"Error starting new chat: {e}")
        return False

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    global driver
    
    
    data = request.json
    
    
    messages = data.get('messages', [])
    stream = data.get('stream', False)
    
    
    user_message = None
    for msg in reversed(messages):
        if msg.get('role') == 'user':
            user_message = msg.get('content')
            break
    
    if not user_message:
        return jsonify({
            "error": {
                "message": "No user message found in the request",
                "type": "invalid_request_error"
            }
        }), 400
    
    
    with driver_lock:
        try:
            initialize_driver()
        except Exception as e:
            return jsonify({
                "error": {
                    "message": f"Failed to initialize browser: {str(e)}",
                    "type": "server_error"
                }
            }), 500
    
    
    completion_id = f"chatcmpl-{uuid.uuid4()}"
    created_time = int(time.time())
    
    
    if stream:
        def generate():
            response_queue = queue.Queue()
            
            def process_message():
                try:
                    with driver_lock:
                        wait = WebDriverWait(driver, 20)
                        
                        
                        text_area = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.ThreadInputBox_textArea__caqN\\+')))
                        text_area.click()
                        text_area.clear()
                        
                        
                        text_area.send_keys(user_message)
                        text_area.send_keys(Keys.RETURN)
                        
                        
                        response_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Markdown_root__oIhik')))
                        
                        
                        previous_text = ""
                        unchanged_count = 0
                        max_unchanged = 5
                        
                        
                        response_queue.put({
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": "myninja-ai",
                            "choices": [{
                                "index": 0,
                                "delta": {
                                    "role": "assistant"
                                },
                                "finish_reason": None
                            }]
                        })
                        
                        while unchanged_count < max_unchanged:
                            current_text = response_element.text
                            
                            if current_text != previous_text:
                                if len(previous_text) == 0:
                                    
                                    chunk = current_text
                                else:
                                    
                                    chunk = current_text[len(previous_text):]
                                
                                
                                response_queue.put({
                                    "id": completion_id,
                                    "object": "chat.completion.chunk",
                                    "created": created_time,
                                    "model": "myninja-ai",
                                    "choices": [{
                                        "index": 0,
                                        "delta": {
                                            "content": chunk
                                        },
                                        "finish_reason": None
                                    }]
                                })
                                
                                unchanged_count = 0
                                previous_text = current_text
                            else:
                                unchanged_count += 1
                            
                            time.sleep(0.1)
                        
                        
                        try:
                            start_new_chat()
                        except:
                            
                            pass
                        
                        
                        response_queue.put({
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created_time,
                            "model": "myninja-ai",
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop"
                            }]
                        })
                
                except Exception as e:
                    response_queue.put({
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": "myninja-ai",
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "error"
                        }],
                        "error": {
                            "message": str(e),
                            "type": "server_error"
                        }
                    })
            
            
            thread = threading.Thread(target=process_message)
            thread.daemon = True
            thread.start()
            
            
            while True:
                try:
                    data = response_queue.get(timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    
                    if data.get("choices", [{}])[0].get("finish_reason") is not None:
                        break
                except queue.Empty:
                    error_data = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": "myninja-ai",
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "error"
                        }],
                        "error": {
                            "message": "Timeout waiting for response",
                            "type": "server_error"
                        }
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    break
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    
    else:
        try:
            with driver_lock:
                wait = WebDriverWait(driver, 20)
                
                
                text_area = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.ThreadInputBox_textArea__caqN\\+')))
                text_area.click()
                text_area.clear()
                
                
                text_area.send_keys(user_message)
                text_area.send_keys(Keys.RETURN)
                
                
                response_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Markdown_root__oIhik')))
                
                
                previous_text = ""
                unchanged_count = 0
                max_unchanged = 5
                
                while unchanged_count < max_unchanged:
                    current_text = response_element.text
                    
                    if current_text != previous_text:
                        unchanged_count = 0
                        previous_text = current_text
                    else:
                        unchanged_count += 1
                    
                    time.sleep(0.1)
                
                
                try:
                    start_new_chat()
                except:
                    
                    pass
                
                
                                
                return jsonify({
                    "id": completion_id,
                    "object": "chat.completion",
                    "created": created_time,
                    "model": "myninja-ai",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": current_text
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": -1,  
                        "completion_tokens": -1,
                        "total_tokens": -1
                    }
                })
                
        except Exception as e:
            return jsonify({
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }), 500

@app.route('/health', methods=['GET'])
def health_check():
    global driver
    
    status = "ok"
    browser_status = "not_initialized"
    
    if is_initialized:
        try:
            if driver:
                driver.title  
                browser_status = "responsive"
            else:
                browser_status = "driver_missing"
        except:
            browser_status = "not_responsive"
    
    return jsonify({
        "status": status,
        "browser_status": browser_status,
        "initialized": is_initialized
    })

@app.route('/reset', methods=['POST'])
def reset():
    global driver, is_initialized
    
    with driver_lock:
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
        is_initialized = False
    
    return jsonify({"status": "reset successful"})

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
