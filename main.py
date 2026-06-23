import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None

from app.email_sender import send_email
from app.guru_engine import build_daily_report


def main() -> None:
    load_dotenv()
    subject, report = build_daily_report()

    if os.getenv("DRY_RUN", "false").lower() == "true":
        print(subject)
        print("-" * len(subject))
        print(report)
        return

    send_email(subject, report)
    print("Daily predictions email sent.")


if __name__ == "__main__":
    main()
