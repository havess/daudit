# Plotly is a cool python library to generate graphs
import plotly.graph_objects as go
import os

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

    def createBarGraph(self, data):
        fig = go.Figure([go.Bar(x=list(data.keys()), y=list(data.values()))])
        # fig.show()

        if not os.path.exists("reports"):
            os.mkdir("reports")

        fig.write_image("reports/sample-report.png")


    def build(self, url):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "text": url,
        }