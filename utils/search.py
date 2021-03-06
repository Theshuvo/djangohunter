try:

	import shodan
	import requests
	from bs4 import BeautifulSoup

except ImportError as e:
    print("Error: %s \n" % (e))
    print("Try this ... pip install -r /path/to/requirements.txt")

from utils.color import Color

class Search(object):

	"""docstring for ClassName"""
	def __init__(self, api, dork='"DisallowedHost"', limit=None, offset=None, timeout=None) :

		self.shodan = shodan.Shodan(api)
		self.limit = limit
		self.offset = offset
		self.timeout = timeout

		self._urls = []
		self.color = Color()


		try:

			results = self.shodan.search(dork, limit=self.limit, offset=offset)
			matches = results['matches']
			total = results['total']


			print('{} Shodan found {} hosts with debug mode enabled'.format(self.color.status("[+]"), total))
			print("{} Looking for secret keys wait a moment ..\n".format(self.color.yellows("[!]")))

			for match in matches:

				self.ipadress = match['ip_str']
				self.port = match['port']
				self.hostnames = match['hostnames']
				self.org = match['org']
				self.domains = match['domains']
				self.city = match['location']['city']
				self.country = match['location']['country_name']
	
				# Skip hosts with SSL
				if self.port == 443 :
					continue

				self._urls.append(['http://{}:{}'.format(self.ipadress, self.port)])
				
		except shodan.APIError as error:
			print("error: {}".format(error))
			pass

	@property
	def urls(self):
		return self._urls

	def load(self, urls):

		for url in urls:
			counter = 0
			mapping = (
				'DB_HOST', 
				'AWS',
				'MYSQL',
				'RDS_HOSTNAME', 
				'ADMIN_USER', 
				'RABBITMQ_HOST', 
				'WALLET_RW_HOST', 
				'POSTGRES_PASSWORD', 
				'KYC_API_KEY', 
				'DATABASE_URL',
				'AUTO_RECRAW_HOST',
				'BONANZA_API_KEY',
				'CELERY',
				'MWS_ACCESS_KEY',
				'PROXY_SECRET',
				'KEEPA_API',
				'MONGODB_PASSWORD',
				'SCRAPYMONGO_PASSWORD',
				'FACE_ID_DB_PASSWORD',
				'AWS_SECRET_ACCESS_KEY',
				'GOOGLE_OAUTH2_CLIENT_SECRET',
				'POSTGRES_PASSWORD',
				'DJANGO_SECRET_KEY',
				'FIREBASE_SERVER_KEY',
				'GOOGLE_API_KEY',
				'SSH_PASSWORD',
				'SSH_AUTH',
				'RABBITMQ_DEFAULT_PASS',
				'AWS_SECRET_KEY',
				'AWS_S3_BUCKET',
				'SENDGRID_PASSWORD',
				'PAYU_KEY',
				'DHL_API_CLIENT_SECRET',
				'LIGHT_PASSWORD',
				'DB_PASSWORD',
				'ATEL_AUTH_SECRET',
				'GPG_KEY',
				'Facebook',
				'Google',
				'Yahoo',
				'Github',
				'Stack',
				'GEOSERVER',
				'RDS_PASSWORD',
				'SMTP_PASSWORD'
			) # Interesting keywords ('DisallowedHost at /', 'DisallowedHost', 'KeyError', 'OperationalError', 'Page not found at /', '')

			self.hostname = ', '.join(str(hostname) for hostname in self.hostnames)
			self.domain = ', '.join(str(domain) for domain in self.domains)

			try:
				request = requests.get('{}'.format(url), timeout=self.timeout)
				html = BeautifulSoup(request.text, 'html.parser')

				keys = []

				for key in mapping :
					if key in html.prettify():
						keys.append(key)

				keys = ', '.join(str(key) for key in keys) # Keywords found

				if len(keys) != 0:
					print("[+] Possible exposed credentials on {}".format(request.url))
					print('[+] Secret keys found {}\n'.format(self.color.error(keys)))
					# some information about the host
					print("\tOrganization: {}\n\tHostnames: {}\n\tDomains: {}\n\tCity: {}\n\tCountry: {}\n".format(self.org, self.hostname, self.domain, self.city, self.country))

			except requests.exceptions.RequestException as error:
				continue
			# Keep track of how many results have been downloaded so we don't use up all our query credits
			counter += 1
			if counter >= self.limit:
				break