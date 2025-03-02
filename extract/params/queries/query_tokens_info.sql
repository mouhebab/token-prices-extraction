SELECT
  TOKEN_ADDRESS,
  SYMBOL
FROM
    ethereum.price.ez_asset_metadata
WHERE
    "BLOCKCHAIN" = 'ethereum'
    AND TOKEN_ADDRESS in {TOKEN_ADDRESSES}

