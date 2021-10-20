const algosdk = require('algosdk');
const fs = require("fs");
const path = require('path');



(async () => {
    const algodToken = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
    const algodServer = 'http://localhost';
    const algodPort = 4001;

    const passPhrase = "amount oval fabric pave tip stand essay apart galaxy embark invite become bracket maximum innocent horror pelican cage eager sing uniform material cereal ability bottom"

    const account = algosdk.mnemonicToSecretKey(passPhrase);
    console.log("account", account);

    let algodClient = new algosdk.Algodv2(algodToken, algodServer, algodPort);

    const clearTealContractPath = path.join(__dirname, 'counter_clear.teal');
    const clearTealContract = fs.readFileSync(clearTealContractPath);
    const { hash: clearCompileHash, result: clearCompileResult } = await algodClient.compile(clearTealContract).do();

    const approvalTealContractPath = path.join(__dirname, 'counter_approval.teal');
    const approvalTealContract = fs.readFileSync(approvalTealContractPath);
    const { hash: approvalCompileHash, result: approvalCompileResult } = await algodClient.compile(approvalTealContract).do();

    const clearProgramByteCode = new Uint8Array(Buffer.from(clearCompileResult, "base64"));
    const approvalProgramByteCode = new Uint8Array(Buffer.from(approvalCompileResult, "base64"));

    console.log("clearProgramByteCode", clearProgramByteCode);
    console.log('approvalProgramBytecode', approvalProgramByteCode);
    

    const suggestedParams = await algodClient.getTransactionParams().do();

    const from = account.addr;
    const onComplete = algosdk.OnApplicationComplete.NoOpOC;
    const numLocalInts = 0;
    const numLocalByteSlices = 0;
    const numGlobalInts = 1;
    const numGlobalByteSlices = 0;

    const txn = algosdk.makeApplicationCreateTxn(
        from,
        suggestedParams,
        onComplete,
        approvalProgramByteCode,
        clearProgramByteCode,
        numLocalInts,
        numLocalByteSlices,
        numGlobalInts,
        numGlobalByteSlices,
        [],
      );

    console.log("txn", txn);

    const signedTxn = txn.signTxn(account.sk)
    // console.log("signedTxn", signedTxn);

    let txId = txn.txID().toString();

    const { txId: createTxId } = await algodClient.sendRawTransaction(signedTxn).do();

    console.log("txId", createTxId);
})();