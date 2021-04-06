#
# Copyright (c) 2021 ahriman team.
#
# This file is part of ahriman
# (see https://github.com/arcan1s/ahriman).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import datetime
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.core.report.report import Report
from ahriman.core.util import pretty_datetime
from ahriman.models.package import Package
from ahriman.models.smtp_ssl_settings import SmtpSSLSettings


class Email(Report, JinjaTemplate):
    """
    email report generator
    :ivar host: SMTP host to connect
    :ivar password: password to authenticate via SMTP
    :ivar port: SMTP port to connect
    :ivar receivers: list of receivers emails
    :ivar sender: sender email address
    :ivar ssl: SSL mode for SMTP connection
    :ivar user: username to authenticate via SMTP
    """

    def __init__(self, architecture: str, configuration: Configuration) -> None:
        """
        default constructor
        :param architecture: repository architecture
        :param configuration: configuration instance
        """
        Report.__init__(self, architecture, configuration)
        JinjaTemplate.__init__(self, "email", configuration)

        # base smtp settings
        self.host = configuration.get("email", "host")
        self.password = configuration.get("email", "password", fallback=None)
        self.port = configuration.getint("email", "port")
        self.receivers = configuration.getlist("email", "receivers")
        self.sender = configuration.get("email", "sender")
        self.ssl = SmtpSSLSettings.from_option(configuration.get("email", "ssl", fallback="disabled"))
        self.user = configuration.get("email", "user", fallback=None)

    def _send(self, text: str, attachment: Dict[str, str]) -> None:
        """
        send email callback
        :param text: email body text
        :param attachment: map of attachment filename to attachment content
        """
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = ", ".join(self.receivers)
        message["Subject"] = f"{self.name} build report at {pretty_datetime(datetime.datetime.utcnow().timestamp())}"

        message.attach(MIMEText(text, "html"))
        for filename, content in attachment.items():
            attach = MIMEText(content, "html")
            attach.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(attach)

        if self.ssl != SmtpSSLSettings.SSL:
            session = smtplib.SMTP(self.host, self.port)
            if self.ssl == SmtpSSLSettings.STARTTLS:
                session.starttls()
        else:
            session = smtplib.SMTP_SSL(self.host, self.port)
        if self.user is not None and self.password is not None:
            session.login(self.user, self.password)
        session.sendmail(self.sender, self.receivers, message.as_string())
        session.quit()

    def generate(self, packages: Iterable[Package], built_packages: Iterable[Package]) -> None:
        """
        generate report for the specified packages
        :param packages: list of packages to generate report
        :param built_packages: list of packages which has just been built
        """
        text = self.make_html(built_packages, False)
        attachments = {"index.html": self.make_html(packages, True)}
        self._send(text, attachments)
