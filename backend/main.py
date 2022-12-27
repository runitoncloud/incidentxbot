import config
import logging
import logging.config
import sys

from bot.api.flask import app
from bot.models.pg import db_verify
from bot.scheduler import scheduler
from bot.slack.client import (
    slack_workspace_id,
    check_bot_user_in_digest_channel,
)
from bot.slack.handler import app as slack_app

from slack_bolt.adapter.socket_mode import SocketModeHandler
from waitress import serve

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=config.log_level)

"""
Check for required environment variables first
"""

if __name__ == "__main__":
    # Pre-flight checks
    ## Check for environment variables
    config.env_check(
        required_envs=[
            "INCIDENTS_DIGEST_CHANNEL",
            "INCIDENT_GUIDE_LINK",
            "INCIDENT_POSTMORTEMS_LINK",
            "INCIDENT_CHANNEL_TOPIC",
            "SLACK_APP_TOKEN",
            "SLACK_BOT_TOKEN",
            "SLACK_USER_TOKEN",
            "POSTGRES_HOST",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_PORT",
        ]
    )
    ## Make sure templates directory exists and all templates are present
    config.slack_template_check(
        required_templates=[
            "incident_channel_boilerplate.json",
            "incident_digest_notification_update.json",
            "incident_digest_notification.json",
            "incident_public_status_update.json",
            "incident_resolution_message.json",
            "incident_role_update.json",
            "incident_severity_update.json",
            "incident_status_update.json",
            "incident_user_role_dm.json",
            "role_definitions.json",
            "severity_levels.json",
        ]
    )

"""
Scheduler
"""

scheduler.process.start()

"""
Startup
"""


def db_check():
    logger.info("Testing the database connection...")
    db_info = f"""
------------------------------
Database host:  {config.database_host}
Database port:  {config.database_port}
Database user:  {config.database_user}
Database name:  {config.database_name}
------------------------------
    """
    print(db_info)
    if not db_verify():
        logger.fatal(
            "Cannot connect to the database - check settings and try again."
        )
        exit(1)


if __name__ == "__main__":
    ## Make sure database connection works
    db_check()

    ## Startup splash for confirming key options
    startup_message = config.startup_message(workspace=slack_workspace_id)
    print(startup_message)

    # Serve Slack Bolt app
    handler = SocketModeHandler(slack_app, config.slack_app_token)
    handler.connect()

    # Make sure bot user is always present in incident digest channel
    check_bot_user_in_digest_channel()

    # Serve Flask app
    serve(app, host="0.0.0.0", port=3000)
