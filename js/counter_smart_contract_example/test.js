const algosdk = require("algosdk");
const utils = require('./utils/utils');
const fs = require("fs");
const path = require("path");

const algodToken =
  "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const algodServer = "http://localhost";
const algodPort = 4001;

const passPhrase =
  "amount oval fabric pave tip stand essay apart galaxy embark invite become bracket maximum innocent horror pelican cage eager sing uniform material cereal ability bottom";

const sender = algosdk.mnemonicToSecretKey(passPhrase);
console.log("account", sender);

let client = new algosdk.Algodv2(algodToken, algodServer, algodPort);


(async () => {
  async function getApprovalProgramBytes(client) {
    // const approvalPath = path.join(__dirname, 'counter_approval_ex.teal');
    const approvalPath = path.join(__dirname, 'storage_approval.teal');
    const program = fs.readFileSync(approvalPath);
    // const program = "#pragma version 2\nint 1";

    // use algod to compile the program
    const compiledProgram = await client.compile(program).do();
    return new Uint8Array(Buffer.from(compiledProgram.result, "base64"));
  }
  
  async function getClearProgramBytes(client) {
    const clearPath = path.join(__dirname, 'counter_clear_ex.teal');
    const program = fs.readFileSync(clearPath);
    // const program = "#pragma version 2\nint 1";

    // use algod to compile the program
    const compiledProgram = await client.compile(program).do();
    return new Uint8Array(Buffer.from(compiledProgram.result, "base64"));
  }

  const from = sender.addr;
  const onComplete = algosdk.OnApplicationComplete.NoOpOC;
  const approvalProgram = await getApprovalProgramBytes(client);
  const clearProgram = await getClearProgramBytes(client);
  const numLocalInts = 0;
  const numLocalByteSlices = 0;
  const numGlobalInts = 0;
  const numGlobalByteSlices = 1;
  const appArgs = [];

  // get suggested params
  const suggestedParams = await client.getTransactionParams().do();

  // create the application creation transaction
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
  // send the transaction
  logBold("Sending application creation transaction.");
  const signedCreateTxn = createTxn.signTxn(sender.sk);
  const { txId: createTxId } = await client
    .sendRawTransaction(signedCreateTxn)
    .do();

  console.log("createTxId", createTxId);

  // wait for confirmation
  const completedTx = await utils.verboseWaitForConfirmation(client, createTxId);

  console.log({ completedTx });
})();


(async () => {
//   const appID = 31704190;
  const appID = 32107695;
  const suggestedParams = await client.getTransactionParams().do();
//   const appArgs = [new Uint8Array(Buffer.from("Add"))];
//   const createTxn = await algosdk.makeApplicationNoOpTxn(sender.addr, suggestedParams, appID, appArgs);
  
//   const signedCreateTxn = createTxn.signTxn(sender.sk);
//   const { txId: createTxId } = await client
//     .sendRawTransaction(signedCreateTxn)
//     .do();

//     const completedTx = await verboseWaitForConfirmation(client, createTxId);
    // console.log("completedTx", completedTx);

    const accountInfo = await client.accountInformation(sender.addr).do();
    const applicationInfo = await client.getApplicationByID(appID).do();
    console.log("accountinfo", accountInfo);
    console.log("applicationInfo", applicationInfo);

    const createdApps = accountInfo['created-apps'];

    const counterApp = createdApps.find((app) => app.id === appID)

    console.log("counterApp", counterApp);

    const globalState = counterApp.params['global-state'];
    console.log("globalState", globalState);

    console.log("state.key", globalState[0].key);

    const buff = Buffer.from(globalState[0].key, 'base64');

    const text = buff.toString('ascii');
    console.log("text", text);
})();