import requests
import time

###############################################################################
# simple_get
#
# An HTTP GET request with basic error handling.
#
# Inputs:
#   url: The URL to request.
#
# Outputs:
#   The content of the HTTP response.
###############################################################################
def simple_get(url):
  try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    content_type = response.headers['Content-Type'].lower()
    if (response.status_code == 200 and content_type is not None and content_type.find('html') > -1):
      return response.content
    else:
      print(f"wtf: {response}")
  except requests.RequestException as e:
    print(f"Error during GET to {url}: {str(e)}", flush=True)

def stringy_now():
  return time.asctime(time.localtime())