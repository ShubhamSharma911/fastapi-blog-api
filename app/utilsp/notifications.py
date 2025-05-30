import asyncio

async def send_email(user_id: int, filename: str):
    await asyncio.sleep(1)
    print(f"[Email] Sent upload confirmation to user {user_id} for {filename}")

async def send_slack_notification(user_id: int, filename: str):
    await asyncio.sleep(2)
    print(f"[Slack] Notified team about resume upload by user {user_id}")

async def write_internal_log(user_id: int, filename: str):
    await asyncio.sleep(1)
    print(f"[Log] Logged resume upload for user {user_id}: {filename}")

async def notify_all_services(user_id: int, filename: str):
    await asyncio.gather(
        send_email(user_id, filename),
        send_slack_notification(user_id, filename),
        write_internal_log(user_id, filename),
    )
