import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
import json

fromaddr = "botwordpress1@gmail.com"
toaddr = "rishabh9511@gmail.com"




def mail_the_report(report, articles_received, articles_posted ):

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Articles report"
    body = "Total articles received %s \n Total articles posted %s " % (articles_received, articles_posted)

    msg.attach(MIMEText(body, 'plain'))

    filename =  "article_report.json"

    #with open("../%s"%(filename), "w") as file_obj:
            #file_obj.write(json.dumps(report, indent=4, separators=(',', ': ')))

    #attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(json.dumps(report, indent=4, separators=(',', ': ')))
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "`1234567890-=")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
