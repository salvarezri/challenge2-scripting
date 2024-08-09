import requests
import argparse
import re
import json

GENERAL_API_LINK = 'https://api.artic.edu/api/v1/artworks/search'
SPECIFIC_API_LINK = 'https://api.artic.edu/api/v1/artworks/'
JSON_NAME = 'artworks.json'
PDF_NAME = 'artworks.pdf'
EMAIL_SENDER = ''
PASSWORD = ''

parser = argparse.ArgumentParser()
# arguments
parser.add_argument('-s', '--search', type=str,
                    help='search something into art works')
parser.add_argument('-f', '--fields', type=str, default='title,id,artist_display,image_id,place_of_origin,date_start,date_end,department_title,short_description',
                    help='fields separated by <,> wich you want into your Json')
parser.add_argument('-m', '--mail', type=str,
                    help='if is added, Aplication will try to send a pdf with all the information')
parser.add_argument('-a', '--ammount', type=int, default= 10,
                    help='if is added, Aplication will limit to <count>; if is not, the aplication will automatically limit to 10 results')
parser.add_argument('-p', '--page', type=int, default= 1,
                    help='if is added, Aplication will start to count from the page <page>; if is not, the aplication will automatically put 1')

args = parser.parse_args()

# <-- VERIFY INPUTS -->
# to_search = ""
if(args.search == None):
  print('You must specify a search value using <--search> or <-s>')
  exit(code=2)
to_search = args.search

# fields
fields ='title,image_id,artist_display,'+ args.fields

# mail
mail = ""
def is_valid_email(email):
  # Define the regular expression for validating an email address
  email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
  # Use the re.match() method to check if the email matches the regex
  return re.match(email_regex, email) is not None

if args.mail != None:
  if is_valid_email(args.mail):
    # importing posibly large PDF modules 
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    mail = args.mail
  else:
    print('mail  must be a valid direction. example: <simple@email.example>')
    exit(code=2)

# ammount & page
# nothing to validate
ammount = args.ammount
page = args.page

# <-- MAKE THE REQUESTS -->

# call the general request
request_params = {'q': to_search, 'limit':ammount,'page':page}

req = requests.get(GENERAL_API_LINK,params = request_params)
# obtain individual artworks information
artworks_url = map(
  lambda data : data['api_link'].replace("\/","/") ,
  req.json()['data']
)

# obtain requested data for each piece
def get_artwork_data(artwork_url, fields =''):
  request_params = {'fields':fields}
  req = requests.get(artwork_url,params = request_params)
  piece_data = req.json()['data']
  piece_data['image_source'] = f"https://www.artic.edu/iiif/2/{piece_data['image_id']}/full/843,/0/default.jpg"
  return piece_data

artworks_data = []
for url in artworks_url:
  piece_data = get_artwork_data(url,fields)
  artworks_data.append(piece_data)



# <-- GENERATING JSON -->
try:
  # 
  with open(JSON_NAME, 'w',encoding='utf-8') as json_file:
    json.dump(artworks_data,json_file, indent=4)
  is_json = True 
  print(f'JSON generated as {JSON_NAME}')
except Exception as e:
  is_json = False 
  print(e)
  print('could not save the JSON :c')

# <-- MAKING A BASIC PDF -->

# Check if the PDF needs to be generated
if mail == '':
    exit()

# Initializing variables with values
fileName = PDF_NAME
documentTitle = PDF_NAME.split('.')[0]

# Create the PDF object
pdf = canvas.Canvas(fileName)

# Set the document title
pdf.setTitle(documentTitle)

# Start writing text
text = pdf.beginText(40, 780)
text.setFont("Courier", 12)

for art_piece in artworks_data:
    # Write the title of the artwork
    text.setFont("Courier", 12)
    text.setFillColor(colors.blue)
    text.textLine(art_piece['title'])

    # Write the artist's name
    text.setFont("Courier", 10)
    text.setFillColor(colors.blueviolet)
    text.textLine(art_piece['artist_display'])

    # Write additional information
    text.setFont("Courier", 9)
    text.setFillColor(colors.black)
    for key in art_piece.keys():
        if key in ['artist_display', 'title']:
            continue
        line = f'{key} : {art_piece[key]}'
        text.textLine(line)

    # Add a space between artworks
    text.textLine('')

# Add the text to the canvas
pdf.drawText(text)
try:
  # Save the PDF
  pdf.save()
  is_pdf = True
  print(f'PDF generated as {PDF_NAME}') 
except Exception as e:
  is_pdf = False 
  print(e)
  print('could not save the PDF :c')

# <-- SENDING THE MAIL  -->
# get all credentials
try:
  with open('.credentials.txt','r') as file:
    lines = file.readlines()
    # do not forget to erase the \n from the first line
    PASSWORD = lines[0][:-1]
    EMAIL_SENDER = lines[1]
except Exception as e:
  print(e)
  print('could not sent e-mail :c')
  exit()

from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders

import ssl
import smtplib

# creating basics  and body

subject = "searched artworks 2"
body = json.dumps(artworks_data,indent=4)
em = EmailMessage()
em['From'] = EMAIL_SENDER
em['To'] = mail
em['subject'] = subject
em.set_content('Thanks for use our service! here is the content you asked: \n'+body)

if is_json or is_pdf:
  em.add_alternative(body, subtype='html')

# attach json
if is_json:
  with open(JSON_NAME,'rb') as atachment1:
    data1 = atachment1.read()
    data_name1 = atachment1.name.split("/")[-1]
    
  attachment1 = MIMEBase('application', 'octet-stream')
  attachment1.set_payload(data1)
  encoders.encode_base64(attachment1)
  attachment1.add_header('Content-Disposition', f'attachment; filename="{data_name1}"')
  em.attach(attachment1)

# attach PDF
if is_pdf:
  with open(PDF_NAME,'rb') as atachment2:
    data2 = atachment2.read()
    data_name2 = atachment2.name.split("/")[-1]
    
  attachment2 = MIMEBase('application', 'octet-stream')
  attachment2.set_payload(data2)
  encoders.encode_base64(attachment2)
  attachment2.add_header('Content-Disposition', f'attachment; filename="{data_name2}"')
  em.attach(attachment2)

# Loggin and send email
context = ssl.create_default_context()
try:
  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
    smtp.login(EMAIL_SENDER,PASSWORD)
    smtp.sendmail(EMAIL_SENDER,mail,em.as_string())
  print(f'email from {EMAIL_SENDER} to {mail} sent correctly')
    
except Exception as e:
  print(e)