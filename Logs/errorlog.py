import logging
import smtplib
from email.mime.text import MIMEText

class Errorlog():

	def __init__(self):
		#Logging
		self.LOG_FILENAME = "%s/pythonerror.log" % (LOG_PATH)
		self.logger = logging.getLogger("Python Error Log")
		self.logger.setLevel(logging.DEBUG)
		self.ch = logging.FileHandler(self.LOG_FILENAME)
		self.ch.setLevel(logging.DEBUG)
		self.formatter = logging.Formatter("%(asctime)s - %(name)s - Thread:%(thread)d - Process:%(process)d - %(message)s")
		self.ch.setFormatter(self.formatter)
		self.logger.addHandler(self.ch)

	def logerror(self):
		self.logger.exception("ERROR:")

	def setEmail(self, frm, to, filename, user, pwd, server):
		self.fromaddr = frm
		self.toaddrs  = to
		fp = open(filename, 'rb')
		self.msg = MIMEText(fp.read())
		fp.close()
		self.msg['Subject'] = 'The contents of %s' % filename
		self.msg['From'] = frm
		self.msg['To'] = to
		self.username = user
		self.password = pwd
		self.server = smtplib.SMTP(server)
	def sendEmail(self):
		self.server.starttls()
		self.server.ehlo()
		self.server.login(self.username,self.password)
		self.server.sendmail(self.fromaddr, self.toaddrs, self.msg.as_string())
		self.server.quit()

elog = Errorlog()