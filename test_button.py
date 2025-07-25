import requests
from bs4 import BeautifulSoup
import time

# Give dashboard time to start
time.sleep(2)

try:
    response = requests.get("http://localhost:8050/")
    if response.status_code == 200:
        # Check if the AI Assistant button text is in the response
        if "AI Assistant" in response.text:
            print("✅ AI Assistant button found in HTML!")
        else:
            print("❌ AI Assistant button NOT found in HTML")
            
        # Parse HTML to find the button
        soup = BeautifulSoup(response.text, 'html.parser')
        buttons = soup.find_all('button')
        print(f"\nFound {len(buttons)} buttons total:")
        for i, button in enumerate(buttons):
            print(f"  Button {i+1}: {button.get_text().strip()[:50]}")
            
except Exception as e:
    print(f"Error: {e}")