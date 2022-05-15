import smartpy as sp

Addresses = sp.io.import_script_from_url("file:addresses.py")
Constants = sp.io.import_script_from_url("file:constants.py")
Errors = sp.io.import_script_from_url("file:errors.py")

################################################################
# Contract
################################################################

class MakerContract(sp.Contract):
  def __init__(
    self,

    governorContractAddress = Addresses.GOVERNOR_ADDRESS,

    vwapContractAddress = Addresses.HARBINGER_VWAP_ADDRESS,
    spotContractAddress = Addresses.HARBINGER_SPOT_ADDRESS,
    
    pauseGuardianContractAddress = Addresses.PAUSE_GUARDIAN_ADDRESS,
    quipuswapContractAddress = Addresses.QUIPUSWAP_ADDRESS,

    receiverContractAddress = Addresses.RECEIVER_ADDRESS, # Address to send the output to

    paused = False,

    tokenPrecision = sp.nat(1000000000000000000), # 18 decimals
    tokenBalance = sp.nat(0), # this should be 0
    tokenAddress = Addresses.TOKEN_ADDRESS,

    maxDataDelaySec = sp.nat(60 * 1), # 1 minute
    minTradeDelaySec = sp.nat(0), # Time to wait in seconds between allowing swaps

    spreadAmount = sp.nat(0), # Spread in percent before allowing a swap
    
    volatilityTolerance = sp.nat(5), # 5%
    tradeAmount = sp.nat(10),
    lastTradeTime = sp.timestamp(1),


    
  ):
    self.init(
 
        governorContractAddress = governorContractAddress,

        vwapContractAddress = vwapContractAddress,
        spotContractAddress = spotContractAddress,
      
        pauseGuardianContractAddress = pauseGuardianContractAddress,
        quipuswapContractAddress = quipuswapContractAddress,

        receiverContractAddress = receiverContractAddress,

        paused = paused,

        tokenPrecision = tokenPrecision,
        tokenBalance = tokenBalance,
        tokenAddress = tokenAddress,

        maxDataDelaySec = maxDataDelaySec,
        minTradeDelaySec = maxDataDelaySec, # A new candle is made before next trade
        
        spreadAmount = spreadAmount, # Amount of spread in percent
      
        volatilityTolerance = volatilityTolerance,
        tradeAmount = tradeAmount,
        lastTradeTime = lastTradeTime,

    )








  ################################################################
  # Trade API
  ################################################################

  @sp.entry_point
  def tokenToTezPayment(self):
    
    # Verify the contract isn't paused.
    sp.verify(self.data.paused == False, Errors.PAUSED)

    # Make sure enough time has passed
    timeDeltaSeconds = sp.as_nat(sp.now - self.data.lastTradeTime)
    sp.verify(timeDeltaSeconds > self.data.minTradeDelaySec, Errors.TRADE_TIME)

    # Read vwap from Harbinger views
    harbingerVwap = sp.view(
      "getPrice",
      self.data.vwapContractAddress,
      Constants.ASSET_CODE,
      sp.TPair(sp.TTimestamp, sp.TNat)
    ).open_some(message = Errors.VWAP_VIEW_ERROR)

    # Read spot price from Harbinger views
    harbingerSpot = sp.view(
      "getPrice",
      self.data.spotContractAddress,
      Constants.ASSET_CODE,
      sp.TPair(
        sp.TTimestamp,                      # Start
        sp.TPair(
            sp.TTimestamp,                  # End
            sp.TPair(
                sp.TNat,                    # Open
                sp.TPair(
                    sp.TNat,                # High
                    sp.TPair(
                        sp.TNat,            # Low
                        sp.TPair(
                            sp.TNat,        # Close
                            sp.TNat         # Volume
                        )
                    )
                )
            )
        )
      )
    
    ).open_some(message = Errors.SPOT_VIEW_ERROR)

    # Assert that the Harbinger spot data is newer than max data delay
    dataAge = sp.as_nat(sp.now - sp.fst(sp.snd(harbingerSpot)))
    sp.verify(dataAge <= self.data.maxDataDelaySec, Errors.STALE_DATA)
  
    # Upsample price numbers to have tokenPrecision digits of precision
    harbingerVwapPrice = (sp.snd(harbingerVwap) * self.data.tokenPrecision)
    harbingerSpotPrice = (sp.fst(sp.snd(sp.snd(sp.snd(sp.snd(sp.snd(harbingerSpot)))))) * self.data.tokenPrecision)

    # Check for volatility difference between VWAP and spot
    volatilityDifference = (abs(harbingerVwapPrice - harbingerSpotPrice) // harbingerSpotPrice) * 100 # because tolerance is a percent
    sp.verify(self.data.volatilityTolerance > volatilityDifference, Errors.VOLATILITY)

    # TODO Check for price difference between Ubinetic/Kaiko/Harbinger oracles

    # Upsample
    tokensToTrade = (self.data.tradeAmount * self.data.tokenPrecision)

    # Calculate the expected XTZ with no slippage.
    # Expected out with no slippage = (number of tokens to trade // XTZ Spot price) // token precision * XTZ Precision
    neutralOut = (tokensToTrade // harbingerSpotPrice) // self.data.tokenPrecision * 1000000

    # Apply spread multiplier
    # Expected out multiplied by spread = (neutral out from above) * (1 + spread amount)
    percent = sp.nat(100) + self.data.spreadAmount
    requiredOut = (neutralOut * percent) // 100 # Note that percent is specified in scale = 100

    # Invoke a quipuswap trade
    tradeParam = (
      tokensToTrade,
      requiredOut,
      self.data.receiverContractAddress,
    )
    tradeHandle = sp.contract(
      sp.TTuple(sp.TNat, sp.TNat, sp.TAddress),
      self.data.quipuswapContractAddress,
      "tokenToTezPayment"
    ).open_some(message = Errors.DEX_CONTRACT_ERROR)
    sp.transfer(tradeParam, sp.mutez(0), tradeHandle)

    # Write last trade timestamp to storage
    self.data.lastTradeTime = sp.now    

  ################################################################
  #  Balance functions
  ################################################################
  
  # Return balance to receiverContractAddress
  @sp.entry_point
  def return_balance(self):
    
    # Update balance
    self.get_balance()

    # Send tokens to receiver
    sendParam = (
      sp.self_address,
      self.data.receiverContractAddress,
      self.data.tokenBalance,
    )

    sendHandle = sp.contract(
      sp.TTuple(sp.TAddress, sp.TAddress, sp.TNat),
      self.data.tokenAddress,
      "transfer"
    ).open_some()
    sp.transfer(sendParam, sp.mutez(0), sendHandle)


  # Call token contract to update balance.
  def get_balance(self):
    param = (sp.self_address, sp.self_entry_point(entry_point = 'redeem_callback'))
    contractHandle = sp.contract(
      sp.TPair(sp.TAddress, sp.TContract(sp.TNat)),
      self.data.tokenAddress,
      "getBalance",      
    ).open_some()
    sp.transfer(param, sp.mutez(0), contractHandle)

  # Private callback for updating Balance.
  @sp.entry_point
  def redeem_callback(self, updatedBalance):
    sp.set_type(updatedBalance, sp.TNat)

    # Validate sender
    sp.verify(sp.sender == self.data.tokenAddress, Errors.BAD_SENDER)

    self.data.tokenBalance = updatedBalance

  ################################################################
  # Pause Guardian
  ################################################################

  # Pause the system
  @sp.entry_point
  def pause(self):
    sp.verify(sp.sender == self.data.pauseGuardianContractAddress, message = Errors.NOT_PAUSE_GUARDIAN)
    self.data.paused = True

  ################################################################
  # Governance
  ################################################################

  # Update the max data delay.
  @sp.entry_point
  def setMaxDataDelaySec(self, newMaxDataDelaySec):
    sp.set_type(newMaxDataDelaySec, sp.TNat)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.maxDataDelaySec = newMaxDataDelaySec

  # Update the delay between swaps.
  @sp.entry_point
  def setMinTradeDelaySec(self, newMinTradeDelaySec):
    sp.set_type(newMinTradeDelaySec, sp.TNat)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.minTradeDelaySec = newMinTradeDelaySec

  # Set the trade amount (in normalized tokens).
  @sp.entry_point
  def setTradeAmount(self, newTradeAmount):
    sp.set_type(newTradeAmount, sp.TNat)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.tradeAmount = newTradeAmount

  # Set spread amount (in percent)
  @sp.entry_point
  def setSpreadAmount(self, newSpreadAmount):
    sp.set_type(newSpreadAmount, sp.TNat)
    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.spreadAmount = newSpreadAmount

  # Set volatility tolerance (in percent)
  @sp.entry_point
  def setVolatilityTolerance(self, newVolatilityTolerance):
    sp.set_type(newVolatilityTolerance, sp.TNat)
    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.volatilityTolerance = newVolatilityTolerance

  # Set the token precision.
  @sp.entry_point
  def setTokenPrecision(self, newTokenPrecision):
    sp.set_type(newTokenPrecision, sp.TNat)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.tokenPrecision = newTokenPrecision

  # Unpause the system.
  @sp.entry_point
  def unpause(self):
    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.paused = False

  # Update the Harbinger VWAP contract.
  @sp.entry_point
  def setVwapContract(self, newVwapContractAddress):
    sp.set_type(newVwapContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.vwapContractAddress = newVwapContractAddress

  # Update the Harbinger spot contract.
  @sp.entry_point
  def setSpotContract(self, newSpotContractAddress):
    sp.set_type(newSpotContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.spotContractAddress = newSpotContractAddress

  # Update the pause guardian contract.
  @sp.entry_point
  def setPauseGuardianContract(self, newPauseGuardianContractAddress):
    sp.set_type(newPauseGuardianContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.pauseGuardianContractAddress = newPauseGuardianContractAddress

  # Update the Quipuswap contract.
  @sp.entry_point
  def setQuipuswapContract(self, newQuipuswapContractAddress):
    sp.set_type(newQuipuswapContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.quipuswapContractAddress = newQuipuswapContractAddress

  # Update the governor contract.
  @sp.entry_point
  def setGovernorContract(self, newGovernorContractAddress):
    sp.set_type(newGovernorContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.governorContractAddress = newGovernorContractAddress
  
  # Update the Receiver contract.                             
  @sp.entry_point
  def setReceiverContract(self, newReceiverContractAddress):
    sp.set_type(newReceiverContractAddress, sp.TAddress)

    sp.verify(sp.sender == self.data.governorContractAddress, message = Errors.NOT_GOVERNOR)
    self.data.receiverContractAddress = newReceiverContractAddress
