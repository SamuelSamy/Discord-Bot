
from urllib import response


class AppealTypes:

    not_answered = 0
    accepted = 1
    denied = -1
    flagged = -10
    warn = -100


class AppealStructure:

    ID              =       "ID"
    guild           =       "guild"
    user            =       "user"
    roblox          =       "roblox"
    ban_reason      =       "ban_reason"
    unban_reason    =       "unban_reason"
    response_time   =       "response_time"
    response        =       "response"
    stage           =       "stage"

    
class Emotes:

    accepted = "<:greenTick:901197496276111451>"
    denied = "<:redTick:901197559912099841>"
    warned = "⚠️"
    flagged = "<:OrangeFlag:913862268125605898>"


class AppealStages:

    opened      = 0
    name        = 1
    ban         = 2
    unban       = 3
    sent        = 4
    answered    = 5