# Plotly is a cool python library to generate graphs
    # import plotly.graph_objects as go

class ReportsBuilder:
    def __init__(self, channel):
        self.channel = channel
        self.username = "daudit"
        self.timestamp = ""

    # We should pass in the metrics data from my_daudit
    def generateGraph(self):
        return {
            "ts": self.timestamp,
            "channels": self.channel,
            "username": self.username,
            "file": "reports/sample-report.png",    # TODO: Change this hardcoded path to saved report images
        }

    def build(self, url):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "text": url,
        }