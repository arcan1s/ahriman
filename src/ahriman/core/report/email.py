#
# Copyright (c) 2021-2023 ahriman team.
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
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.core.report.report import Report
from ahriman.core.util import pretty_datetime, utcnow
from ahriman.models.package import Package
from ahriman.models.repository_id import RepositoryId
from ahriman.models.result import Result
from ahriman.models.smtp_ssl_settings import SmtpSSLSettings


class Email(Report, JinjaTemplate):
    """
    email report generator

    Attributes:
        host(str): SMTP host to connect
        no_empty_report(bool): skip empty report generation
        password(str | None): password to authenticate via SMTP
        port(int): SMTP port to connect
        receivers(list[str]): list of receivers emails
        sender(str): sender email address
        ssl(SmtpSSLSettings): SSL mode for SMTP connection
        template(Path | str): path or name to template for built packages
        template_full(Path | str | None): path or name to template for full package list
        user(str | None): username to authenticate via SMTP
    """

    def __init__(self, repository_id: RepositoryId, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
            repository_id(RepositoryId): repository unique identifier
            configuration(Configuration): configuration instance
            section(str): settings section name
        """
        Report.__init__(self, repository_id, configuration)
        JinjaTemplate.__init__(self, repository_id, configuration, section)

        self.template = configuration.get(section, "template", fallback=None) or \
            configuration.getpath(section, "template_path")
        self.template_full = configuration.get(section, "template_full", fallback=None) or \
            configuration.getpath(section, "full_template_path", fallback=None)

        # base smtp settings
        self.host = configuration.get(section, "host")
        self.no_empty_report = configuration.getboolean(section, "no_empty_report", fallback=True)
        self.password = configuration.get(section, "password", fallback=None)
        self.port = configuration.getint(section, "port")
        self.receivers = configuration.getlist(section, "receivers")
        self.sender = configuration.get(section, "sender")
        self.ssl = SmtpSSLSettings.from_option(configuration.get(section, "ssl", fallback="disabled"))
        self.user = configuration.get(section, "user", fallback=None)

    def _send(self, text: str, attachment: dict[str, str]) -> None:
        """
        send email callback

        Args:
            text(str): email body text
            attachment(dict[str, str]): map of attachment filename to attachment content
        """
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = ", ".join(self.receivers)
        message["Subject"] = f"{self.name} build report at {pretty_datetime(utcnow())}"

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

    def generate(self, packages: list[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
            packages(list[Package]): list of packages to generate report
            result(Result): build result
        """
        if self.no_empty_report and not result.success:
            return

        text = self.make_html(result, self.template)
        attachments = {}
        if self.template_full is not None:
            attachments["index.html"] = self.make_html(Result(updated=packages), self.template_full)

        self._send(text, attachments)
