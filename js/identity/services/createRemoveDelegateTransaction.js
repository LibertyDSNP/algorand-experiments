const algosdk = require("algosdk");
const createRawTransaction = require("./createRawTransaction");

const createRemoveDelegateTransaction = async (
  client,
  logicSignatureAccount,
  appID,
  delegateAddress
) => {
  if (!algosdk.isValidAddress(delegateAddress)) {
    throw new Error(`Invalid algo address ${delegateAddress}`);
  }

  const suggestedParams = await client.getTransactionParams().do();
  const appArgs = [
    new Uint8Array(Buffer.from("Remove_delegate")),
    new Uint8Array(Buffer.from(delegateAddress)),
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

module.exports = createRemoveDelegateTransaction;
