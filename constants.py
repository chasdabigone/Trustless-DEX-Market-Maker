import smartpy as sp

# The fixed point number representing 1 in the system, 10^18
PRECISION = sp.nat(1000000000000000000)

# A constant that can be multipled by a mutez to produce a value in Kolibri's scale.
MUTEZ_TO_TOKEN_CONVERSION = 1000000000000

# A constant that can be multipled by a mutez to produce a value in Kolibri's scale.
MUTEZ_TO_KOLIBRI_CONVERSION = 1000000000000

# The asset pair reported by Harbinger.
ASSET_CODE = "XTZ-USD"

# The type of data returned in Harbinger's Normalizer callback.
HARBINGER_DATA_TYPE = sp.TPair(sp.TString, sp.TPair(sp.TTimestamp, sp.TNat))
