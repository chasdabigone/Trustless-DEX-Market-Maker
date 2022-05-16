# Trustless-DEX-Market-Maker
An decentralized, trustless, oracle-based market maker for Tezos

based on a Quipuswap Proxy contract by Keefer Taylor of Hover Labs

https://github.com/Hover-Labs/kolibri-contracts/

Thank you to Keefer and Ryan from Hover Labs for answering many questions

This contract is fundamentally an exchange wrapper for the Quipuswap DEX. It uses the Harbinger oracle to approximate the current price of kUSD relative to XTZ, and put a price ceiling somewhere above that. If the minout from Quipuswap is lower than required, the swap will fail. Anyone can execute the swap function tokenToTezPayment(), but the parameters can only be changed by the Governor.
