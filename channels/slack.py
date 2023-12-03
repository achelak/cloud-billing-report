from slack_sdk import WebClient
import os


class SlackNotificator:
    def __init__(self, slack_api_token: str = None, slack_channel_id: str = None, ascii_report_tables: tuple = None,
                 report_date: str = None):
        self.slack_api_token = slack_api_token
        self.slack_channel_id = slack_channel_id
        self.ascii_report_table_by_project = ascii_report_tables[0]
        self.ascii_report_table_by_service = ascii_report_tables[1]
        self.report_date = report_date
        self.by_project_title = f"💸 *Billing Report for Google Cloud Services per Project* 📊\nReport for the *{self.report_date}*, (for month / for yesterday). Sorted by month price."
        self.by_service_title = f"💸 *Billing Report for Google Cloud Services per Service* 📊\nReport for the *{self.report_date}*, (for month / for yesterday). Sorted by month price."

    def send_message(self):
        self.chunk_message(self.ascii_report_table_by_project, self.by_project_title)
        self.chunk_message(self.ascii_report_table_by_service, self.by_service_title)

    def chunk_message(self, table: str, title: str):
        all_lines = table.split('\n')
        filtered_lines = []

        skip_line = False
        for line in all_lines:
            if skip_line:
                skip_line = False
                continue

            if all(char.isspace() or char == '|' for char in line):
                skip_line = True
                continue

            filtered_lines.append(line)

        first_30_lines = filtered_lines[:30]

        first_30_text = title + '\n```\n' + '\n'.join(first_30_lines) + '\n```'

        client = WebClient(token=self.slack_api_token)
        channel_id = self.slack_channel_id

        response = client.chat_postMessage(channel=channel_id, text=first_30_text)
        initial_thread_ts = response.data['ts']

        remaining_lines = all_lines[30:]
        chunk_size = 30

        for i in range(0, len(remaining_lines), chunk_size):
            chunk = remaining_lines[i:i + chunk_size]
            chunk_text = '```\n' + '\n'.join(chunk) + '\n```'

            client.chat_postMessage(channel=channel_id, text=chunk_text, thread_ts=initial_thread_ts)
