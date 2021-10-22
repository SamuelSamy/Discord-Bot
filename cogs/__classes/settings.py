from enum import Enum

class Settings(Enum):
    slowmode_channels    = "slowmode_channels" # [{}]
    lockdown_channels    = "lockdown_channels" # []
    lock_role            = "lock_role" # int
    scam_logs            = "scam_logs" # int
    mod_logs             = "mod_logs" # int
    muted_role           = "muted_role" # int
    helpers              = "helpers" # []
    helper_logs          = "helper_logs" # int
    helper_role          = "helper_role" # int
    suggestions_channels = "suggestions_channels" # []