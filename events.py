from datetime import datetime

from icecream import ic

from main import db, scheduler
from orm import RevokedTokenModel


@scheduler.task("interval", id="delete_expired_tokens", minutes=1)
def delete_exprired_tokens():
    app = scheduler.app
    if app is not None:
        with app.app_context():
            ic("Deleting expired tokens")
            db.session.query(RevokedTokenModel).filter(
                RevokedTokenModel.expires_date < datetime.now()
            ).delete()
            db.session.commit()
