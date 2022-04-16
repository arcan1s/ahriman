#
# Copyright (c) 2021-2022 ahriman team.
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
# technically we could use python-telegram-bot, but it is just a single request, cmon
import requests

from typing import Iterable

from ahriman.core.configuration import Configuration
from ahriman.core.report.jinja_template import JinjaTemplate
from ahriman.core.report.report import Report
from ahriman.core.util import exception_response_text
from ahriman.models.package import Package
from ahriman.models.result import Result


class Telegram(Report, JinjaTemplate):
    """
    telegram report generator

    Attributes:
      TELEGRAM_API_URL(str): (class attribute) telegram api base url
      TELEGRAM_MAX_CONTENT_LENGTH(int): (class attribute) max content length of the message
      api_key(str): bot api key
      chat_id(str): chat id to post message, either string with @ or integer
      template_path(Path): path to template for built packages
      template_type(str): template message type to be used in parse mode, one of MarkdownV2, HTML, Markdown
    """

    TELEGRAM_API_URL = "https://api.telegram.org"
    TELEGRAM_MAX_CONTENT_LENGTH = 4096

    def __init__(self, architecture: str, configuration: Configuration, section: str) -> None:
        """
        default constructor

        Args:
          architecture(str): repository architecture
          configuration(Configuration): configuration instance
          section(str): settings section name
        """
        Report.__init__(self, architecture, configuration)
        JinjaTemplate.__init__(self, section, configuration)

        self.api_key = configuration.get(section, "api_key")
        self.chat_id = configuration.get(section, "chat_id")
        self.template_path = configuration.getpath(section, "template_path")
        self.template_type = configuration.get(section, "template_type", fallback="HTML")

    def _send(self, text: str) -> None:
        """
        send message to telegram channel

        Args:
          text(str): message body text
        """
        try:
            response = requests.post(
                f"{self.TELEGRAM_API_URL}/bot{self.api_key}/sendMessage",
                data={"chat_id": self.chat_id, "text": text, "parse_mode": self.template_type})
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.exception("could not perform request: %s", exception_response_text(e))
            raise
        except Exception:
            self.logger.exception("could not perform request")
            raise

    def generate(self, packages: Iterable[Package], result: Result) -> None:
        """
        generate report for the specified packages

        Args:
          packages(Iterable[Package]): list of packages to generate report
          result(Result): build result
        """
        if not result.success:
            return
        text = self.make_html(result, self.template_path)
        # telegram content is limited by 4096 symbols, so we are going to split the message by new lines
        # to fit into this restriction
        if len(text) > self.TELEGRAM_MAX_CONTENT_LENGTH:
            position = text.rfind("\n", 0, self.TELEGRAM_MAX_CONTENT_LENGTH)
            portion, text = text[:position], text[position + 1:]  # +1 to exclude newline we split
            self._send(portion)
        # send remaining (or full in case if size is less than max length) text
        self._send(text)
