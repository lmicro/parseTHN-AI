import requests 
import datetime
from bs4 import BeautifulSoup
from datetime import datetime
import os
from openai import OpenAI
import traceback
import sys
import smtplib
from email.message import EmailMessage


OpenAIClient = OpenAI()


#############################################################################
def get_text_snippet(article_url, char_limit=200):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
    except requests.RequestException:
        return "Could not retrieve article"

    soup = BeautifulSoup(response.text, 'html.parser')
    first_paragraph = soup.find('p')
    
    if first_paragraph:
        text = first_paragraph.get_text(strip=True)
        return text[:char_limit]
    return "No content found"

#############################################################################
def fetch_and_save_unique_story_links(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    story_links = soup.find_all('a', class_='story-link')
    today = datetime.now().strftime('%Y%m%d')

    existing_urls = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    existing_urls.add(parts[2])

    new_links_count = 0
    with open(output_file, 'a', encoding='utf-8') as file:
        for link in story_links:
            href = link.get('href')
            if href and href not in existing_urls:
                snippet = get_text_snippet(href)
                line = f"{today}|{snippet}|{href}\n"
                file.write(line)
                new_links_count += 1

    print(f"{new_links_count} new links saved to {output_file}")
#############################################################################
def get_full_text(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join(p.get_text(strip=True) for p in paragraphs)
    return text

#############################################################################
# AI PROCESSING HERE
#############################################################################
def summarize_text(text):
    try:
        #print("\n\nRunning summarize_text with" + text)
        askquestion1 = "From what is provided give me a list of products and versions (if provided) and 3 security keywords associated with this story and in a short and simple paragraph summarize the story, while following with the solution suggested, if any. Here is the content:" + text
        #print("\n\n" + askquestion1)
        response = OpenAIClient.responses.create(
            model="o3-mini",
            input = askquestion1)
        #print(response.output_text)
        return response.output_text
        #return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.extract_tb(exc_traceback)
        filename, line, func, text = tb[-1]  # Last item = point of failure
        print(f"Exception: {e}")
        print(f"Occurred in {filename}, line {line}, in function '{func}'")
        print(f"Code: {text}")
        return f"Failed to summarize: {e} - Occurred in {filename}, line {line}, in function '{func}'"

        #response = OpenAICLient.responses.create(
        #   model="gpt-4o-mini",
        #    messages=[
        #        {"role": "system", "content": "You are a helpful assistant that writes detailed summaries of articles."},
        #        {"role": "user", "content": f"Please summarize the following article in a detailed paragraph:\n\n{text}"} ], max_tokens=500)
#############################################################################

def generate_summary_report(input_file):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'summary_report_{timestamp}.txt'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(output_file, 'w', encoding='utf-8') as report:
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) != 3:
                continue
            date, description, url = parts
            full_text = get_full_text(url)
            ##################################################
            # summarize_text call
            ##################################################
            summary = summarize_text(full_text) if full_text else "No content to summarize."
            report.write('\n' + '#'*80 + '\n\n')
            report.write(f"URL:{url}\n")
            report.write(f"Description:\n")
            report.write(f"{description}\n")
            report.write(f"Summary:\n")
            report.write(f"{summary}\n")
            report.write('\n' + '#'*80 + '\n\n')

    print(f"Summary report generated: {output_file}")
    send_email_with_attachment('Joey.Bhagadonuts1999@gmail.com', 'kfui sxxq yjvc ewzr', 'matthew.presti.626@gmail.com,matthaeus.prestius@icloud.com', 'Todays Security Summary', 'This is the Security News Report for Today', output_file)
# send_email_with_attachment('you@gmail.com', 'your_app_password', 'recipient@example.com', 'Subject', 'Body text', 'path/to/file.txt')

#############################################################################
def send_email_with_attachment(sender_email, app_password, recipient_email, subject, body, attachment_path):
    # Create the email message
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)

    # Attach the file
    if os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    else:
        print(f"Attachment file not found: {attachment_path}")
        return

    # Connect to Gmail SMTP and send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
# send_email_with_attachment('you@gmail.com', 'your_app_password', 'recipient@example.com', 'Subject', 'Body text', 'path/to/file.txt')

#send_email_with_attachment('Joey.Bhagadonuts1999@gmail.com', 'xxxx', 'matthew.presti.626@gmail.com', 'Todays Security Summary', 'C:\\Users\\Matthew Presti\\python\\parseTHN\\data')
#send_email_with_attachment('Joey.Bhagadonuts1999@gmail.com', 'kfui sxxq yjvc ewzr', 'matthew.presti.626@gmail.com', 'Todays Security Summary', 'This is the Security News Report for Today', 'c:\\logUploaderSettings.ini')

#############################################################################
if __name__ == "__main__":
    os.chdir('/home/lmicro/python/parseTHN/data')
    target_url = 'https://thehackernews.com'  # Replace with your target URL
    today = datetime.now().strftime('%Y%m%d')
    output_filename = today + "_" + "story_links.txt"
    #print("OPFilename:{output_filename}")
    fetch_and_save_unique_story_links(target_url, output_filename)
    generate_summary_report(output_filename) 
