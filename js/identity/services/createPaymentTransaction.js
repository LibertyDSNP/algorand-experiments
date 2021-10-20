const algosdk = require("algosdk");
const utils = require("../../utils/utils");

const createPaymentTransaction = async (client, sender, receiver, amount) => {
  console.log("sender", sender.addr);

  // provide the default values that are required to submit a transaction, such as the expected fee for the transaction
  const suggestedParams = await client.getTransactionParams().do();

  const unsignedPaymentTxn = algosdk.makePaymentTxnWithSuggestedParams(
    sender.addr,
    receiver,
    amount,
    undefined,
    new Uint8Array(0),
    suggestedParams
  );

  try {
    const signedCreatePaymentTxn = unsignedPaymentTxn.signTxn(sender.sk);

    const { txId: createTxId } = await client
      .sendRawTransaction(signedCreatePaymentTxn)
      .do();

    const completedTx = await utils.verboseWaitForConfirmation(
      client,
      createTxId
    );

    return completedTx;
  } catch (e) {
    console.log("e", e);
  }
};

module.exports = createPaymentTransaction;
