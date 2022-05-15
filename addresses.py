import smartpy as sp

# This file contains addresses for tests which are named and ensure uniqueness across the test suite.

# The address which acts as the Governor
GOVERNOR_ADDRESS = sp.address("tz1YYnf7vGXqCmB1shNg4rHiTz5gwWTDYceB")

# The address that acts as the token contract.
TOKEN_ADDRESS = sp.address("KT1GG8Zd5rUp1XV8nMPRBY2tSyVn6NR5F4Q1")

# The address which acts as the Oracle.
ORACLE_ADDRESS = sp.address("tz1P2Po7YM526ughEsRbY4oR9zaUPDZjxFrb")

# An address which represents a Harbinger Oracle.
HARBINGER_ADDRESS = sp.address("tz1TDSmoZXwVevLTEvKCTHWpomG76oC9S2fJ")

# An address which acts as a pause guardian.
PAUSE_GUARDIAN_ADDRESS = sp.address("tz1Rsw2YaQ54pwiQJ6q3h2vgH4kWrc5K5uG8")

# An address which is never used. This is a `null` value for addresses.
NULL_ADDRESS = sp.address("tz1bTpviNnyx2PXsNmGpCQTMQsGoYordkUoA")

# The address which acts as the Token Admin
TOKEN_ADMIN_ADDRESS = sp.address("tz1eEnQhbwf6trb8Q8mPb2RaPkNk2rN7BKi8")

# The address of the Harbinger Normalizer (views)
HARBINGER_VWAP_ADDRESS = sp.address("KT1ENe4jbDE1QVG1euryp23GsAeWuEwJutQX")

# The address of the Harbinger Spot Price (views)
HARBINGER_SPOT_ADDRESS = sp.address("KT1UcwQtaztLSq8oufdXAtWpRTfFySCj7gFM")

# The address of a XTZ/kUSD Quipuswap contract
QUIPUSWAP_ADDRESS = sp.address("KT1K4EwTpbvYN9agJdjpyJm4ZZdhpUNKB3F6")

# The address of the contract to receive the swap
RECEIVER_ADDRESS = GOVERNOR_ADDRESS

# An series of named addresses with no particular role.
# These are used for token transfer tests.
ALICE_ADDRESS = sp.address("tz1VQnqCCqX4K5sP3FNkVSNKTdCAMJDd3E1n")
BOB_ADDRESS = sp.address("tz2FCNBrERXtaTtNX6iimR1UJ5JSDxvdHM93")
CHARLIE_ADDRESS = sp.address("tz3S6BBeKgJGXxvLyZ1xzXzMPn11nnFtq5L9")

# An address of a Baker
BAKER_PUBLIC_KEY_HASH = "tz3RDC3Jdn4j15J7bBHZd29EUee9gVB1CxD9"
BAKER_ADDRESS = sp.address(BAKER_PUBLIC_KEY_HASH)
BAKER_KEY_HASH = sp.key_hash(BAKER_PUBLIC_KEY_HASH)
VOTING_POWERS = {
  BAKER_KEY_HASH: 8000,
}
