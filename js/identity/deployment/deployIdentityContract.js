const algosdk = require("algosdk");
const utils = require("../../utils/utils");
const { getProgramBytes } = require("./util");

const deployIdentityContract = async (client, account) => {
  const from = account.addr;
  const onComplete = algosdk.OnApplicationComplete.NoOpOC;

  const approvalProgram = await getProgramBytes(
    client,
    "../contracts/teal/identity_approval.teal"
  );
  const clearProgram = await getProgramBytes(
    client,
    "../contracts/teal/identity_clear.teal"
  );
  const numLocalInts = 2;
  const numLocalByteSlices = 2;
  const numGlobalInts = 1;
  const numGlobalByteSlices = 1;
  const appArgs = [];

  const suggestedParams = await client.getTransactionParams().do();

  const createTxn = algosdk.makeApplicationCreateTxn(
    from,
    suggestedParams,
    onComplete,
    approvalProgram,
    clearProgram,
    numLocalInts,
    numLocalByteSlices,
    numGlobalInts,
    numGlobalByteSlices,
    appArgs
  );

  utils.logBold("Sending application creation transaction.");

  try {
    const signedCreateTxn = createTxn.signTxn(account.sk);

    const { txId: createTxId } = await client
      .sendRawTransaction(signedCreateTxn)
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

module.exports = deployIdentityContract;
