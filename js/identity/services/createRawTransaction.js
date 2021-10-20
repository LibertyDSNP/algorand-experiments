const utils = require("../../utils/utils");

const createRawTransaction = async (client, blob) => {
  try {
    const { txId: createTxId } = await client.sendRawTransaction(blob).do();

    const completedTx = await utils.verboseWaitForConfirmation(
      client,
      createTxId
    );

    return completedTx;
  } catch (e) {
    console.log("error:", e);
  }
};

module.exports = createRawTransaction;
