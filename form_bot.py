from mistralai.client import MistralClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import argparse
from typing import Optional
import re

# Initialize Mistral client
mistral_client = MistralClient(api_key="wAdi94TD0nD7bIITfnGtyrDbeRXvjswf")

# Add this list of authorized emails
AUTHORIZED_EMAILS = [
    "2024pietcabhavishya009@poornima.org",
    "example2@gmail.com",
    # Add more authorized emails here
]

def print_banner():
    banner = """
    ███╗   ███╗ █████╗ ██████╗ ███████╗    ██████╗ ██╗   ██╗
    ████╗ ████║██╔══██╗██╔══██╗██╔════╝    ██╔══██╗╚██╗ ██╔╝
    ██╔████╔██║███████║██║  ██║█████╗      ██████╔╝ ╚████╔╝ 
    ██║╚██╔╝██║██╔══██║██║  ██║██╔══╝      ██╔══██╗  ╚██╔╝  
    ██║ ╚═╝ ██║██║  ██║██████╔╝███████╗    ██████╔╝   ██║   
    ╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝    ╚═════╝    ╚═╝   
                                                             
    ██████╗ ██╗  ██╗ █████╗ ██╗   ██╗██╗███████╗██╗  ██╗██╗   ██╗ █████╗ 
    ██╔══██╗██║  ██║██╔══██╗██║   ██║██║██╔════╝██║  ██║╚██╗ ██╔╝██╔══██╗
    ██████╔╝███████║███████║██║   ██║██║███████╗███████║ ╚████╔╝ ███████║
    ██╔══██╗██╔══██║██╔══██║╚██╗ ██╔╝██║╚════██║██╔══██║  ╚██╔╝  ██╔══██║
    ██████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║██║  ██║   ██║   ██║  ██║
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
    """
    print(banner)
    print("\n" + "="*80 + "\n")

class FormBot:
    def __init__(self, api_key: Optional[str] = None, headless: bool = False):
        # Initialize Mistral client
        self.client = MistralClient(api_key=api_key)
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Add these new options to avoid detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Initialize the driver with updated service
        service = Service()
        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Remove navigator.webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def get_deepseek_answer(self, question, options):
        """Get answer from Mistral for the given question and options"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Format options with clear sequence numbers
                options_text = ""
                for i, opt in enumerate(options, 1):
                    options_text += f"Option {i} - {opt}\n"
                
                # Debug print to verify options
                print("\n" + "="*50)
                print("DEBUG: Content being sent to AI")
                print("="*50)
                print("\nQuestion:")
                print(question)
                print("\nOptions:")
                print(options_text)
                
                prompt = f"""You are an expert at answering multiple choice questions. Your task is to analyze the question and options carefully to determine the correct answer. give output only in single number and nothing else with it.

Question: {question}

Available options (in sequence):
{options_text}

Instructions:
1. Read the question carefully
2. Analyze each option in sequence (Option 1, Option 2, etc.)
3. Think through the logic of each answer
4. Select the most correct option
5. Respond with ONLY the number of the correct option (1-{len(options)})

Example:
If you think Option 2 is correct, respond with: 2

