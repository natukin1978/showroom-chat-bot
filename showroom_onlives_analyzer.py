class ShowroomOnlivesAnalyzer:
    def __init__(self):
        self.onlives = {}

    def get_live(self, main_name: str) -> dict[str, any] | None:
        for onlive in self.onlives["onlives"]:
            for live in onlive["lives"]:
                if "main_name" in live and live["main_name"] == main_name:
                    return live
        return None

    def merge(self, json_data: dict[str, any]):
        self.onlives |= json_data
