const algosdk = require("algosdk");
const utils = require("../../utils/utils");

const createOptInAppTransaction = async (
  client,
  logicSignatureAccount,
  appID
) => {
  console.log("logicSignatureAccount", logicSignatureAccount.address());
  const suggestedParams = await client.getTransactionParams().do();

  const createUnsignedOpInTx = algosdk.makeApplicationOptInTxn(
    logicSignatureAccount.address(),
    suggestedParams,
    appID
  );

  try {
    const signedLogicSignature = algosdk.signLogicSigTransaction(
      createUnsignedOpInTx,
      logicSignatureAccount
    );

    console.log("signedLogicSignature", signedLogicSignature);

    const { txId: createTxId } = await client
      .sendRawTransaction(signedLogicSignature.blob)
      .do();

    console.log("createTxId", createTxId);

    const completedTx = await utils.verboseWaitForConfirmation(
      client,
      createTxId
    );
    console.log({ completedTx });
    return completedTx;
  } catch (e) {
    console.log("error:", e);
  }
};

module.exports = createOptInAppTransaction;