Your answer:"""

                print("\nFull Prompt being sent to AI:")
                print("="*50)
                print(prompt)
                print("="*50 + "\n")

                response = self.client.chat(
                    model="mistral-medium",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at answering multiple choice questions. You carefully analyze each question and option in sequence to determine the correct answer. You respond with ONLY a single digit number representing the correct answer. give output only in single number and nothing else with it."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=5
                )
                
                # Extract the number from the response
                answer_text = response.choices[0].message.content.strip()
                print(f"Raw Mistral response: '{answer_text}'")  # Debug print
                
                # Remove any non-numeric characters except digits
                answer_text = ''.join(filter(str.isdigit, answer_text))
                print(f"Extracted digits: '{answer_text}'")  # Debug print
                
                if not answer_text:
                    print(f"Attempt {attempt + 1}: Could not extract number from response: '{response.choices[0].message.content}'")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    return None
                    
                answer_index = int(answer_text)
                if answer_index < 1 or answer_index > len(options):
                    print(f"Attempt {attempt + 1}: Invalid answer index {answer_index} for {len(options)} options")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    return None
                    
                return answer_index
                
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error getting Mistral answer: {e}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    continue
                return None
        
        return None

    def get_current_email(self):
        """Get the email of the currently logged-in user from Google Form"""
        try:
            # Wait for the form page to load completely
            time.sleep(3)
            
            # Try to find email from the Google Form header
            selectors = [
                "div.gb_k.gb_l.gb_m.gb_n",  # Form header account info
                "a[aria-label*='Google Account']",
                ".gb_A.gb_La.gb_f",  # Common Google Form header class
                "div[aria-label*='Google Account']"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    text = element.get_attribute('aria-label') or element.text
                    if text and '@' in text:
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                        if email_match:
                            return email_match.group(0)
                except:
                    continue
            
            # If email not found in header, try getting from page source
            page_source = self.driver.page_source
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', page_source)
            if email_match:
                return email_match.group(0)
            
            return None
        except Exception as e:
            print(f"Error getting email: {e}")
            return None

    def verify_user(self):
        """Verify if the current user is authorized"""
        max_retries = 3
        for attempt in range(max_retries):
            email = self.get_current_email()
            if email:
                if email.lower() in [auth_email.lower() for auth_email in AUTHORIZED_EMAILS]:
                    print(f"\n✅ Authorized user: {email}")
                    return True
                else:
                    print(f"\n❌ Unauthorized user: {email}")
                    print("This version is not licensed for your account.")
                    return False
            else:
                print(f"\n⚠️ Attempt {attempt + 1}/{max_retries}: Could not verify email from form page. Retrying...")
                time.sleep(2)
        
        print("\n❌ Could not verify your Google account after multiple attempts.")
        return False

    def fill_form(self, form_url):
        """Fill out the Google Form"""
        try:
            print("\nOpening browser...")
            self.driver.get("https://accounts.google.com")
            
            print("\n1. Please log into your Google account now")
            print("2. Once logged in, press Enter to continue")
            print("\nTaking you to Google login...")
            time.sleep(3)  # Give time for the message to be read
            
            # Wait for the login page to be fully loaded
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                print("Error waiting for login page: ", e)
            
            print("\nPlease complete your login now...")
            print("Take your time, the program will wait.")
            
            while True:
                try:
                    user_input = input("\nHave you completed login? (yes/no): ").lower()
                    if user_input == 'yes':
                        print("\nVerifying your account...")
                        time.sleep(2)  # Give time for the page to settle
                        for attempt in range(3):  # Try verification up to 3 times
                            if self.verify_user():
                                break
                            if attempt < 2:  # Don't wait on last attempt
                                print("Retrying verification...")
                                time.sleep(2)
                        else:  # If all attempts failed
                            print("\nAccess denied. Closing in 5 seconds...")
                            time.sleep(5)
                            return
                        break
                    elif user_input == 'no':
                        print("Take your time, type 'yes' when you're done.")
                    else:
                        print("Please type 'yes' or 'no'")
                except EOFError:
                    print("Error reading input. Please try running from command prompt.")
                    return
            
            print("\nNavigating to the form...")
            try:
                self.driver.get(form_url)
                # Add a delay after navigation
                time.sleep(3)  # Wait for 3 seconds after navigation
            except Exception as e:
                print(f"Error navigating to form: {e}")
                input("Press Enter to exit...")
                return
            
            # Wait for the form to be fully loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']"))
            )
            
            # Find all questions
            questions = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            print(f"Found {len(questions)} questions")
            
            # Modified start prompt section
            print("\nReady to begin answering questions!")
            print("Type 'start' when you're ready to proceed.")
            while True:
                try:
                    user_input = input("Type 'start' to begin: ").lower()
                    if user_input == 'start':
                        break
                    else:
                        print("Please type 'start' to begin or press Ctrl+C to exit")
                except EOFError:
                    print("Error reading input. Please try running from command prompt.")
                    return
            
            for question_index, question in enumerate(questions, 1):
                try:
                    # Wait for question to be visible and clickable
                    WebDriverWait(self.driver, 5).until(
                        EC.visibility_of(question)
                    )
                    
                    # Get question text
                    question_text = question.find_element(By.CSS_SELECTOR, "div[role='heading']").text
                    print(f"\nProcessing question {question_index}: {question_text}")
                    
                    # Get options for this specific question
                    options = question.find_elements(By.CSS_SELECTOR, "div[role='radio']")
                    print(f"\nDebug - Raw options found: {len(options)}")
                    
                    # More detailed option extraction
                    option_texts = []
                    for i, opt in enumerate(options, 1):
                        try:
                            # Get the text from aria-label attribute
                            option_text = opt.get_attribute('aria-label')
                            if option_text:
                                print(f"Debug - Option {i} text: '{option_text}'")
                                option_texts.append(option_text)
                            else:
                                print(f"Debug - Could not find text for option {i}")
                                
                        except Exception as e:
                            print(f"Debug - Error processing option {i}: {e}")
                            continue
                    
                    print(f"\nFinal options found: {len(option_texts)}")
                    for i, text in enumerate(option_texts, 1):
                        print(f"Option {i}: {text}")
                    
                    # Get answer from Mistral with retries
                    answer_index = self.get_deepseek_answer(question_text, option_texts)
                    
                    if answer_index and 0 <= answer_index - 1 < len(options):
                        # Wait for option to be clickable
                        option = options[answer_index - 1]  # Use the option directly from the question's options
                        # Scroll the option into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", option)
                        # Click the option
                        option.click()
                        print(f"Selected option {answer_index} for question {question_index}")
                    else:
                        print(f"Could not get valid answer for question {question_index}: {question_text}")
                    
                except Exception as e:
                    print(f"Error processing question {question_index}: {e}")
                    continue
            
            print("\nForm filling completed! Please review your answers.")
            print("You can now manually submit the form when you're ready.")
            input("Press Enter when you want to close the browser...")
            
        except Exception as e:
            print(f"Error filling form: {e}")
        finally:
            self.driver.quit()

def main():
    try:
        print_banner()  # Banner at start
        
        parser = argparse.ArgumentParser(description='Google Forms MCQ Auto-Fill Bot')
        parser.add_argument('--url', '-u', type=str, help='Google Form URL to fill', required=True)
        parser.add_argument('--api-key', '-k', type=str, help='Mistral API key', required=True)
        parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        
        args = parser.parse_args()
        
        if args.debug:
            print("Debug mode enabled")
            print(f"Form URL: {args.url}")
            print("API Key: ***" + args.api_key[-4:])
            print(f"Headless mode: {args.headless}")
        
        bot = FormBot(api_key=args.api_key, headless=args.headless)
        bot.fill_form(args.url)
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
    finally:
        print("\n\n")
        print_banner()  # Banner at end
        input("Press Enter to exit...")
    return 0

if __name__ == "__main__":
    main() 