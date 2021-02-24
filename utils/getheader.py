import random
 
first_num = random.randint(86, 86)
third_num = random.randint(4240, 4240)
fourth_num = random.randint(75, 75)
 
 
class FakeChromeUA:
	os_type = [
				#'(Windows NT 6.1; WOW64)',
				'(Windows NT 10.0; WOW64)'#,
			#	'(X11; Linux x86_64)'#,
		#		'(Macintosh; Intel Mac OS X 10_12_6)'
			   ]
 
	chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)
 
	@classmethod
	def get_ua(cls):
		return ' '.join(['Mozilla/5.0', random.choice(cls.os_type), 'AppleWebKit/537.36',
						 '(KHTML, like Gecko)', cls.chrome_version, 'Safari/537.36']
						)
 
 
class FakeAndroidChromeUA:
	os_type = ['(Linux; Android 6.0; Nexus 5 Build/MRA58N)','(Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012)','(Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004)']

	chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)
 
	@classmethod
	def get_ua(cls):
		return ' '.join(['Mozilla/5.0', random.choice(cls.os_type), 'AppleWebKit/537.36',
						 '(KHTML, like Gecko)', cls.chrome_version, 'Safari/537.36']
						)
 
headers = {
	'User-Agent': FakeChromeUA.get_ua(),
	'Accept-Encoding': 'gzip, deflate, sdch, br',
	'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'Connection': 'keep-alive'
}
headers_mobile = {
	'User-Agent': FakeAndroidChromeUA.get_ua(),
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Connection': 'keep-alive'
}