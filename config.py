def load_additional_sources():
    server_url = None
    mac_address = None

    # Try to load from clipboard
    try:
        clipboard_data = pyperclip.paste()
        if clipboard_data:
            data = clipboard_data.split(',')
            if len(data) >= 2:
                server_url, mac_address = data[:2]
            else:
                print("Not enough values in clipboard data")
    except Exception as e:
        print(f"Error loading from clipboard: {e}")

    # Try to load from a file
    if not server_url or not mac_address:
        try:
            with open('server_mac.txt', 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if lines:
                    data = lines[0].strip().split(',')
                    if len(data) >= 2:
                        server_url, mac_address = data[:2]
                    else:
                        print("Not enough values in file data")
        except Exception as e:
            print(f"Error loading from file: {e}")

    # Try to load from a webpage
    if not server_url or not mac_address:
        try:
            response = requests.get('http://example.com/get_server_mac')
            if response.status_code == 200:
                data = response.text.split(',')
                if len(data) >= 2:
                    server_url, mac_address = data[:2]
                else:
                    print("Not enough values in webpage data")
        except Exception as e:
            print(f"Error loading from webpage: {e}")

    return server_url, mac_address
