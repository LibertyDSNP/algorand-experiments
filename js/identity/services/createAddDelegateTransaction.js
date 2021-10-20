const algosdk = require("algosdk");
const createRawTransaction = require("./createRawTransaction");

const createAddDelegateTransaction = async (
  client,
  logicSignatureAccount,
  appID,
  delegateAddress,
  expireAt,
  role
) => {
  if ([delegateAddress, expireAt, role].some((param) => param === undefined)) {
    throw new Error(
      `missing params: delegateAddress ${delegateAddress}, expiration ${expireAt}, role ${role}`
    );
  }

  if (!algosdk.isValidAddress(delegateAddress)) {
    throw new Error(`Invalid algo address ${delegateAddress}`);
  }

  const lastRound = (await client.status()).lastRound;
  if (expireAt < lastRound + 1) {
    throw new Error(`Expiration block number is invalid ${expireAt}`);
  }

  const delegateMetadata = algosdk.encodeObj([expireAt, role]);

  const suggestedParams = await client.getTransactionParams().do();
  const appArgs = [
    new Uint8Array(Buffer.from("Add_delegate")),
    new Uint8Array(Buffer.from(delegateAddress)),
    delegateMetadata,
  ];

  const unsignedNoOpTxn = await algosdk.makeApplicationNoOpTxn(
    logicSignatureAccount.address(),
    suggestedParams,
    appID,
    appArgs
  );

  const signedLogicSignature = algosdk.signLogicSigTransactionObject(
    unsignedNoOpTxn,
    logicSignatureAccount
  );

  return createRawTransaction(client, signedLogicSignature.blob);
};

module.exports = createAddDelegateTransaction;
