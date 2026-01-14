from ..models.audit import sdq_config_checksum
from ..app.extensions import db
from flask import current_app
import hashlib


def check_config(filename:str) -> None:
    current_app.logger.info(f"Check hash of file {filename}")

    sdq_config = sdq_config_checksum.query.filter_by(
        config_name="config"
    ).order_by(sdq_config_checksum.updated_at.desc()).first()

    if sdq_config:
        old_hash = sdq_config.checksum
    else:
        old_hash = None

    config = sdq_config_checksum.query.filter_by(
        config_name="config"
    ).order_by(sdq_config_checksum.updated_at.desc()).first()

    with open(filename, "rb") as f:
        config_hash = hashlib.md5()
        while True:
            buf = f.read(1048576) # blocksize
            if not buf:
                break
            config_hash.update(buf)
    new_hash = config_hash.hexdigest()

    if old_hash != new_hash:
        current_app.logger.info(f"eventName: checkConfigHash; message: The config {filename} has been modified (new hash {new_hash});")
        log = sdq_config_checksum(config_name="config", checksum=new_hash)
        db.session.add(log)
    db.session.commit()
    