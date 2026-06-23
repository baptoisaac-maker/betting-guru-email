# Betting Guru Email Bot

This starter project generates a daily football betting-analysis report and emails it automatically.

## What it does now

- Builds a WhatsApp/email-ready daily report
- Selects one best market per match from multiple prediction inputs
- Adds confidence and bookie-trap warnings
- Sends by email using SMTP
- Includes GitHub Actions automation for daily sending at **08:00 Africa/Kampala**

> Current MVP uses sample prediction inputs. The next phase is connecting live fixture APIs and compliant prediction sources.

## Local setup

```bash
cd betting-guru-email
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`.

First test without sending:

```env
DRY_RUN=true
```

Run:

```bash
python main.py
```

To send real email:

```env
DRY_RUN=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_sender_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_sender_email@gmail.com
EMAIL_TO=your_receiving_email@example.com
```

Then run:

```bash
python main.py
```

## Gmail App Password

For Gmail, enable 2-Step Verification and create an App Password. Do not use your normal Gmail password.

## GitHub Actions daily automation

1. Create a GitHub repository.
2. Upload these files.
3. Go to repository **Settings → Secrets and variables → Actions → New repository secret**.
4. Add:
   - `EMAIL_HOST`
   - `EMAIL_PORT`
   - `EMAIL_USERNAME`
   - `EMAIL_PASSWORD`
   - `EMAIL_FROM`
   - `EMAIL_TO`
5. The included workflow sends daily at `05:00 UTC`, which is `08:00 Africa/Kampala`.
6. You can test manually from **Actions → Send Daily Betting Guru Email → Run workflow**.

## Responsible betting

This tool provides analysis only. It does not guarantee outcomes. Bet responsibly.
