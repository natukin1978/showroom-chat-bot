class ShowroomCommentLogAnalyzer:
    KEY_CREATED_AT = "created_at"

    def __init__(self):
        self.latest_created_at = None
        self.comment_log = {}

    def get_new_comments(self) -> dict[str, any]:
        comment_logs = self.comment_log["comment_log"]
        if self.latest_created_at:
            comment_logs = list(
                filter(
                    lambda comment_log: comment_log[self.KEY_CREATED_AT]
                    > self.latest_created_at,
                    comment_logs,
                )
            )
        if comment_logs:
            mcl = max(
                comment_logs, key=lambda comment_log: comment_log[self.KEY_CREATED_AT]
            )
            self.latest_created_at = mcl[self.KEY_CREATED_AT]
        return comment_logs

    def merge(self, json_data: dict[str, any]):
        self.comment_log |= json_data
