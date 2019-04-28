# -*- coding: utf-8 -*-
import socket
from flask import Blueprint
from config import islocal
url = Blueprint('main',__name__)

hostname = socket.gethostname()

from . import dataBankView, anydoorView, dataToolView, pipView, xmindCountView

if islocal:
    from . import localView
else:
    from . import otherView